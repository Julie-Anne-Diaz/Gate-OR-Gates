"""Small HDL -> Yosys JSON -> basic-gate netlist -> Minecraft pipeline.

Minecraft placement requires OR-Tools. Yosys is an external executable; VHDL also
requires its GHDL plugin. Minecraft export reuses gate_templates.py.
"""

import argparse
from collections import defaultdict, deque
from dataclasses import replace
from functools import lru_cache
import json
import heapq
from pathlib import Path
import re
import subprocess
import math
import time
from types import SimpleNamespace


CELL_TYPES = {f"$_{name}_": name for name in
              ("AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR", "BUF")}
CELL_TYPES["$_BUF_"] = "BUFFER"
DIRECTIONS = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}
OPPOSITE = {"east": "west", "west": "east", "north": "south", "south": "north"}


@lru_cache(maxsize=1)
def load_templates():
    """Adapt the shared block catalog without editing it or changing HDL mapping.

    Catalog terminals describe signal direction; the router needs the outward
    connection side. Repairs below restore the previously used basic geometry.
    Combined register templates stay separate from combinational ABC cells.
    """
    import gate_templates as catalog

    Block, Terminal, GateTemplate = catalog.Block, catalog.Terminal, catalog.GateTemplate
    recorded = dict(catalog.GATES) | getattr(catalog, 'STANDALONE_GATES', {})
    basic, standalone, repairs = {}, {}, {}
    for name, original in recorded.items():
        changes = []
        blocks = {}
        for block in original.blocks:
            point, state = (block.x, block.y, block.z), block.state
            if ':' not in state.split('[', 1)[0]:
                state = 'minecraft:' + state
            if state.startswith('minecraft:repeater['):
                state = re.sub(r'([\[,])tick=', r'\1delay=', state)
            if state.startswith('minecraft:wall_lever['):
                state = state.replace('minecraft:wall_lever[', 'minecraft:lever[face=wall,powered=false,', 1)
            if state == 'minecraft:stone':
                state = 'minecraft:stone_bricks'
            if point in blocks and blocks[point].state != state:
                # The supplied SYNCDFF places dust here, then overwrites it
                # with the reset inverter torch. Keep that final recorded state.
                if not (name == 'SYNCDFF' and point == (3, 0, 0)
                        and blocks[point].state == 'minecraft:redstone_wire'
                        and state == 'minecraft:redstone_wall_torch[facing=east]'):
                    raise ValueError(f'{name} template: conflicting blocks at {point}.')
                changes.append(f'{point}: keep final reset inverter torch')
            if state != block.state:
                changes.append(f'{point}: normalize block state')
            blocks[point] = replace(block, state=state)
        inputs, outputs = dict(original.inputs), dict(original.outputs)
        if name == 'BUFFER' and not blocks:
            blocks = {(b.x, b.y, b.z): b for b in (
                Block(0, -1, 0, 'minecraft:stone_bricks'),
                Block(0, 0, 0, 'minecraft:lever[face=floor,facing=west,powered=false]'),
                Block(1, -1, 0, 'minecraft:stone_bricks'),
                Block(1, 0, 0, 'minecraft:repeater[facing=west,delay=1]'),
                Block(2, -1, 0, 'minecraft:redstone_lamp'),
                Block(2, 0, 0, 'minecraft:redstone_wire'))}
            inputs, outputs = {'A': Terminal(0, 0, 0, 'west')}, {'Y': Terminal(2, 0, 0, 'east')}
            changes.append('restore the six-block BUFFER for the empty catalog entry')
        if name == 'NAND' and outputs.get('Y') is not None:
            terminal = outputs['Y']
            if (terminal.x, terminal.y, terminal.z) == (5, 0, 1) and (5, 0, 1) not in blocks:
                if blocks.get((4, 0, 1)) and blocks[(4, 0, 1)].state == 'minecraft:redstone_wire':
                    outputs['Y'] = replace(terminal, x=4)
                    changes.append('Y: use the actual output dust at (4, 0, 1)')
        for pin, terminal in inputs.items():
            if terminal is not None and pin != 'CLK' and terminal.side != 'west':
                inputs[pin] = replace(terminal, side='west')
                changes.append(f'{pin}: normalize outward connection side to west')
        # Add only absent supports; never overwrite a recorded component.
        for (x, y, z), block in list(blocks.items()):
            floor_component = block.state.startswith(('minecraft:redstone_wire', 'minecraft:repeater',
                                                       'minecraft:redstone_torch'))
            floor_component |= block.state.startswith('minecraft:lever[') and 'face=floor' in block.state
            if floor_component and (x, y-1, z) not in blocks:
                material = 'minecraft:white_wool' if name == 'XOR' and (x,y,z) == (7,0,1) else 'minecraft:stone_bricks'
                blocks[(x,y-1,z)] = Block(x, y-1, z, material)
                changes.append(f'{(x,y-1,z)}: add missing component support')
        template = replace(original, blocks=tuple(blocks.values()), inputs=inputs, outputs=outputs)
        (basic if name in CELL_TYPES.values() else standalone)[name] = template
        if changes:
            repairs[name] = changes

    clocked = {}
    if 'ASYNCDFF' in standalone:
        local_dff = standalone['ASYNCDFF']
        clocked['ASYNCDFF_LOCAL'] = replace(local_dff,
            inputs={p: t for p, t in local_dff.inputs.items() if p != 'CLK'},
            notes='Integrated clock; external data/reset inputs and output.')
        clocked['DFF_LOCAL'] = replace(local_dff,
            inputs={'A': local_dff.inputs['A']},
            blocks=tuple(replace(b, state='minecraft:redstone_wire')
                         if (b.x,b.y,b.z) == (0,0,0) else b for b in local_dff.blocks),
            notes='Integrated clock; unused reset is unpowered dust, with no reset lever.')
        # Keep the existing shared-clock adapter and its storage circuit intact.
        receiver_blocks = tuple(b for b in local_dff.blocks
                                if b.z <= 4 or (b.x,b.y,b.z) == (1,0,5)) + (
            Block(0, -1, 7, 'minecraft:stone_bricks'), Block(1, -1, 7, 'minecraft:stone_bricks'),
            Block(1, -1, 6, 'minecraft:stone_bricks'), Block(0, 0, 7, 'minecraft:redstone_wire'),
            Block(1, 0, 7, 'minecraft:redstone_wire'),
            Block(1, 0, 6, 'minecraft:repeater[facing=south,delay=1]'))
        clocked['ASYNCDFF_SHARED'] = replace(local_dff, blocks=receiver_blocks,
            inputs={'A': local_dff.inputs['A'], 'RESET': local_dff.inputs['RESET'],
                    'CLK': Terminal(0, 0, 7, 'west')},
            notes='External shared clock drives the original torch; no local oscillator.')
        clocked['DFF_SHARED'] = replace(clocked['ASYNCDFF_SHARED'],
            inputs={p: t for p,t in clocked['ASYNCDFF_SHARED'].inputs.items() if p != 'RESET'},
            blocks=tuple(replace(b, state='minecraft:redstone_wire')
                         if (b.x,b.y,b.z) == (0,0,0) else b for b in receiver_blocks))
        clocked['CLOCK_SOURCE'] = GateTemplate(
            blocks=tuple(b for b in local_dff.blocks if b.z >= 5) + (
                Block(4, -1, 5, 'minecraft:stone_bricks'), Block(5, -1, 5, 'minecraft:stone_bricks'),
                Block(4, 0, 5, 'minecraft:repeater[facing=west,delay=1]'),
                Block(5, 0, 5, 'minecraft:redstone_wire')),
            inputs={}, outputs={'Y': Terminal(5, 0, 5, 'east')},
            notes='Original oscillator, with an isolated output for one shared clock domain.')
    return SimpleNamespace(GATES=basic, STANDALONE_GATES=standalone, CLOCKED_GATES=clocked,
                           ROUTABLE_GATES=basic | clocked, repairs=repairs)


def validate_template(gate_name: str, template=None,
                      require_routable: bool = True) -> None:
    """Validate recorded geometry and the flat-router terminal contract.

    This checks block support and wiring metadata, not the gate truth table.
    """
    library = load_templates()
    gate = (library.ROUTABLE_GATES | library.STANDALONE_GATES)[gate_name.upper()] if template is None else template
    if not gate.blocks:
        raise ValueError(f"{gate_name}: no blocks recorded.")
    blocks = {(b.x, b.y, b.z): b.state for b in gate.blocks}
    errors = []
    if len(blocks) != len(gate.blocks):
        errors.append("duplicate block coordinates")
    expected = {"A"} if gate_name.upper() in {"NOT", "BUFFER"} else {"A", "B"}
    if gate_name.upper() in {'ASYNCDFF', 'ASYNCDFF_SHARED'}:
        expected = {'A', 'RESET', 'CLK'}
    elif gate_name.upper() == 'ASYNCDFF_LOCAL':
        expected = {'A', 'RESET'}
    elif gate_name.upper() == 'DFF_LOCAL':
        expected = {'A'}
    elif gate_name.upper() == 'DFF_SHARED':
        expected = {'A', 'CLK'}
    elif gate_name.upper() == 'CLOCK_SOURCE':
        expected = set()
    if set(gate.inputs) != expected or set(gate.outputs) != {"Y"}:
        errors.append("incorrect input/output pin names")
    minx, maxx = min(p[0] for p in blocks), max(p[0] for p in blocks)
    def solid(p):
        state = blocks.get(p, "")
        return bool(state) and not any(s in state for s in
            ("redstone_wire", "torch", "lever", "repeater", "air"))
    for pin, terminal in (gate.inputs | gate.outputs).items():
        if terminal is None:
            if require_routable:
                errors.append(f"{pin}: terminal is missing")
            continue
        output = pin == "Y"
        if terminal.side != ("east" if output else "west") or terminal.y != 0:
            errors.append(f"{pin}: expected outward {'east' if output else 'west'} side at y=0")
        if terminal.x != (maxx if output else minx):
            errors.append(f"{pin}: terminal is not on the footprint edge")
        state = blocks.get((terminal.x, terminal.y, terminal.z), "")
        allowed = ("minecraft:redstone_wire",) if output else ("minecraft:redstone_wire", "minecraft:lever[")
        if not state.startswith(allowed):
            errors.append(f"{pin}: terminal must identify actual {'dust' if output else 'dust or lever'}")
    for (x, y, z), state in blocks.items():
        if (state.startswith(("minecraft:redstone_wire", "minecraft:repeater", "minecraft:redstone_torch"))
                or state.startswith('minecraft:lever') and 'face=floor' in state):
            if not solid((x, y-1, z)):
                errors.append(f"unsupported component at {(x, y, z)}")
        if state.startswith("minecraft:redstone_wall_torch") or (state.startswith('minecraft:lever') and 'face=wall' in state):
            offsets = {"east": (-1, 0), "west": (1, 0), "south": (0, -1), "north": (0, 1)}
            direction = next((d for d in offsets if f"facing={d}" in state), None)
            if direction is None or not solid((x+offsets[direction][0], y, z+offsets[direction][1])):
                errors.append(f"wall component has no attachment at {(x, y, z)}")
        if state.startswith('minecraft:oak_hanging_sign') and not solid((x,y+1,z)):
            errors.append(f"hanging sign has no ceiling at {(x,y,z)}")
        elif state.startswith('minecraft:oak_sign') and not solid((x,y-1,z)):
            errors.append(f"sign has no support at {(x,y,z)}")
    if errors:
        raise ValueError(f"{gate_name} template: " + "; ".join(errors))



class RoutingError(ValueError):
    """A placement can be retried without hiding invalid netlists/templates."""


class NetRoutingError(RoutingError):
    """A failed branch and the completed wiring that can be ripped up."""
    def __init__(self, message, bit, sink, routed_bits):
        super().__init__(message)
        self.bit = bit
        self.sink = tuple(sink)
        self.routed_bits = list(dict.fromkeys(routed_bits))


def repeater_state(output_direction):
    """Java's facing property points toward the INPUT, opposite signal travel."""
    return f"minecraft:repeater[facing={OPPOSITE[output_direction]},delay=1]"


def yosys_quote(path):
    return json.dumps(str(Path(path).resolve()).replace("\\", "/"))


def synthesize(sources, top, output, yosys="yosys", plugin="ghdl", standard="08",
               profile="default", legalize_dffs=False):
    """Keep raw Yosys JSON, a reproducible script, and the complete tool log."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", top):
        raise ValueError("Use a plain HDL identifier for --top.")
    if profile not in {"default", "compact"}:
        raise ValueError("Synthesis profile must be 'default' or 'compact'.")
    paths = [Path(p).resolve() for p in sources]
    if not paths or any(not p.is_file() for p in paths):
        raise ValueError("Supply existing HDL source files in dependency order.")
    suffixes = {p.suffix.lower() for p in paths}
    vhdl = suffixes <= {".vhd", ".vhdl"}
    if not vhdl and not suffixes <= {".v", ".sv"}:
        raise ValueError("Use either VHDL or Verilog/SystemVerilog sources, not a mixture.")
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    files = " ".join(yosys_quote(p) for p in paths)
    frontend = (f"ghdl --std={standard} {files} -e {top}" if vhdl
                else f"read_verilog -sv {files}")
    # Avoid FPGA LUT mapping: Minecraft needs individual Boolean gates.
    mapping = "abc -g AND,OR,XOR,XNOR,NAND,NOR"
    # Enable/hold cells become ordinary DFFs plus feedback multiplexers before
    # ABC maps the combinational logic to the supported gate library.
    steps = [f"synth -top {top} -flatten -noabc", "dffunmap -ce-only", "techmap", mapping]
    if profile == "compact":
        # Convert decoded case selectors before lowering to individual gates.
        # The -run end label is exclusive: stop before the fine/techmap stage.
        # ABC still emits only the Boolean gates supported by our templates.
        steps = [f"synth -top {top} -flatten -noabc -run begin:fine",
                 "pmux2shiftx", f"synth -top {top} -noabc -run fine:", "dffunmap -ce-only", "techmap",
                 mapping + " -script +strash;dc2;&get,-n;&dch,-f;&nf,-E,100;&put"]
    if legalize_dffs:
        # Preserve preset/polarity semantics with D/Q/control inverters around
        # the rising-edge, reset-to-zero storage supported by the block catalog.
        steps.insert(-1, "dfflegalize -cell $_DFF_PP0_ x -cell $_DFF_P_ x")
    script = "\n".join([frontend, f"hierarchy -check -top {top}", *steps, "clean",
                        "check -assert", f"write_json {yosys_quote(output)}", ""])
    script_path = output.with_suffix(".ys")
    log_path = output.with_suffix(".log")
    script_path.write_text(script, encoding="utf-8")
    command = [yosys] + (["-m", plugin] if vhdl and plugin else [])
    try:
        result = subprocess.run(command + ["-s", str(script_path)],
                                capture_output=True, text=True, errors="replace")
    except FileNotFoundError as exc:
        raise ValueError("Yosys was not found. Install Yosys and use --yosys PATH; "
                         "VHDL also needs the GHDL plugin. Script: " + str(script_path)) from exc
    log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise ValueError(f"Yosys failed (exit {result.returncode}). See {log_path}")
    if not output.is_file():
        raise ValueError(f"Yosys did not produce {output}. See {log_path}")


def basic_netlist(raw, top):
    """Flatten ports and preserve register boundaries, clock/reset and bit IDs."""
    if top not in raw.get("modules", {}):
        raise ValueError(f"Top module {top!r} is absent from the JSON.")
    module = raw["modules"][top]
    initial_bits = {}
    for wire in module.get('netnames', {}).values():
        initial = wire.get('attributes', {}).get('init')
        if isinstance(initial, str):
            for bit, value in zip(wire['bits'], reversed(initial)):
                initial_bits[bit] = int(value) if value in '01' else value
    gates, registers, ports = [], [], []
    for name, cell in sorted(module.get("cells", {}).items()):
        if cell["type"] == "$scopeinfo":
            continue  # Yosys hierarchy metadata, not a logic cell.
        kind = CELL_TYPES.get(cell["type"])
        # Registers are state boundaries, not combinational gates. Retain their
        # clock/reset semantics separately so feedback through Q is legal.
        flipflop = re.fullmatch(r"\$_DFF_([NP])(?:([NP])([01]))?_", cell["type"])
        if flipflop:
            expected = {"D", "C", "Q"} | ({"R"} if flipflop[2] else set())
            connections = cell['connections']
            if set(connections) != expected or any(len(v) != 1 for v in connections.values()):
                raise ValueError(f"Unexpected pins on {name}: {connections}")
            rename = {'D': 'A', 'C': 'CLK', 'Q': 'Y', 'R': 'RESET'}
            register = {'name': name, 'gate': 'ASYNCDFF' if flipflop[2] else 'DFF',
                        'cell_type': cell['type'],
                        'pins': {rename[k]: v[0] for k,v in connections.items()},
                        'clock_edge': 'rising' if flipflop[1] == 'P' else 'falling'}
            if flipflop[2]:
                register['reset'] = {'kind': 'asynchronous',
                                     'active_level': int(flipflop[2] == 'P'),
                                     'value': int(flipflop[3])}
            if register['pins']['Y'] in initial_bits:
                register['initial_value'] = initial_bits[register['pins']['Y']]
            registers.append(register)
            continue
        if kind is None:
            raise ValueError(f"Unsupported cell {name}: {cell['type']}. "
                             "Supported JSON cells are basic gates and plain/asynchronous-reset DFFs.")
        expected = {"A", "Y"} if kind in {"NOT", "BUFFER"} else {"A", "B", "Y"}
        connections = cell["connections"]
        if set(connections) != expected or any(len(v) != 1 for v in connections.values()):
            raise ValueError(f"Unexpected pins on {name}: {connections}")
        gates.append({"name": name, "gate": kind,
                      "pins": {k: v[0] for k, v in connections.items()}})
    for name, port in module.get("ports", {}).items():
        if port["direction"] not in {"input", "output"}:
            raise ValueError(f"Bidirectional port {name} is not supported.")
        bits = port["bits"]
        for i, bit in enumerate(bits):
            index = port.get("offset", 0) + (len(bits) - 1 - i if port.get("upto") else i)
            label = f"{name}[{index}]" if len(bits) > 1 else name
            ports.append({"name": label, "direction": port["direction"], "bit": bit})
    # All supported binary cells are commutative. Put the most widely shared
    # input on pin A so control trunks approach the same side of each lane.
    uses = defaultdict(int)
    for gate in gates:
        for pin, bit in gate['pins'].items():
            if pin != 'Y':
                uses[bit] += 1
    for gate in gates:
        pins = gate['pins']
        if 'B' in pins and uses[pins['B']] > uses[pins['A']]:
            pins['A'], pins['B'] = pins['B'], pins['A']
    drivers, sinks = {}, defaultdict(list)

    def driver(bit, endpoint):
        if not isinstance(bit, int) or bit in drivers:
            raise ValueError(f"Invalid or multiple drivers for bit {bit}.")
        drivers[bit] = endpoint

    for port in ports:
        endpoint = ["port", port["name"]]
        if port["direction"] == "input":
            driver(port["bit"], endpoint)
        else:
            sinks[port["bit"]].append(endpoint)
    for gate in [*gates, *registers]:
        for pin, bit in gate["pins"].items():
            endpoint = [gate["name"], pin]
            if pin == "Y":
                driver(bit, endpoint)
            else:
                sinks[bit].append(endpoint)
    nets = []
    for bit, targets in sinks.items():
        if isinstance(bit, int) and bit not in drivers:
            raise ValueError(f"Undriven bit {bit}.")
        if isinstance(bit, str) and bit not in {"0", "1"}:
            raise ValueError(f"Undefined/high-impedance bit {bit!r} is unsupported.")
        nets.append({"bit": bit, "source": drivers.get(bit, ["constant", bit]),
                     "sinks": targets})
    # Register Q is a source for the current cycle, irrespective of its next-D
    # logic. This cuts sequential feedback without accepting combinational loops.
    ordered, done = [], {r['name'] for r in registers}
    pending = list(gates)
    while pending:
        ready = [g for g in pending if all(
            not isinstance(b, int) or drivers[b][0] == "port" or drivers[b][0] in done
            for p, b in g["pins"].items() if p != "Y")]
        if not ready:
            raise ValueError("Combinational feedback is not supported.")
        for gate in ready:
            pending.remove(gate)
            done.add(gate["name"])
            ordered.append(gate)
    result = {"top": top, "ports": ports, "gates": ordered, "nets": nets}
    if registers:
        result['registers'] = registers
    return result


def neighbors(point):
    x, z = point
    return [(x + dx, z + dz) for dx, dz in DIRECTIONS]


def wire_neighborhood(point):
    """Conservative contact envelope for dust, repeaters and stair supports."""
    x, y, z = point
    return ((px, py, pz) for px, pz in [(x,z), *neighbors((x,z))]
            for py in range(y-1, y+2))


def wire_extension_clear(segment, earlier, attachment):
    """New wire may touch only its predecessor, never an older parallel leg.

    In particular, a bridge hairpin must leave an air gap: a unique sequence
    of block coordinates can still reconnect around a repeater and latch on.
    """
    added, previous = set(), attachment
    for point in segment:
        if point in earlier or point in added:
            return False
        if any(q != previous and (q in earlier or q in added) for q in wire_neighborhood(point)):
            return False
        added.add(point)
        previous = point
    return True


def validate_wire_branch(path, tree=()):
    """Check only generated wiring; intentional gate/clock feedback is separate."""
    if not path or not wire_extension_clear(path[1:], set(tree) | {path[0]}, path[0]):
        raise RoutingError('Wire route reconnects to an earlier section or branch; repeater feedback risk.')


def route_wire(start, end, blocked, bounds):
    """Bounded breadth-first search on one horizontal block layer."""
    queue, previous = deque([start]), {start: None}
    while queue:
        point = queue.popleft()
        if point == end:
            path = []
            while point is not None:
                path.append(point)
                point = previous[point]
            return path[::-1]
        for nxt in neighbors(point):
            x, z = nxt
            if not (bounds[0] <= x <= bounds[1] and bounds[2] <= z <= bounds[3]):
                continue
            if nxt in previous or nxt in blocked:
                continue
            previous[nxt] = point
            queue.append(nxt)
    raise RoutingError(f"No planar wire route from {start} to {end}.")


def bridge_path(start, direction, span=8, height=3):
    """One-block steps up to the requested height, a deck, then steps down.

    Dust at Y=3 and its support at Y=2 leave Y=1 free over a lower Y=0
    wire. Use solid stone bricks (not stair blocks) beneath every dust block.
    """
    x, z = start
    dx, dz = direction
    return [(x + i*dx, min(i, height, span-i), z + i*dz) for i in range(span+1)]


def bridge_clear(path, blocks, headroom, signals, obstacles, bounds, roofs=None):
    """Check the complete bridge, including ramps, supports and electrical gap."""
    for x, y, z in path:
        if not (bounds[0] <= x <= bounds[1] and bounds[2] <= z <= bounds[3]):
            return False
        if (x, z) in obstacles:
            nearby = {(x,z), *neighbors((x,z))}
            roof = roofs.get((x,z), 1) if roofs is not None else max((py for px,py,pz in blocks if (px,pz) in nearby), default=1)
            if y < max(4, roof+3):
                return False
        if (x, y, z) in blocks or (x, y-1, z) in headroom or (x, y, z) in headroom:
            return False
        if (x, y-1, z) in blocks or (x, y+1, z) in blocks:
            return False
        for px, pz in [(x, z), *neighbors((x, z))]:
            if any((px, py, pz) in signals for py in range(y-1, y+2)):
                return False
    return True


def route_with_bridges(start, end, blocked, obstacles, blocks, headroom, signals, bounds):
    """A* on ground positions with validated whole bridges as extra edges.

    Prefer ordinary dust. Higher bridges can cross gate columns when their
    supports and components clear the entire nearby roof by three blocks.
    """
    def distance(p):
        return abs(p[0]-end[0]) + abs(p[1]-end[1])

    roofs = {}
    for (x,y,z) in blocks:
        for p in [(x,z), *neighbors((x,z))]:
            roofs[p] = max(roofs.get(p, -1), y)
    costs, previous = {start: 0}, {start: None}
    queue = [(distance(start), 0, start)]
    checked = 0
    while queue:
        _, cost, point = heapq.heappop(queue)
        if cost != costs[point]:
            continue
        if point == end:
            edges = []
            while previous[point] is not None:
                parent, segment = previous[point]
                edges.append(segment)
                point = parent
            path = [(start[0], 0, start[1])]
            for segment in reversed(edges):
                path.extend(segment[1:])
            return path
        checked += 1
        if checked > 40000:
            break
        # A whole bridge edge may otherwise jump over an earlier part of this
        # same path and later loop back into its ramp/supports.
        ancestor_columns = {start}
        ancestor_points = {(start[0], 0, start[1])}
        ancestor = point
        while previous[ancestor] is not None:
            parent, segment = previous[ancestor]
            ancestor_columns.update((x, z) for x, _, z in segment)
            ancestor_points.update(segment)
            ancestor = parent
        choices = []
        for nxt in neighbors(point):
            if (bounds[0] <= nxt[0] <= bounds[1] and bounds[2] <= nxt[1] <= bounds[3]
                    and nxt not in blocked):
                choices.append((nxt, [(point[0], 0, point[1]), (nxt[0], 0, nxt[1])], 1))
        for direction in DIRECTIONS:
            for span,height in ((8,3), (10,3), (12,3), (16,5), (20,5), (24,5)):
                segment = bridge_path(point, direction, span, height)
                landing = (segment[-1][0], segment[-1][2])
                if landing in blocked:
                    continue
                # There must be something to cross, not just a gratuitous hill.
                if not any((x, z) in blocked for x, _, z in segment[1:-1]):
                    continue
                if bridge_clear(segment, blocks, headroom, signals, obstacles, bounds, roofs):
                    choices.append((landing, segment, span+12))
        for nxt, segment, step_cost in choices:
            if any((x, z) in ancestor_columns for x, _, z in segment[1:]):
                continue
            if not wire_extension_clear(segment[1:], ancestor_points, segment[0]):
                continue
            new_cost = cost + step_cost
            if new_cost < costs.get(nxt, float('inf')):
                costs[nxt] = new_cost
                previous[nxt] = (point, segment)
                heapq.heappush(queue, (new_cost+distance(nxt), new_cost, nxt))
    raise RoutingError(f"No route with bridge clearance from {start} to {end}.")


def repeaters(path):
    """Restore power at most every 12 steps, only on straight sections."""
    result, last = {}, 0
    while len(path) - 1 - last > 12:
        candidates = [i for i in range(last + 1, min(last + 12, len(path) - 2) + 1)
                      if (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]) ==
                         (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])]
        if not candidates:
            raise ValueError("Wire turns too often to insert a repeater safely.")
        last = candidates[-1]
        direction = (path[last+1][0] - path[last][0], path[last+1][1] - path[last][1])
        result[path[last]] = DIRECTIONS[direction]
    return result


def route_in_layers(candidates, end, tree, obstacles, blocks, headroom, signals,
                    bounds, max_states=120000, reverse=True, keepouts=frozenset(), tail=(), preferred_y=None,
                    keepout_height=None):
    """Weighted A* between routing layers, with repeater-ready stair macros.

    Search backward from a constrained input to powered dust. Stair macros
    include flat landing sections, and every result is checked for restoration.
    """
    target = (end[0], 0, end[1])
    goals = set(candidates) if reverse else {target}
    if not goals:
        raise RoutingError('No powered attachment available.')
    def make_index(points):
        if not points:
            return None
        axis = max(range(3), key=lambda i: max(p[i] for p in points)-min(p[i] for p in points))
        points.sort(key=lambda p: p[axis])
        middle = len(points)//2
        return (points[middle], axis, make_index(points[:middle]), make_index(points[middle+1:]))
    index = make_index(list(goals)) if reverse else None
    def nearest(p, node, best=float('inf')):
        if node is None:
            return best
        q, axis, left, right = node
        best = min(best, abs(p[0]-q[0])+abs(p[1]-q[1])+abs(p[2]-q[2]))
        delta = p[axis]-q[axis]
        near, far = (left,right) if delta < 0 else (right,left)
        best = nearest(p, near, best)
        return nearest(p, far, best) if abs(delta) < best else best
    own = set(tree)
    tail_columns = {(x,z) for x,_,z in tail}
    forbidden = set()
    for x, y, z in signals-own:
        for px, pz in [(x,z), *neighbors((x,z))]:
            forbidden.update((px, py, pz) for py in range(y-1, y+2))
    roofs = {}
    for x, y, z in blocks:
        for p in [(x,z), *neighbors((x,z))]:
            roofs[p] = max(roofs.get(p, -1), y)
    max_y = max(12, (preferred_y or 0)+3, max((p[1] for p in signals), default=0)+4)
    max_y = min(max_y, 36)
    # A branch may share its attachment, but must not touch a repeater's side.
    repeaters_in_tree = {p for p in own if 'repeater' in blocks.get(p, '')}
    own_neighbors = defaultdict(set)
    for q in own:
        x,y,z = q
        for px,pz in [(x,z), *neighbors((x,z))]:
            for py in range(y-1,y+2):
                own_neighbors[(px,py,pz)].add(q)
    legal_cache = {}
    def legal(p):
        if p in legal_cache:
            return legal_cache[p]
        result = clear(p)
        legal_cache[p] = result
        return result
    def clear(p):
        x,y,z = p
        if not (bounds[0] <= x <= bounds[1] and bounds[2] <= z <= bounds[3] and 0 <= y <= max_y):
            return False
        if reverse and p in goals:
            return True
        if (x,z) in tail_columns:
            return False
        # Reserve room for two entry/exit stair macros (up to y=6), plus
        # electrical clearance. Large feedback builds may cross above y=8;
        # actual occupied blocks/signals still undergo every check below.
        if (x,z) in keepouts and (keepout_height is None or y < keepout_height):
            return False
        if p in forbidden or p in own:
            return False
        if (x,z) in obstacles and y < max(4, roofs.get((x,z), 1)+3):
            return False
        if p in blocks and p != target:
            return False
        if (x,y-1,z) in blocks and p != target:
            return False
        if (x,y+1,z) in blocks or p in headroom or (x,y-1,z) in headroom:
            return False
        for px,pz in [(x,z), *neighbors((x,z))]:
            if any((px,py,pz) in repeaters_in_tree for py in range(y-1,y+2)):
                return False
        return True
    estimates = {}
    def estimate(p):
        if reverse:
            if p not in estimates:
                estimates[p] = nearest(p, index)
            return estimates[p]
        return abs(p[0]-target[0])+abs(p[2]-target[2])+p[1]
    queue, costs, previous = [], {}, {}
    serial = 0
    for p in ([target] if reverse else candidates):
        state = (p, None, 0 if reverse else tree[p])
        costs[state] = 0
        previous[state] = (None, [p])
        heapq.heappush(queue, (2*estimate(p), 0, serial, state))
        serial += 1
    checked = 0
    rejected_goals = {'geometry': 0, 'power': 0, 'contact': 0}
    while queue and checked < max_states:
        _, cost, _, state = heapq.heappop(queue)
        if cost != costs[state]:
            continue
        point, incoming, distance = state
        if point in goals:
            edges = []
            node = previous[state]
            while node is not None:
                node, segment = node
                edges.append(segment)
            path = []
            for segment in reversed(edges):
                path.extend(segment)
            if reverse:
                path.reverse()
            path.extend(tail)
            components = set(path)
            supports = {(x,y-1,z) for x,y,z in path}
            air = {(x,y+1,z) for x,y,z in path}
            if len(components) != len(path) or (supports | components) & air or supports & components:
                rejected_goals['geometry'] += 1
                continue
            try:
                validate_wire_branch(path, own)
            except RoutingError:
                rejected_goals['contact'] += 1
                continue
            try:
                boosts = repeaters_3d(path, tree[path[0]])
            except RoutingError:
                rejected_goals['power'] += 1
                continue
            return path, boosts, tree[path[0]]
        checked += 1
        # Keep an immutable path chain per candidate. A later improvement of
        # a search state must not change an already-built child's geometry.
        ancestor_columns, ancestor_points = set(), set()
        node = previous[state]
        while node is not None:
            node, segment = node
            ancestor_columns.update((x,z) for x,_,z in segment)
            ancestor_points.update(segment)
        for direction in DIRECTIONS:
            dx,dz = direction
            if incoming is not None and (dx, dz) == (-incoming[0], -incoming[2]):
                continue
            profiles = [(0, [0]), (3, [0,0,1,2,3,3,3]), (-3, [0,0,-1,-2,-3,-3,-3])]
            if point[1] == 0:
                # A narrow crossing can use the existing eight-step bridge
                # shape instead of turning back around two long stair macros.
                profiles.append((3, [1,2,3,3,3,2,1,0]))
            for dy, heights in profiles:
                segment = [(point[0]+i*dx, point[1]+height, point[2]+i*dz)
                           for i,height in enumerate(heights, 1)]
                nxt = segment[-1]
                if any((x,z) in ancestor_columns for x,_,z in segment):
                    continue
                if not all(legal(p) for p in segment):
                    continue
                if not wire_extension_clear(segment, ancestor_points, point):
                    continue
                if reverse:
                    if nxt in goals:
                        # Only the final predecessor may meet the selected
                        # attachment. Touching other candidate dust is a loop.
                        if own_neighbors.get(point) and (len(segment) != 1 or own_neighbors[point] != {nxt}):
                            continue
                        if any(own_neighbors.get(p) and
                               (i != len(segment)-2 or own_neighbors[p] != {nxt})
                               for i,p in enumerate(segment[:-1])):
                            continue
                    else:
                        # On reaching dust beside the tree, connect on the
                        # next step instead of running alongside the trunk.
                        touching = own_neighbors.get(nxt, set())
                        if own_neighbors.get(point) or any(own_neighbors.get(p) for p in segment[:-1]):
                            continue
                        if touching and (len(touching) != 1 or not touching <= goals):
                            continue
                elif any(own_neighbors.get(p) and
                         (i != 0 or point not in own or own_neighbors[p] != {point})
                         for i,p in enumerate(segment)):
                    continue
                if any(p in own for p in segment[:-1]):
                    continue
                new_state = (nxt, (dx, 0, dz), 0)
                layer_cost = (0.05 if nxt[1] else 0) if preferred_y is None else (
                    0 if nxt[1] == preferred_y else 2 if nxt[1] == 0 else 0.5)
                new_cost = cost + len(segment) + (3 if dy else 0) + layer_cost*len(segment)
                if new_cost >= costs.get(new_state, float('inf')):
                    continue
                costs[new_state] = new_cost
                previous[new_state] = (previous[state], segment)
                heapq.heappush(queue, (new_cost+2*estimate(nxt), new_cost, serial, new_state))
                serial += 1
    raise RoutingError(f"Layered routing exhausted {checked} states to {end}; rejected goals {rejected_goals}.")


def repeaters_3d(path, initial_distance=0, junctions=frozenset()):
    """Repeaters must have flat input/output dust, never sit on a ramp."""
    result, last = {}, -initial_distance
    while len(path)-1-last > 12:
        candidates = [i for i in range(max(1, last+1), min(last+12, len(path)-2)+1)
                      if path[i] not in junctions and path[i-1][1] == path[i][1] == path[i+1][1]
                      and (path[i][0]-path[i-1][0], path[i][2]-path[i-1][2]) ==
                          (path[i+1][0]-path[i][0], path[i+1][2]-path[i][2])]
        if not candidates:
            raise RoutingError("Route has no flat straight section for signal restoration.")
        last = candidates[-1]
        result[path[last]] = DIRECTIONS[(path[last+1][0]-path[last][0],
                                         path[last+1][2]-path[last][2])]
    return result


def block_commands(blocks, origin=None, offset=(0, 0, 0)):
    """Emit supports before components, at the player or an absolute origin."""
    ox, oy, oz = origin if origin is not None else offset
    commands = []
    for (x, y, z), state in sorted(blocks.items(), key=lambda item: item[0][1]):
        coords = (x+ox, y+oy, z+oz)
        if origin is None:
            location = " ".join(f"~{v}" if v else "~" for v in coords)
            commands.append(f"execute at @s align xyz run setblock {location} {state} replace")
        else:
            commands.append(f"setblock {coords[0]} {coords[1]} {coords[2]} {state} replace")
    return commands


def standalone_template(name, origin=None, offset=(0, 0, 0)):
    """Export the supplied local-clock circuit with its manual controls intact."""
    template = load_templates().STANDALONE_GATES[name]
    validate_template(name, template, require_routable=False)
    supports, components = {}, {}
    for block in template.blocks:
        target = components if any(part in block.state for part in
                  ('redstone_wire', 'repeater', 'torch', 'lever', 'sign')) else supports
        target[(block.x, block.y, block.z)] = block.state
    # A hanging sign needs its ceiling first, even though the ceiling is higher.
    commands = block_commands(supports, origin, offset) + block_commands(components, origin, offset)
    terminals = {pin: ([t.x,t.y,t.z] if t else None)
                 for pin,t in (template.inputs | template.outputs).items()}
    return commands, {'template': name, 'coordinate_mode': 'absolute' if origin else 'player_relative',
                      'origin': origin, 'offset': offset, 'terminals': terminals,
                      'local_clock_trigger_xyz': [5,0,7], 'output_lamp_xyz': [9,-1,1],
                      'automatic_wiring_ready': False, 'notes': template.notes}


def bridge_demo(origin=None, offset=(0, 0, 0)):
    """Two independent lever-to-lamp lines, forced to cross for in-game QA."""
    lower = [(8, 0, z) for z in range(2, 17)]
    blocks, signals = {}, set(lower)
    headroom = {(x, y+1, z) for x, y, z in lower}
    routes = []
    def add_line(name, path):
        boosts = repeaters_3d(path)
        for p in path:
            x, y, z = p
            blocks[(x, y-1, z)] = "minecraft:stone_bricks"
            blocks[p] = repeater_state(boosts[p]) if p in boosts else "minecraft:redstone_wire"
        x, y, z = path[-1]
        blocks[(x, y-1, z)] = "minecraft:redstone_lamp"
        blocks[path[0]] = "minecraft:lever[face=floor,facing=east,powered=false]"
        routes.append({"name": name, "path_xyz": path, "lever_xyz": path[0],
                       "lamp_xyz": [x, y-1, z]})
    add_line("lower", lower)
    blocked = {(px, pz) for x, _, z in lower for px, pz in [(x, z), *neighbors((x, z))]}
    upper = route_with_bridges((2, 9), (14, 9), blocked, set(), blocks,
                               headroom, signals, (2, 14, 2, 16))
    add_line("upper", upper)
    return block_commands(blocks, origin, offset), {
        "coordinate_mode": "absolute" if origin is not None else "player_relative",
        "origin": origin, "offset": offset if origin is None else None,
        "routes": routes, "expected": "Each lever controls only its own lamp; test all four input combinations."}


def placement_parents(gate, producers, cuts):
    """Cut selected storage inputs for placement only; all nets still route."""
    return [producers[b] for p, b in gate['pins'].items()
            if p != 'Y' and b in producers and (gate['name'], p) not in cuts]


def gate_positions(netlist, templates, spacing):
    """Pack independent gates into lanes; place dependent stages to the east."""
    for kind in {g["gate"] for g in netlist["gates"]}:
        validate_template(kind, templates[kind])
    producers = {g["pins"]["Y"]: g["name"] for g in netlist["gates"]}
    cuts = {tuple(s) for s in netlist.get('placement_cuts', [])}
    depths, layers, footprints = {}, defaultdict(list), {}
    for gate in netlist["gates"]:
        blocks = templates[gate["gate"]].blocks
        if not blocks:
            raise ValueError(f"{gate['gate']} has no Minecraft blocks in gate_templates.py yet. Gate JSON is still usable.")
        template = templates[gate["gate"]]
        if any(t is None for t in [*template.inputs.values(), *template.outputs.values()]):
            raise ValueError(f"Fill in terminal coordinates for {gate['gate']} first.")
        name = gate["name"]
        footprints[name] = (min(b.x for b in blocks), max(b.x for b in blocks),
                            min(b.z for b in blocks), max(b.z for b in blocks))
        parents = placement_parents(gate, producers, cuts)
        depths[name] = max((depths[p] + 1 for p in parents), default=0)
        layers[depths[name]].append(name)
    # Visit each output's dependency tree together, so unrelated bus bits do
    # not interleave just because ABC assigned cells arbitrary names.
    by_name = {g["name"]: g for g in netlist["gates"]}
    ordered, visited = [], set()
    def visit(name):
        if name in visited:
            return
        visited.add(name)
        for pin, bit in by_name[name]["pins"].items():
            if pin != "Y" and bit in producers and (name, pin) not in cuts:
                visit(producers[bit])
        ordered.append(name)
    for port in netlist["ports"]:
        if port["direction"] == "output" and port["bit"] in producers:
            visit(producers[port["bit"]])
    for name in by_name:
        visit(name)
    rank = {name: i for i, name in enumerate(ordered)}
    positions, x = {}, 6
    for depth in sorted(layers):
        z, width = 2, 0
        for name in sorted(layers[depth], key=rank.get):
            minx, maxx, minz, maxz = footprints[name]
            parent_centers = [positions[producers[bit]][1] +
                              templates[by_name[producers[bit]]["gate"]].outputs["Y"].z
                              for pin, bit in by_name[name]["pins"].items()
                              if pin != "Y" and bit in producers and (name, pin) not in cuts]
            if parent_centers:
                z = max(z, round(sum(parent_centers)/len(parent_centers) - (maxz-minz)/2))
            positions[name] = (x - minx, z - minz)
            z += maxz - minz + 1 + spacing
            width = max(width, maxx - minx + 1)
        # Include terminal repeaters and short external control wires.
        x += width + 8 + spacing
    return positions


def ortools_minecraft(netlist, origin=None, spacing=2, offset=(0, 0, 0), solver_seconds=10, solver_workers=1):
    """CP-SAT placement with fixed orientations and dependency-layer ordering.

    Optimizes a Manhattan-distance estimate, not complete Minecraft physics.
    Every proposed placement must pass the redstone wire router.
    """
    if netlist.get('registers'):
        raise ValueError("The supplied standalone DFF has CLK=None for external wiring. "
                         "Use --clock-source integrated for one oscillator per HDL clock domain, "
                         "or --template-test ASYNCDFF to export the manual template.")
    try:
        import ortools
        from ortools.sat.python import cp_model
    except ImportError as exc:
        raise ValueError("--placer ortools needs OR-Tools in this Python environment. "
                         "Run: python -m pip install -r requirements.txt") from exc
    GATES = load_templates().ROUTABLE_GATES

    if spacing < 2:
        raise ValueError("--spacing must be at least 2.")
    if not math.isfinite(solver_seconds) or solver_seconds <= 0:
        raise ValueError("--solver-seconds must be a finite positive number.")
    if type(solver_workers) is not int or solver_workers < 1:
        raise ValueError("--solver-workers must be a positive integer.")
    requested_spacing = spacing
    # Shared-control taps and nearby data inputs need a four-block lane gap.
    # Keep compact two-block lanes for circuits without fanout.
    if any(len(n['sinks']) > 1 for n in netlist['nets']):
        spacing = max(spacing, 4)
    seed = gate_positions(netlist, GATES, spacing)
    if not seed:
        commands, layout = build_layout(netlist, {}, origin, spacing, offset)
        bounds = layout['local_bounds']
        layout["placement"] = {"method": "ortools_cp_sat", "solver_status": "NOT_NEEDED",
                               "wire_steps": sum(len(r['path_xyz'])-1 for r in layout['routes']),
                               "bridges": sum(r['bridge_count'] for r in layout['routes']),
                               "horizontal_area": ((bounds['x'][1]-bounds['x'][0]+1)*
                                                   (bounds['z'][1]-bounds['z'][0]+1)) if bounds else 0}
        return commands, layout
    # Keep the existing tree/layer ordering as a routing-friendly constraint.
    # CP-SAT chooses coordinates, layer distances and vertical gate alignment.
    names = list(seed)
    by_name = {g['name']: g for g in netlist['gates']}
    producers = {g['pins']['Y']: g['name'] for g in netlist['gates']}
    cuts = {tuple(s) for s in netlist.get('placement_cuts', [])}
    layer_of = {}
    for gate in netlist['gates']:
        parents = placement_parents(gate, producers, cuts)
        layer_of[gate['name']] = max((layer_of[p]+1 for p in parents), default=0)
    layer_keys = sorted(set(layer_of.values()))
    bus_layers = {layer_of[s[0]] for n in netlist['nets'] if len(n['sinks']) > 1
                  for s in n['sinks'] if s[0] != 'port'}
    sequential_routing = bool(cuts) or any(
        c.get('external_clock_routed') for c in netlist.get('clock_bindings', []))
    if sequential_routing:
        # An isolated clock has a nonzero footprint origin. Translate all seed
        # lanes together so every coordinate hint is inside its variable domain.
        shift = max(0, 2-min(z for _, z in seed.values()))
        seed = {name: (x, z+shift) for name, (x, z) in seed.items()}
    footprints = {}
    for name in names:
        blocks = GATES[by_name[name]['gate']].blocks
        footprints[name] = (min(b.x for b in blocks), max(b.x for b in blocks),
                            min(b.z for b in blocks), max(b.z for b in blocks))
    bound = max(256, max(max(p) for p in seed.values()) + 64)
    attempts, solve_time = [], 0.0
    started = time.monotonic()
    for attempt, extra in enumerate((0, 4, 8, 16, 24)):
        remaining = solver_seconds - solve_time
        if remaining <= 0:
            break
        model = cp_model.CpModel()
        columns = [model.new_int_var(6, bound, f'column_{i}') for i in range(len(layer_keys))]
        model.add(columns[0] == 6)
        xs = {name: columns[layer_of[name]]-footprints[name][0] for name in names}
        zs = {name: model.new_int_var(2, bound, f'z_{i}') for i, name in enumerate(names)}
        for i in range(1, len(columns)):
            previous_width = max(footprints[n][1]-footprints[n][0]+1 for n in names if layer_of[n] == i-1)
            # Space for output repeater, dust, input repeater. Later retries
            # add routing room rather than silently using the custom placer.
            model.add(columns[i] >= columns[i-1] + previous_width+(13 if i in bus_layers else 3)+extra)
        x_intervals, z_intervals = [], []
        for name in names:
            minx, maxx, minz, maxz = footprints[name]
            x_intervals.append(model.new_fixed_size_interval_var(xs[name]+minx-1, maxx-minx+3, f'x_box_{name}'))
            z_intervals.append(model.new_fixed_size_interval_var(zs[name]+minz-spacing//2,
                                                                 maxz-minz+1+spacing, f'z_box_{name}'))
            model.add_hint(zs[name], seed[name][1])
        model.add_no_overlap_2d(x_intervals, z_intervals)
        hinted_column = 6
        for i, column in enumerate(columns):
            seed_column = min(seed[n][0]+footprints[n][0] for n in names if layer_of[n] == i)
            if sequential_routing and i:
                previous_width = max(footprints[n][1]-footprints[n][0]+1
                                     for n in names if layer_of[n] == i-1)
                hinted_column += previous_width+(13 if i in bus_layers else 5)+extra
            hinted_column = max(hinted_column, seed_column)
            model.add_hint(column, hinted_column if sequential_routing else seed_column)
            lane = sorted((n for n in names if layer_of[n] == i), key=lambda n: seed[n][1])
            for a, b in zip(lane, lane[1:]):
                model.add(zs[b]+footprints[b][2] >= zs[a]+footprints[a][3]+1+spacing)
        # Terminal dust lies outside the template footprint. Unrelated pins
        # in adjacent columns must not overlap or touch, even when gate bodies
        # themselves satisfy NoOverlap2D.
        terminals = []
        for name in names:
            gate = by_name[name]
            template = GATES[gate['gate']]
            for pin,t in (template.inputs | template.outputs).items():
                terminals.append((name, gate['pins'][pin], xs[name]+t.x+(2 if pin == 'Y' else -2), zs[name]+t.z))
        for i,(a,bit,ax,az) in enumerate(terminals):
            for j,(b,other,bx,bz) in enumerate(terminals[:i]):
                if bit == other or abs(layer_of[a]-layer_of[b]) != 1:
                    continue
                if sequential_routing and max(layer_of[a], layer_of[b]) in bus_layers:
                    # These columns already have ten blocks of terminal
                    # clearance in X. Avoid thousands of redundant abs vars.
                    continue
                dx = model.new_int_var(0, 2*bound, f'clear_x_{i}_{j}')
                dz = model.new_int_var(0, 2*bound, f'clear_z_{i}_{j}')
                model.add_abs_equality(dx, ax-bx)
                model.add_abs_equality(dz, az-bz)
                model.add(dx+dz >= 2)
        distances = []
        for i, net in enumerate(netlist['nets']):
            source = net['source']
            targets = [s for s in net['sinks'] if s[0] != 'port']
            if len(targets) > 1:
                # Shared controls are trees, so price their full vertical span,
                # not just one sink or a sum that ignores the common trunk.
                taps = [zs[t[0]]+GATES[by_name[t[0]]['gate']].inputs[t[1]].z for t in targets]
                if source[0] not in {'port', 'constant'}:
                    taps.append(zs[source[0]]+GATES[by_name[source[0]]['gate']].outputs[source[1]].z)
                lo = model.new_int_var(0, 2*bound, f'bus_low_{i}')
                hi = model.new_int_var(0, 2*bound, f'bus_high_{i}')
                model.add_min_equality(lo, taps)
                model.add_max_equality(hi, taps)
                distances.append(hi-lo)
            if source[0] in {'port', 'constant'}:
                continue
            for j, sink in enumerate(targets):
                a, b = source[0], sink[0]
                ta = GATES[by_name[a]['gate']].outputs[source[1]]
                tb = GATES[by_name[b]['gate']].inputs[sink[1]]
                dx = model.new_int_var(0, 2*bound, f'dx_{i}_{j}')
                dz = model.new_int_var(0, 2*bound, f'dz_{i}_{j}')
                if tuple(sink) not in cuts:
                    model.add(xs[b]+tb.x-2 >= xs[a]+ta.x+2)
                model.add_abs_equality(dx, xs[b]+tb.x-2 - (xs[a]+ta.x+2))
                model.add_abs_equality(dz, zs[b]+tb.z - (zs[a]+ta.z))
                distances.extend((dx, dz))
        right = model.new_int_var(0, 2*bound, 'right')
        bottom = model.new_int_var(0, 2*bound, 'bottom')
        model.add_max_equality(right, [xs[n]+footprints[n][1]+2 for n in names])
        model.add_max_equality(bottom, [zs[n]+footprints[n][3] for n in names])
        # Lexicographic proxy: wire distance first, extent second. This is
        # deliberately not advertised as optimal routed area or block count.
        weight = 4*bound+1
        model.minimize(weight*sum(distances) + right+bottom)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = remaining / (5-attempt)
        solver.parameters.num_search_workers = solver_workers
        solver.parameters.random_seed = 0
        status = solver.solve(model)
        solve_time += solver.wall_time
        entry = {"extra_column_gap": extra, "status": solver.status_name(status),
                 "solve_seconds": solver.wall_time}
        attempts.append(entry)
        if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
            continue
        positions = {n: (solver.value(xs[n]), solver.value(zs[n])) for n in names}
        entry.update({"objective": solver.objective_value, "best_bound": solver.best_objective_bound,
                      "estimated_wire_steps": sum(solver.value(d) for d in distances)})
        routing_started = time.monotonic()
        try:
            commands, layout = build_layout(netlist, positions, origin, spacing, offset)
        except ValueError as exc:
            entry["routing_seconds"] = time.monotonic()-routing_started
            entry["routing_error"] = str(exc)
            continue
        if layout['routing']['method'] == 'greedy':
            sx = layout['local_bounds']['x'][0]-2
            sz = layout['local_bounds']['z'][0]-2
            positions = {n: (x-sx, z-sz) for n, (x, z) in positions.items()}
            commands, layout = build_layout(netlist, positions, origin, spacing, offset)
        entry["routing_seconds"] = time.monotonic()-routing_started
        bounds = layout['local_bounds']
        layout['placement'] = {
            "method": "ortools_cp_sat", "ortools_version": ortools.__version__,
            "solver_status": entry['status'], "attempts": attempts,
            "solver_seconds": solve_time, "elapsed_seconds": time.monotonic()-started,
            "solver_workers": solver_workers,
            "routing_seconds": sum(a.get("routing_seconds", 0) for a in attempts),
            "objective": "all gate connections plus shared-control span, then extent; fixed layer order",
            "estimated_wire_steps": entry['estimated_wire_steps'],
            "wire_steps": sum(len(r['path_xyz'])-1 for r in layout['routes']),
            "bridges": sum(r['bridge_count'] for r in layout['routes']),
            "horizontal_area": (bounds['x'][1]-bounds['x'][0]+1)*(bounds['z'][1]-bounds['z'][0]+1),
            "requested_spacing": requested_spacing, "effective_spacing": spacing, "routing_validated": True}
        return commands, layout
    reasons = '; '.join(a.get('routing_error', a['status']) for a in attempts)
    raise RoutingError(f"OR-Tools did not produce a routable placement: {reasons}. "
                       "Try --solver-seconds 30 or more --spacing. "
                       "No custom fallback was exported.")


# Legacy custom placement retained for reference; no longer executable.
# def minecraft(netlist, origin=None, spacing=2, offset=(0, 0, 0), placer="custom", solver_seconds=10):
#     """Compact placement using actual routed length and template clearance.
# 
#     Start with dependency layers, then try small moves of each gate. Accept
#     only fully routable layouts that shorten wires or reduce bounding area.
#     This is a bounded local search, not a guarantee of a global optimum.
#     """
#     from gate_templates import GATES
# 
#     if placer == "ortools":
#         return ortools_minecraft(netlist, origin, spacing, offset, solver_seconds)
#     if placer != "custom":
#         raise ValueError(f"Unknown placer: {placer}")
# 
#     requested_spacing = spacing
#     for extra in (0, 2, 4, 8, 16, 24):
#         spacing = requested_spacing + extra
#         positions = gate_positions(netlist, GATES, spacing)
#         try:
#             commands, layout = build_layout(netlist, positions, origin, spacing, offset)
#             break
#         except RoutingError:
#             if extra == 24:
#                 raise
# 
#     def score(result):
#         bounds = result["local_bounds"]
#         area = ((bounds["x"][1] - bounds["x"][0] + 1) *
#                 (bounds["z"][1] - bounds["z"][0] + 1)) if bounds else 0
#         return (sum(r["bridge_count"] for r in result["routes"]),
#                 sum(len(r["path_xyz"]) - 1 for r in result["routes"]), area)
# 
#     best_score, attempts = score(layout), 0
#     moves = [(dx, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz]
#     changed = True
#     # Bridged layouts cost more to evaluate; keep larger circuits responsive.
#     attempt_limit = 0 if best_score[0] or len(netlist["gates"]) > 12 else 256
#     while changed and attempts < attempt_limit:
#         changed = False
#         for gate in netlist["gates"]:
#             name = gate["name"]
#             x, z = positions[name]
#             best = None
#             for dx, dz in moves:
#                 if attempts >= attempt_limit:
#                     break
#                 attempts += 1
#                 candidate = {**positions, name: (x + dx, z + dz)}
#                 try:
#                     candidate_commands, candidate_layout = build_layout(
#                         netlist, candidate, origin, spacing, offset)
#                 except ValueError:
#                     continue  # Overlap, terminal conflict, or no safe route.
#                 candidate_score = score(candidate_layout)
#                 if candidate_score < best_score:
#                     best_score = candidate_score
#                     best = candidate, candidate_commands, candidate_layout
#             if best is not None:
#                 positions, commands, layout = best
#                 changed = True
#     # Keep the whole build close to the player even when optimization moved
#     # the first gate east or north to meet its neighbor.
#     if positions and layout["local_bounds"]:
#         sx = layout["local_bounds"]["x"][0] - 2
#         sz = layout["local_bounds"]["z"][0] - 2
#         positions = {name: (x - sx, z - sz) for name, (x, z) in positions.items()}
#         commands, layout = build_layout(netlist, positions, origin, spacing, offset)
#     layout["placement"] = {"method": "footprint_and_routed_wire_compaction",
#                            "candidates_checked": attempts, "wire_steps": score(layout)[1],
#                            "bridges": score(layout)[0], "effective_spacing": spacing,
#                            "horizontal_area": score(layout)[2]}
#     return commands, layout
# 

def integrated_clock_netlist(netlist):
    """One oscillator per HDL clock domain; preserve every storage feedback net."""
    registers = netlist.get('registers', [])
    if not registers:
        raise ValueError("--clock-source integrated requires at least one register.")
    domains = defaultdict(list)
    for register in registers:
        domains[register['pins']['CLK']].append(register)
    clock_bits = set(domains)
    gates, bindings, tied_resets = [], [], set()
    clock_sources = {}
    names = {g['name'] for g in [*netlist['gates'], *registers]}
    for bit, members in domains.items():
        clock_net = next((n for n in netlist['nets'] if n['bit'] == bit), None)
        expected = {(r['name'], 'CLK') for r in members}
        if (clock_net is None or clock_net['source'][0] != 'port'
                or {tuple(s) for s in clock_net['sinks']} != expected):
            raise ValueError("The integrated clock can replace only a top-level clock input used "
                             "exclusively by DFF clock pins; clocks used by other logic need an external tap.")
        if len(members) > 1:
            name = f'__clock_{bit}'
            while name in names:
                name += '_'
            names.add(name)
            clock_sources[bit] = name
            gates.append({'name': name, 'gate': 'CLOCK_SOURCE', 'pins': {'Y': bit}})
            bindings.append({'source': 'integrated_shared', 'bit': bit,
                             'hdl_ports': [p['name'] for p in netlist['ports'] if p['bit'] == bit],
                             'clock_gate': name, 'registers': [r['name'] for r in members],
                             'external_clock_routed': True})
    for register in registers:
        if register['clock_edge'] != 'rising' or register.get('reset') not in (
                None, {'kind': 'asynchronous', 'active_level': 1, 'value': 0}):
            raise ValueError("The integrated template supports rising-edge DFFs with optional "
                             "active-high asynchronous reset to zero only.")
        if register.get('initial_value') not in (None, 'x'):
            raise ValueError("Declared register initialization is not implemented by the integrated template.")
        clock_bit = register['pins']['CLK']
        shared = clock_bit in clock_sources
        pins = {p: b for p, b in register['pins'].items() if p != 'CLK' or shared}
        # A plain DFF uses the same storage circuit with reset held inactive.
        if pins.get('RESET') == '0':
            del pins['RESET']
            tied_resets.add((register['name'], 'RESET'))
        kind = 'ASYNCDFF' if 'RESET' in pins else 'DFF'
        gates.append({'name': register['name'],
                      'gate': kind + ('_SHARED' if shared else '_LOCAL'), 'pins': pins})
        if not shared:
            bindings.append({'source': 'integrated', 'bit': clock_bit,
                             'hdl_ports': [p['name'] for p in netlist['ports'] if p['bit'] == clock_bit],
                             'register': register['name'], 'external_clock_routed': False})
    nets = []
    for net in netlist['nets']:
        if net['bit'] in clock_sources:
            nets.append({**net, 'source': [clock_sources[net['bit']], 'Y']})
            continue
        if net['bit'] in clock_bits:
            continue
        sinks = [s for s in net['sinks'] if tuple(s) not in tied_resets]
        if sinks:
            nets.append({**net, 'sinks': sinks})
    # Preserve the old acyclic order. When blocked by a sequential cycle, cut
    # only incoming storage dependencies for placement, never the physical net.
    pending = [*netlist['gates'], *gates]
    producers = {g['pins']['Y']: g['name'] for g in pending}
    register_names = {r['name'] for r in registers}
    ordered, done, cuts = [], set(), set()
    while pending:
        ready = [g for g in pending if all(b not in producers or producers[b] in done
                 for p, b in g['pins'].items() if p != 'Y' and (g['name'], p) not in cuts)]
        if not ready:
            new_cuts = {(g['name'], p) for g in pending if g['name'] in register_names
                        for p, b in g['pins'].items() if p not in {'Y', 'CLK'}
                        and b in producers and producers[b] not in done} - cuts
            if not new_cuts:
                raise ValueError('Combinational feedback is not supported.')
            cuts.update(new_cuts)
            continue
        for cell in ready:
            pending.remove(cell)
            ordered.append(cell)
            done.add(cell['name'])
    return {**{k: v for k, v in netlist.items() if k != 'registers'},
            'gates': ordered, 'nets': nets,
            'ports': [p for p in netlist['ports'] if p['bit'] not in clock_bits],
            'clock_bindings': bindings, 'placement_cuts': sorted(cuts)}


def minecraft(netlist, origin=None, spacing=2, offset=(0, 0, 0), placer="ortools", solver_seconds=10,
              solver_workers=1, clock_source="external", routing_limit=2000, progress=False):
    """Place with OR-Tools, then connect gates using the redstone router."""
    if placer != "ortools":
        raise ValueError("Only the ortools placer is supported.")
    if clock_source not in {'external', 'integrated'}:
        raise ValueError("Clock source must be external or integrated.")
    if type(routing_limit) is not int or routing_limit < 1:
        raise ValueError('--routing-limit must be a positive integer.')
    netlist = {**netlist, 'routing_limit': routing_limit, 'progress': progress}
    if clock_source == 'integrated':
        netlist = integrated_clock_netlist(netlist)
    commands, layout = ortools_minecraft(netlist, origin, spacing, offset, solver_seconds, solver_workers)
    if 'clock_bindings' in netlist:
        layout['clocks'] = []
        for binding in netlist['clock_bindings']:
            clock_gate = binding.get('clock_gate', binding.get('register'))
            placement = next(g for g in layout['gates'] if g['name'] == clock_gate)
            gx, gz = placement['xz']
            details = {**binding, 'trigger_local_xyz': [gx+5, 0, gz+7]}
            if binding['external_clock_routed']:
                arrivals, terminal_delays = {}, []
                for route in layout['routes']:
                    if route['bit'] != binding['bit']:
                        continue
                    path = [tuple(p) for p in route['path_xyz']]
                    boosts = {tuple(r['xyz']) for r in route['repeaters']}
                    # Two source repeaters (tap and external output), then
                    # routed repeaters, then the receiver's external input.
                    ticks = arrivals.get(path[0], 2)
                    for p in path:
                        ticks += int(p in boosts)
                        arrivals[p] = ticks
                    terminal_delays.append({'register': route['sink'][0],
                                            'to_clk_pin_repeater_ticks': ticks+1})
                delays = [d['to_clk_pin_repeater_ticks'] for d in terminal_delays]
                details.update({'terminal_delays': terminal_delays,
                                'skew_repeater_ticks': max(delays)-min(delays),
                                'timing_validated': False})
            layout['clocks'].append(details)
        # Keep the existing single-clock metadata available to current callers.
        if len(layout['clocks']) == 1:
            layout['clock'] = layout['clocks'][0]
        layout['feedback_sinks'] = netlist.get('placement_cuts', [])
    return commands, layout


def build_layout(netlist, positions, origin=None, spacing=2, offset=(0, 0, 0), reroute=None):
    """Keep successful routes unchanged; rip up failed passes on fixed gates.

    Whole-net rollback rebuilds supports, repeaters and clearance from scratch,
    so no stale occupancy survives a retry. Promote the blocked branch/net
    ahead of earlier wiring, with accumulated priorities to avoid oscillation.
    """
    complex_routing = sum(len(n['sinks']) for n in netlist['nets']) > 128
    complex_feedback = complex_routing and bool(netlist.get('placement_cuts'))
    if reroute is None:
        # Multiple register outputs can form interleaved fanout trees. Keep
        # the first greedy layout when it works, then allow existing reroutes.
        reroute = (complex_routing or len(netlist.get('clock_bindings', [])) > 1
                   or bool(netlist.get('placement_cuts'))
                   or any(c.get('external_clock_routed') for c in netlist.get('clock_bindings', [])))
    if not reroute:
        commands, layout = _build_layout_once(netlist, positions, origin, spacing, offset)
        layout['routing'] = {'method': 'greedy', 'reroute_passes': 0,
                             'placement_scale': 1, 'failures': []}
        return commands, layout
    priorities, sink_priorities, history = {}, {}, []
    if complex_routing:
        # Large fanout networks spend most of the old router's time proving
        # that ground-only entrances are blocked. Start with layered search.
        priorities[netlist['nets'][0]['bit']] = 0
    for attempt in range(32):
        if netlist.get('progress'):
            print(f"Routing pass {attempt+1}: starting "
                  f"{sum(len(n['sinks']) for n in netlist['nets'])} connections", flush=True)
        # Large register-feedback networks need return corridors as well as
        # forward data/control routes. Start with room for those corridors;
        # keep the established compact policy for the simpler circuits.
        scale = 3 if complex_feedback else (
            1 if attempt < 4 else 2 if attempt < 12 else 3)
        candidate_positions = {n: (x*scale, z*scale) for n,(x,z) in positions.items()}
        try:
            commands, layout = _build_layout_once(
                netlist, candidate_positions, origin, spacing, offset, priorities, sink_priorities)
            layout['routing'] = {'method': ('rip_up_reroute' if history else
                                           'layered_astar' if priorities else 'greedy'),
                                 'reroute_passes': len(history), 'placement_scale': scale,
                                 'failures': history}
            return commands, layout
        except NetRoutingError as exc:
            history.append({'bit': exc.bit, 'sink': list(exc.sink),
                            'ripped_nets': exc.routed_bits, 'error': str(exc)})
            priorities[exc.bit] = priorities.get(exc.bit, 0) + 1
            sink_priorities[(exc.bit, exc.sink)] = sink_priorities.get((exc.bit, exc.sink), 0) + 1
            if attempt == 31:
                raise RoutingError(f"Rip-up/reroute exhausted after {len(history)} failed passes: {exc}") from exc


def _build_layout_once(netlist, positions, origin=None, spacing=2, offset=(0, 0, 0),
                       priorities=None, sink_priorities=None):
    """Fanout trees with flat terminals and optional staircase bridges.

    Refuse unsupported electrical layouts instead of quietly shorting wires.
    Terminal positions and block footprints come from gate_templates.py.
    """
    GATES = load_templates().ROUTABLE_GATES
    if netlist.get('registers'):
        raise ValueError("Automatic register wiring requires a routable DFF clock terminal.")
    priorities, sink_priorities = priorities or {}, sink_priorities or {}
    large_feedback = bool(netlist.get('placement_cuts')) and len(netlist['gates']) > 128

    for kind in {g["gate"] for g in netlist["gates"]}:
        validate_template(kind)

    if spacing < 2:
        raise ValueError("--spacing must be at least 2 empty blocks between gate lanes.")
    for net in netlist["nets"]:
        if net["source"][0] == "constant":
            raise ValueError("Constant nets are recorded in gate JSON; Minecraft constant sources are not implemented.")
    blocks, endpoints, occupied, placements = {}, {}, set(), []

    def put(x, y, z, state):
        if state == "minecraft:stone":
            state = "minecraft:stone_bricks"
        key = (x, y, z)
        if key in blocks and blocks[key] != state:
            raise ValueError(f"Block collision at {key}.")
        blocks[key] = state

    for i, gate in enumerate(netlist["gates"]):
        template = GATES[gate["gate"]]
        if not template.blocks:
            raise ValueError(f"{gate['gate']} has no Minecraft blocks in gate_templates.py yet. Gate JSON is still usable.")
        inputs, outputs = dict(template.inputs), dict(template.outputs)
        terms = inputs | outputs
        if any(t is None for t in terms.values()):
            raise ValueError(f"Fill in terminal coordinates for {gate['gate']} first.")
        if any(t.y != 0 or t.side != ("east" if pin == "Y" else "west") for pin, t in terms.items()):
            raise ValueError("This router requires west-facing inputs and east-facing outputs at local y=0.")
        gx, gz = positions[gate["name"]]
        placements.append({"name": gate["name"], "gate": gate["gate"], "xz": [gx, gz]})
        input_points = {(t.x, t.y, t.z) for t in inputs.values()}
        for b in template.blocks:
            state = ("minecraft:redstone_wire" if "minecraft:lever[" in b.state
                     and (b.x, b.y, b.z) in input_points else b.state)
            put(gx + b.x, b.y, gz + b.z, state)
        minx, maxx = min(b.x for b in template.blocks), max(b.x for b in template.blocks)
        minz, maxz = min(b.z for b in template.blocks), max(b.z for b in template.blocks)
        # Include a perimeter for repeaters and electrical clearance. Do not
        # allow even identical template blocks to overlap during compaction.
        footprint = {(gx+x, gz+z) for x in range(minx-1, maxx+2)
                     for z in range(minz-spacing//2, maxz+(spacing+1)//2+1)}
        if footprint & occupied:
            raise ValueError("Gate footprints overlap or lack electrical clearance.")
        occupied.update(footprint)
        for pin, terminal in terms.items():
            edge = maxx if pin == "Y" else minx
            if terminal.x != edge:
                raise ValueError(f"{gate['gate']}.{pin} must be on the footprint edge.")
            dx = 1 if pin == "Y" else -1
            # Send power east. Java's repeater facing property is its input side.
            x, z = gx + terminal.x + dx, gz + terminal.z
            put(x, -1, z, "minecraft:stone_bricks")
            put(x, 0, z, repeater_state("east"))
            endpoints[(gate["name"], pin)] = (x + dx, z)
    # A shared signal whose sinks occupy one column gets a straight reserved
    # trunk five blocks west of its input terminals. CP-SAT leaves crossing
    # space between that trunk and the preceding gate column.
    buses = {}
    for net in netlist['nets']:
        taps = [endpoints[tuple(s)] for s in net['sinks'] if s[0] != 'port']
        if len(net['sinks']) > 1 and len(taps) == len(net['sinks']) and len({p[0] for p in taps}) == 1:
            buses[net['bit']] = {'x': taps[0][0]-5, 'taps': sorted(set(taps), key=lambda p:p[1])}
    # Two interleaved signals cannot share a straight ground trunk. Keep the
    # dedicated-trunk strategy for unambiguous columns; route competing trees
    # with the general fanout/bridge router instead.
    competing = {bit for bit, bus in buses.items() for other, candidate in buses.items()
                 if bit != other and bus['x'] == candidate['x']
                 and bus['taps'][0][1] <= candidate['taps'][-1][1]+1
                 and candidate['taps'][0][1] <= bus['taps'][-1][1]+1}
    buses = {bit: bus for bit, bus in buses.items() if bit not in competing}
    if priorities:
        # A straight reserved bus can itself be the obstruction. In fallback
        # every shared signal may use an elevated, branching route instead.
        buses = {}
    # Place external controls beside their connected gate, not in bus-name
    # order. ABC cell names are arbitrary and can permute independent bits.
    port_anchors = {}
    control_slots = defaultdict(int)
    for net in netlist["nets"]:
        source, sink = tuple(net["source"]), tuple(net["sinks"][0])
        if source[0] == "port" and sink in endpoints:
            x, z = endpoints[sink]
            port_anchors[source] = (x, z) if len(net["sinks"]) == 1 else (x-6, z)
            if net['bit'] in competing:
                slot = control_slots[x]
                control_slots[x] += 1
                port_anchors[source] = (x-6-8*slot, z)
            if net['bit'] in buses:
                bus = buses[net['bit']]
                port_anchors[source] = (bus['x'], bus['taps'][0][1]-3)
        if sink[0] == "port" and source in endpoints:
            x, z = endpoints[source]
            port_anchors[sink] = (x, z)
    # Unconnected ports and direct input-to-output wires get their own lanes.
    fallback_z = max([0] + [p[1] for p in endpoints.values()]) + 6
    for i, port in enumerate(netlist["ports"]):
        point = (2 if port["direction"] == "input" else 14, fallback_z + i * (spacing + 1))
        point = port_anchors.get(("port", port["name"]), point)
        endpoints[("port", port["name"])] = point
        x, z = point
        put(x, -1, z, "minecraft:stone_bricks" if port["direction"] == "input" else "minecraft:redstone_lamp")
        put(x, 0, z, "minecraft:lever[face=floor,facing=east,powered=false]"
            if port["direction"] == "input" else "minecraft:redstone_wire")
    all_points = list(endpoints.values())
    # A lever/lamp can occupy its own gate endpoint, and connected gate pins
    # can share one dust block. Unrelated signals may never share a position.
    owners = {}
    for net in netlist["nets"]:
        for endpoint in [net["source"], *net["sinks"]]:
            point = endpoints[tuple(endpoint)]
            if point in owners and owners[point] != net["bit"]:
                raise ValueError("Unrelated terminals collide.")
            owners[point] = net["bit"]
    margin = max(16, spacing)
    extent = max([margin] + [abs(v) for p in all_points for v in p]) + margin
    limit = netlist.get('routing_limit', 2000)
    if extent > limit:
        raise ValueError(f"Layout extent {extent} exceeds the {limit}-block routing limit. "
                         "Increase --routing-limit for this build.")
    routes, headroom, signals = [], set(), set()
    competing_approaches = {}
    for net in netlist['nets']:
        if net['bit'] not in competing and not priorities:
            continue
        clearance = set()
        if priorities:
            x, z = endpoints[tuple(net['source'])]
            direction = -1 if net['source'][0] == 'port' else 1
            for distance in range(16):
                point = (x+direction*distance, z)
                clearance.update({point, *neighbors(point)})
        for sink in net['sinks']:
            if sink[0] == 'port':
                continue
            x,z = endpoints[tuple(sink)]
            for distance in range(16 if priorities else 4):
                point = (x-distance,z)
                clearance.update({point, *neighbors(point)})
        competing_approaches[net['bit']] = clearance
    # Route each electrical net as a rooted tree. New branches attach to powered
    # ground-level dust, never to the side of an existing repeater.
    branches = [(net, sink) for net in sorted(netlist["nets"], key=lambda n: (-priorities.get(n['bit'], 0), -len(n["sinks"]),
                sum(abs(endpoints[tuple(n['source'])][i]-endpoints[tuple(n['sinks'][0])][i]) for i in (0,1))))
                for sink in sorted(net["sinks"], key=lambda s: (
                    0 if net['bit'] in buses else -sink_priorities.get((net['bit'], tuple(s)), 0),
                    (sum(abs(endpoints[tuple(s)][i]-endpoints[tuple(net['source'])][i]) for i in (0,1))
                     if priorities else endpoints[tuple(s)][1]))) ]
    trees, net_wires = {}, defaultdict(set)
    for net, sink in branches:
        root, end = endpoints[tuple(net["source"])], endpoints[tuple(sink)]
        tree = trees.setdefault(net["bit"], {(root[0], 0, root[1]): 0})
        obstacles = set(occupied)
        keepouts = set()
        for p in all_points:
            if owners[p] != net["bit"]:
                obstacles |= {p, *neighbors(p)}
        for bit, clearance in competing_approaches.items():
            if bit != net['bit']:
                obstacles.update(clearance)
                if priorities:
                    keepouts.update(clearance)

        if priorities and net['bit'] not in buses:
            # Do not strand an unconnected terminal beside our own repeater
            # or ramp. Leave each remaining input its short westward approach.
            for pending in net['sinks']:
                px, pz = endpoints[tuple(pending)]
                if pending == sink or (px, 0, pz) in tree or pending[0] == 'port':
                    continue
                if pz == root[1] and 0 <= px-root[0] <= 16:
                    continue
                for dx in range(16):
                    point = (px-dx, pz)
                    obstacles.update({point, *neighbors(point)})
                    keepouts.update({point, *neighbors(point)})

        other_wires = set().union(*(v for k,v in net_wires.items() if k != net["bit"]))
        blocked = obstacles | other_wires
        # Existing net components cannot be overwritten. Branches may touch
        # dust carrying the same signal, but must clear repeater side faces.
        for p in tree:
            blocked.update({(p[0], p[2]), *neighbors((p[0], p[2]))})
            if "repeater" in blocks.get(p, ""):
                blocked.update(neighbors((p[0], p[2])))
        for (x,y,z), state in blocks.items():
            if y == 0 and (x,0,z) not in tree and (x,z) not in (root,end):
                blocked.add((x,z))
        bounds = (-margin, extent, -margin, extent)
        if priorities:
            clearance_margin = max(64, margin)
            bounds = (min(-clearance_margin, min(p[0] for p in all_points)-clearance_margin),
                      extent+clearance_margin,
                      min(-clearance_margin, min(p[1] for p in all_points)-clearance_margin),
                      extent+clearance_margin)
        candidates = sorted((p for p,d in tree.items() if p[1] == 0 and d <= 10
                             and "repeater" not in blocks.get(p, "")),
                            key=lambda p: abs(p[0]-end[0])+abs(p[2]-end[1]))
        path = None
        if net['bit'] in buses:
            bus = buses[net['bit']]
            # Build a monotone trunk and individual taps, sharing only their
            # attachment dust. Reserve every future junction from repeaters.
            junctions = {(bus['x'],0,z) for _,z in bus['taps']}
            trunk = [p for p in tree if p[0] == bus['x'] and p[1] == 0 and
                     'repeater' not in blocks.get(p, '')]
            attach = min(trunk, key=lambda p:abs(p[2]-end[1])) if trunk else (root[0],0,root[1])
            path = [attach]
            for target in [(bus['x'],0,attach[2]), (bus['x'],0,end[1]), (end[0],0,end[1])]:
                while path[-1] != target:
                    x,y,z = path[-1]
                    if x != target[0]: x += 1 if target[0] > x else -1
                    elif z != target[2]: z += 1 if target[2] > z else -1
                    path.append((x,y,z))
            start_distance = tree[attach]
            if any((x,z) in obstacles | other_wires or (x,0,z) in tree for x,_,z in path[1:]):
                raise NetRoutingError(f"Reserved control trunk blocked for bit {net['bit']}.",
                                      net['bit'], sink, [r['bit'] for r in routes])
            boosts = repeaters_3d(path, start_distance, junctions)
        elif (end[0],0,end[1]) in tree:
            path, boosts, start_distance = [(end[0],0,end[1])], {}, tree[(end[0],0,end[1])]
        else:
            if priorities:
                layered_candidates = [p for p,d in tree.items() if d <= 10 and p[1] % 3 == 0
                                      and 'repeater' not in blocks.get(p, '')]
                # A return path can be much easier to find from its source.
                # Keep the normal search budget, then try the other direction
                # before discarding a placement with long return connections.
                for reverse in ((True, False) if large_feedback else (True,)):
                    try:
                        path, boosts, start_distance = route_in_layers(
                            layered_candidates, end, tree, obstacles, blocks, headroom, signals, bounds,
                            keepouts=keepouts, preferred_y=6+3*(net['bit'] % 4), reverse=reverse,
                            keepout_height=9 if large_feedback else None)
                        break
                    except RoutingError:
                        pass
            for bridge in (False, True):
                if path is not None or priorities:
                    break
                for candidate in (candidates[:8] if bridge else candidates):
                    start = (candidate[0], candidate[2])
                    if start in obstacles | other_wires:
                        continue
                    branch_blocked = set(blocked)
                    for escape in neighbors(start):
                        touching = {q for q in tree if q[1] == 0 and
                                    (q[0],q[2]) in {escape, *neighbors(escape)}}
                        if touching == {candidate} and escape not in obstacles | other_wires:
                            branch_blocked.discard(escape)
                    # Adjacent sinks can be valid escapes from our own tree.
                    # Check after opening the attachment's neighbors, otherwise
                    # a one-step connection is incorrectly rejected as blocked.
                    if end in branch_blocked and end != start:
                        continue
                    try:
                        if bridge:
                            trial = route_with_bridges(start, end, branch_blocked-{start}, obstacles, blocks, headroom, signals, bounds)
                        else:
                            trial = [(x,0,z) for x,z in route_wire(start, end, branch_blocked-{start}, bounds)]
                        boosts = repeaters_3d(trial, tree[candidate])
                        path, start_distance = trial, tree[candidate]
                        break
                    except RoutingError:
                        continue
                if path is not None:
                    break
        if path is None:
            raise NetRoutingError(f"No fanout branch route for bit {net['bit']} to {sink}.",
                                  net['bit'], sink, [r['bit'] for r in routes])
        # A macro path must not intersect itself or plug a dust staircase's
        # headroom with another segment's support block.
        components = set(path)
        supports = {(x, y-1, z) for x, y, z in path}
        air = {(x, y+1, z) for x, y, z in path}
        if len(components) != len(path) or supports & components or (supports | components) & air:
            raise RoutingError("Route intersects itself or blocks staircase headroom.")
        try:
            validate_wire_branch(path, tree)
        except RoutingError as exc:
            raise NetRoutingError(str(exc), net['bit'], sink, [r['bit'] for r in routes]) from exc
        for x, y, z in path:
            if (x, y-1, z) not in blocks:
                put(x, y-1, z, "minecraft:stone_bricks")
            if (x, y, z) not in blocks:
                facing = boosts.get((x, y, z))
                put(x, y, z, repeater_state(facing)
                    if facing else "minecraft:redstone_wire")
            # One empty horizontal block between unrelated nets prevents shorts.
            net_wires[net["bit"]].update({(x, z), *neighbors((x, z))})
        distance = start_distance
        for i, p in enumerate(path):
            if i:
                distance = 0 if p in boosts else distance+1
            tree[p] = min(tree.get(p, distance), distance)
        headroom.update(air)
        signals.update(components)
        bridge_count = sum(a[1] == 0 and b[1] == 1 for a, b in zip(path, path[1:]))
        routes.append({"bit": net["bit"], "path_xz": [(x, z) for x, y, z in path],
                       "path_xyz": path, "bridge_count": bridge_count,
                       "source": net["source"], "sink": sink,
                       "branch_start_xyz": path[0], "initial_signal_distance": start_distance,
                       "repeaters": [{"xyz": p, "xz": [p[0], p[2]],
                                       "output_direction": f, "facing": OPPOSITE[f]}
                                     for p, f in boosts.items()]})
        if netlist.get('progress') and (len(routes) % 25 == 0 or len(routes) == len(branches)):
            print(f"Routed {len(routes)}/{len(branches)} connections; "
                  f"{len(branches)-len(routes)} remaining in this pass", flush=True)
    if 'clock_bindings' in netlist:
        # The reset sign has a ceiling above it; place solids before components.
        components = {p: s for p, s in blocks.items() if any(k in s for k in
                      ('redstone_wire', 'repeater', 'torch', 'lever', 'sign'))}
        supports = {p: s for p, s in blocks.items() if p not in components}
        commands = block_commands(supports, origin, offset) + block_commands(components, origin, offset)
    else:
        commands = block_commands(blocks, origin, offset)
    bounds = {axis: [min(p[i] for p in blocks), max(p[i] for p in blocks)]
              for i, axis in enumerate(("x", "y", "z"))} if blocks else {}
    return commands, {"coordinate_mode": "absolute" if origin is not None else "player_relative",
                      "origin": origin, "offset": offset if origin is None else None,
                      "local_bounds": bounds, "support_y": -1, "wire_y": 0,
                      "gates": placements, "routes": routes,
                      "control_buses": [{"bit": bit, **bus} for bit,bus in buses.items()],
                      "ports": [{**p, "xz": endpoints[("port", p["name"])]} for p in netlist["ports"]]}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


@lru_cache(maxsize=1)
def connected_hex_template():
    """Add isolated, full-strength input leads to the existing display macro.

    Its manual levers are inside the stored circuit, not on its footprint edge.
    Preserve every other catalog block and route only the four new leads.
    """
    template = load_templates().STANDALONE_GATES['SEVENSEG_HEX']
    blocks = {(b.x, b.y, b.z): b.state for b in template.blocks}
    minx = min(p[0] for p in blocks)
    maxx = max(p[0] for p in blocks)
    minz = min(p[2] for p in blocks)
    maxz = max(p[2] for p in blocks)
    inputs, leads = {}, []
    for pin, terminal in template.inputs.items():
        target = (terminal.x, terminal.y, terminal.z)
        if terminal.y != 0 or not blocks[target].startswith('minecraft:lever['):
            raise ValueError(f'SEVENSEG_HEX {pin}: expected the catalog manual input lever.')
        start = (minx-31, 0, terminal.z)
        signals = {p for p,s in blocks.items() if any(k in s for k in
                   ('redstone_wire', 'repeater', 'torch', 'lever'))} - {target}
        headroom = {(x,y+1,z) for x,y,z in signals}
        forbidden = {(px,py,pz) for x,y,z in signals
                     for px,pz in [(x,z), *neighbors((x,z))] for py in range(y-1,y+2)}
        for dx,dz in ((0,-1), (0,1), (-1,0), (1,0)):
            approach = (terminal.x+2*dx, terminal.z+2*dz)
            tail = [(terminal.x+dx,0,terminal.z+dz), target]
            landing = [(approach[0],0,approach[1]), tail[0]]
            if any(p in blocks or p in forbidden or (p[0],p[1]-1,p[2]) in blocks
                   or (p[0],p[1]+1,p[2]) in blocks or p in headroom for p in landing):
                continue
            try:
                path, boosts, _ = route_in_layers([start], approach, {start:0}, set(), blocks,
                    headroom, signals, (minx-42,maxx+40,minz-32,maxz+32), tail=tail, preferred_y=18)
            except RoutingError:
                continue
            # Restore full power at the old lever location: its internal fanout
            # was designed for a lever's full signal, not a depleted long lead.
            boosts[tail[0]] = DIRECTIONS[(-dx,-dz)]
            break
        else:
            raise RoutingError(f'Cannot connect the existing SEVENSEG_HEX {pin} input safely.')
        entry = (start[0]-2,0,start[2])
        receiver = (start[0]-1,0,start[2])
        path = [entry, receiver, *path]
        boosts[receiver] = 'east'
        validate_wire_branch(path)
        blocks[target] = 'minecraft:redstone_wire'
        for x,y,z in path:
            blocks.setdefault((x,y-1,z), 'minecraft:stone_bricks')
            blocks.setdefault((x,y,z), repeater_state(boosts[(x,y,z)])
                              if (x,y,z) in boosts else 'minecraft:redstone_wire')
        inputs[pin] = entry
        leads.append({'pin': pin, 'path_xyz': path,
                      'repeaters': [{'xyz':p, 'output_direction':d} for p,d in boosts.items()]})
    return blocks, inputs, leads


def attach_hex_displays(commands, layout, buses, progress=False):
    """Connect four-bit output buses to copies of the last-push display macro.

    Core placement/routing is unchanged. Macro internals are copied, and only
    new leads and connections are routed. The caller's objects are not mutated.
    """
    if not buses or len(set(buses)) != len(buses):
        raise ValueError('Name each four-bit output bus once in --hex-display.')
    import copy
    layout = copy.deepcopy(layout)
    core_bounds = copy.deepcopy(layout['local_bounds'])
    ports = {p['name']: p for p in layout['ports']}
    selected = []
    for bus in buses:
        names = [f'{bus}[{i}]' for i in range(4)]
        if any(n not in ports or ports[n]['direction'] != 'output' for n in names) or any(
                n.startswith(bus+'[') and n not in names for n in ports):
            raise ValueError(f'--hex-display {bus} requires a four-bit output bus indexed [3:0].')
        selected.append([ports[n] for n in names])
    origin, offset = layout['origin'], layout['offset'] or (0,0,0)
    # Recover local block coordinates, including block states with sign text.
    blocks = {}
    for command in commands:
        match = re.search(r' run setblock (~?-?\d*) (~?-?\d*) (~?-?\d*) (.*) replace$', command)
        if match is None:
            match = re.fullmatch(r'setblock (-?\d+) (-?\d+) (-?\d+) (.*) replace', command)
        if match is None:
            raise ValueError('Display composition requires exporter setblock commands.')
        xyz = tuple(int(v.lstrip('~') or 0) for v in match.groups()[:3])
        anchor = origin if origin is not None else offset
        point = tuple(xyz[i]-anchor[i] for i in range(3))
        if point in blocks:
            raise ValueError(f'Duplicate core block at {point}.')
        blocks[point] = match[4]
    template, terminals, leads = connected_hex_template()
    minx, maxx = min(p[0] for p in template), max(p[0] for p in template)
    minz, maxz = min(p[2] for p in template), max(p[2] for p in template)
    gx = max(p[0] for p in blocks)+64-minx
    gz = 2-minz
    displays, pending = [], []
    for bus, group in zip(buses, selected):
        name = f'__display_{bus}'
        for (x,y,z),state in template.items():
            point = (x+gx,y,z+gz)
            if point in blocks:
                raise ValueError(f'Display collision at {point}.')
            blocks[point] = state
        display = {'name':name, 'component':'SEVENSEG_HEX', 'bus':bus, 'xz':[gx,gz],
                   'catalog_file':'sevenseg_hex_template.py', 'inputs':{},
                   'lead_routes':leads, 'block_count':len(template)}
        for i,port in enumerate(group):
            pin = f'BIT{i}'
            tx,ty,tz = terminals[pin]
            target = (tx+gx,ty,tz+gz)
            source = (port['xz'][0],0,port['xz'][1])
            display['inputs'][pin] = {'bit':port['bit'], 'xyz':target}
            pending.append((port, source, target, name, pin))
        displays.append(display)
        gz += maxz-minz+1+32
    # Track the real signal distance at each existing output, including fanout.
    distances = {}
    for route in layout['routes']:
        distance = route['initial_signal_distance']
        boosts = {tuple(r['xyz']) for r in route['repeaters']}
        for i,p in enumerate(route['path_xyz']):
            p = tuple(p)
            if i:
                distance = 0 if p in boosts else distance+1
            distances[(route['bit'],p)] = distance
    connections = []
    bounds = (min(p[0] for p in blocks)-64, max(p[0] for p in blocks)+64,
              min(p[2] for p in blocks)-64, max(p[2] for p in blocks)+64)
    for port, source, target, name, pin in pending:
        signals = {p for p,s in blocks.items() if any(k in s for k in
                   ('redstone_wire','repeater','torch','lever'))} - {source,target}
        headroom = {(x,y+1,z) for x,y,z in signals}
        initial = distances.get((port['bit'], source), 0)
        path, boosts, initial = route_in_layers([source], (target[0],target[2]), {source:initial},
            set(), blocks, headroom, signals, bounds, preferred_y=18, max_states=240000)
        for x,y,z in path:
            blocks.setdefault((x,y-1,z), 'minecraft:stone_bricks')
            blocks.setdefault((x,y,z), repeater_state(boosts[(x,y,z)])
                              if (x,y,z) in boosts else 'minecraft:redstone_wire')
        connections.append({'bit':port['bit'], 'source':['port',port['name']], 'sink':[name,pin],
                            'path_xyz':path, 'initial_signal_distance':initial,
                            'repeaters':[{'xyz':p,'output_direction':d,'facing':OPPOSITE[d]}
                                         for p,d in boosts.items()]})
        if progress:
            print(f"Display connections: {len(connections)}/{len(pending)} routed; "
                  f"{len(pending)-len(connections)} remaining", flush=True)
    layout['displays'] = displays
    layout['display_connections'] = connections
    layout['local_bounds'] = {axis:[min(p[i] for p in blocks),max(p[i] for p in blocks)]
                              for i,axis in enumerate(('x','y','z'))}
    layout['block_count'] = len(blocks)
    layout['display_composition'] = {
        'core_bounds':core_bounds, 'core_block_count':len(commands),
        'display_count':len(displays), 'added_blocks':len(blocks)-len(commands),
        'connection_wire_steps':sum(len(r['path_xyz'])-1 for r in connections)}
    components = {p:s for p,s in blocks.items() if any(k in s for k in
                  ('redstone_wire','repeater','torch','lever','sign'))}
    supports = {p:s for p,s in blocks.items() if p not in components}
    return block_commands(supports,origin,offset)+block_commands(components,origin,offset), layout


def gate_test_netlist(selection="ALL"):
    """Independent gates with separate levers; bypass synthesis optimizations."""
    kinds = sorted(set(CELL_TYPES.values())) if selection == "ALL" else [selection]
    ports, cells = {}, {}
    bit = 2
    for kind in kinds:
        cell_type = next(key for key, value in CELL_TYPES.items() if value == kind)
        connections = {}
        pins = ["A", "Y"] if kind in ("NOT", "BUFFER") else ["A", "B", "Y"]
        for pin in pins:
            connections[pin] = [bit]
            ports[f"{kind.lower()}_{pin.lower()}"] = {
                "direction": "output" if pin == "Y" else "input", "bits": [bit]}
            bit += 1
        cells[kind.lower()] = {"type": cell_type, "connections": connections}
    return basic_netlist({"modules": {"gate_tests": {"ports": ports, "cells": cells}}}, "gate_tests")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path)
    parser.add_argument("--top", help="Required for HDL or JSON conversion.")
    parser.add_argument("--gate-test", type=str.upper, choices=["ALL", *sorted(set(CELL_TYPES.values()))],
                        help="Export independent template tests without running Yosys.")
    parser.add_argument("--template-test", type=str.upper, choices=['ASYNCDFF'],
                        help="Export the standalone local-clock DFF template with its levers intact.")
    parser.add_argument("--bridge-demo", action="store_true", help="Generate two crossing wires for in-game testing, without HDL.")
    parser.add_argument("--output", type=Path, default=Path("build/circuit.json"))
    parser.add_argument("--from-json", type=Path, help="Reuse Yosys JSON without running synthesis.")
    parser.add_argument("--yosys", default="yosys", help="Yosys executable path.")
    parser.add_argument("--ghdl-plugin", default="ghdl", help="Plugin name/path; empty for a built-in frontend.")
    parser.add_argument("--std", choices=["93", "08"], default="08")
    parser.add_argument("--synth-profile", choices=["default", "compact"], default="default",
                        help="Opt into case-selector and ABC edge-cost optimization; requires HDL sources.")
    parser.add_argument("--legalize-dffs", action="store_true",
                        help="Map register polarities/presets to the integrated storage cells during synthesis.")
    parser.add_argument("--mcfunction", type=Path, help="Also export supported layouts to Minecraft Java commands.")
    parser.add_argument("--hex-display", nargs='+', metavar='BUS',
                        help="Connect each four-bit output bus to the existing SEVENSEG_HEX component.")
    parser.add_argument("--clock-source", choices=['external', 'integrated'], default='external',
                        help="Use integrated for one redstone oscillator per HDL clock domain, with shared clock wiring.")
    placement = parser.add_mutually_exclusive_group()
    placement.add_argument("--origin", nargs=3, type=int, metavar=("X", "Y", "Z"),
                           help="Opt into absolute coordinates; Y is the wire layer (floor block Y + 1).")
    placement.add_argument("--offset", nargs=3, type=int, default=(0, 0, 0), metavar=("X", "Y", "Z"),
                           help="Offset from the executing player's feet; default: 0 0 0.")
    parser.add_argument("--spacing", type=int, default=2,
                        help="Minimum empty blocks between lanes (default: 2; fanout uses at least 4).")
    parser.add_argument("--routing-limit", type=int, default=2000,
                        help="Maximum routing extent in blocks; raise explicitly for very large circuits.")
    parser.add_argument("--progress", action='store_true',
                        help="Report completed connections and remaining routes in each routing pass.")
    parser.add_argument("--placer", choices=["ortools"], default="ortools",
                        help="OR-Tools is the active placement algorithm.")
    parser.add_argument("--solver-seconds", type=float, default=10,
                        help="Total CP-SAT solving time budget across retries (routing time is additional).")
    parser.add_argument("--solver-workers", type=int, default=1,
                        help="Parallel CP-SAT workers; default 1. Multiple workers may change placement results.")
    args = parser.parse_args()
    try:
        if args.hex_display and (not args.mcfunction or args.gate_test or args.template_test or args.bridge_demo):
            raise ValueError('--hex-display requires an HDL/JSON circuit and --mcfunction.')
        if args.clock_source == 'integrated' and (args.template_test or args.gate_test or args.bridge_demo or not args.mcfunction):
            raise ValueError("--clock-source integrated requires an HDL/JSON circuit and --mcfunction.")
        if (args.synth_profile != "default" or args.legalize_dffs) and (args.from_json or args.gate_test or args.bridge_demo or args.template_test):
            raise ValueError("--synth-profile/--legalize-dffs require HDL sources; they cannot simplify --from-json.")
        if args.template_test:
            if args.sources or args.from_json or args.top or args.gate_test or args.bridge_demo or not args.mcfunction:
                raise ValueError("Use --template-test ASYNCDFF with --mcfunction, without HDL or other test modes.")
            commands, details = standalone_template(args.template_test,
                tuple(args.origin) if args.origin is not None else None, tuple(args.offset))
            args.mcfunction.parent.mkdir(parents=True, exist_ok=True)
            args.mcfunction.write_text('# Standalone ASYNCDFF: local clock and manual levers retained.\n'
                                       '# External CLK is not assigned; this is not an auto-routed HDL build.\n' +
                                       '\n'.join(commands) + '\n', encoding='utf-8')
            write_json(args.mcfunction.with_suffix('.template.json'), details)
            print(f"Standalone template: {args.mcfunction} ({len(commands)} blocks; local clock retained)")
            return
        if args.bridge_demo:
            if args.sources or args.from_json or args.top or args.gate_test or not args.mcfunction:
                raise ValueError("Use --bridge-demo with --mcfunction, without sources, --from-json or --top.")
            commands, routes = bridge_demo(tuple(args.origin) if args.origin is not None else None, tuple(args.offset))
            args.mcfunction.parent.mkdir(parents=True, exist_ok=True)
            args.mcfunction.write_text("# Crossing test: stand on the floor; each lever should control only its own lamp.\n" +
                                       "\n".join(commands) + "\n", encoding="utf-8")
            write_json(args.mcfunction.with_suffix(".routes.json"), routes)
            print(f"Bridge test: {args.mcfunction} ({len(commands)} blocks)")
            return
        if not args.top and not args.gate_test:
            raise ValueError("--top is required for HDL or JSON conversion.")
        if args.from_json and args.sources:
            raise ValueError("Choose HDL sources or --from-json, not both.")
        if args.output.suffix.lower() != ".json":
            raise ValueError("--output must end in .json.")
        if args.gate_test:
            if args.sources or args.from_json or args.top or not args.mcfunction:
                raise ValueError("Use --gate-test with --mcfunction, without sources, --from-json or --top.")
            raw_path = None
            netlist = gate_test_netlist(args.gate_test)
        elif args.from_json:
            raw_path = args.from_json
        else:
            synthesize(args.sources, args.top, args.output, args.yosys, args.ghdl_plugin, args.std,
                       args.synth_profile, args.legalize_dffs)
            raw_path = args.output
        if raw_path is not None:
            netlist = basic_netlist(json.loads(raw_path.read_text(encoding="utf-8")), args.top)
        gate_path = args.output.with_suffix(".gates.json")
        if raw_path is not None and gate_path.resolve() == raw_path.resolve():
            raise ValueError("Choose an --output whose .gates.json path differs from the input JSON.")
        write_json(gate_path, netlist)
        if raw_path is not None:
            print(f"Yosys JSON: {raw_path}")
        print(f"Basic gates: {gate_path} ({len(netlist['gates'])} gates)")
        if netlist.get('registers'):
            print(f"Registers: {len(netlist['registers'])}; clock/reset metadata saved in {gate_path}")
        if args.mcfunction:
            commands, routes = minecraft(netlist, tuple(args.origin) if args.origin is not None else None,
                                         args.spacing, tuple(args.offset), args.placer, args.solver_seconds,
                                         args.solver_workers, args.clock_source, args.routing_limit, args.progress)
            if args.hex_display:
                # Retain the expensive core result even if display attachment
                # fails, so it can be inspected and reused without another run.
                core_path = args.mcfunction.with_name(args.mcfunction.stem+'.core.mcfunction')
                core_path.parent.mkdir(parents=True, exist_ok=True)
                core_path.write_text('\n'.join(commands)+'\n', encoding='utf-8')
                write_json(core_path.with_suffix('.routes.json'), routes)
                commands, routes = attach_hex_displays(commands, routes, args.hex_display, args.progress)
            args.mcfunction.parent.mkdir(parents=True, exist_ok=True)
            header = ("# Player-relative: run this function as a player standing on the floor.\n"
                      "# Supports replace floor blocks at feet Y - 1; build extends east (+X) and south (+Z).\n"
                      if args.origin is None else "# Absolute placement; origin Y is the wire layer.\n")
            if 'clocks' in routes:
                header += '# One integrated redstone oscillator per HDL clock domain.\n'
                if any(c['external_clock_routed'] for c in routes['clocks']):
                    header += '# Shared-clock receivers and routed feedback require in-game timing validation.\n'
            args.mcfunction.write_text(header +
                                       "\n".join(commands) + "\n", encoding="utf-8")
            write_json(args.mcfunction.with_suffix(".routes.json"), routes)
            print(f"Minecraft: {args.mcfunction} ({len(commands)} blocks)")
            metrics = routes['placement']
            print(f"Placer: {metrics['method']}; wire steps: {metrics['wire_steps']}; "
                  f"area: {metrics['horizontal_area']}; bridges: {metrics['bridges']}")
            if routes.get('displays'):
                print(f"Displays: {len(routes['displays'])} existing SEVENSEG_HEX components; "
                      f"core placement metrics above; full bounds: {routes['local_bounds']}")
            for clock in routes.get('clocks', []):
                print(f"Clock: integrated oscillator for {clock['hdl_ports']}; "
                      f"existing clock lever at local {clock['trigger_local_xyz']}")
                if clock['external_clock_routed']:
                    print(f"Shared clock: {len(clock['registers'])} registers; "
                          f"routed repeater skew: {clock['skew_repeater_ticks']} ticks; "
                          "Minecraft timing not validated.")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
