# Gate-OR-Gates

## Physical switches and buttons

The [hardware bridge setup](hardware_bridge/README.md) connects a DE10-Lite's ten
switches and two pushbuttons to Minecraft levers using an Arduino UNO R3. See
[team sharing](hardware_bridge/SHARING.md) to join the live server or share a world
copy. Hardware controls are separate from the HDL placement/routing pipeline below.

## HDL to Minecraft

`hdl_to_minecraft.py` is the pipeline entry point. It uses Python 3.10+ and
an external Yosys executable. Minecraft placement requires OR-Tools from
`requirements.txt` and uses it by default. Minecraft export
imports the existing `gate_templates.py`; synthesis and JSON conversion work
without it.

The exporter accepts the shared `gate_templates.py` catalog directly. Keep that
filename beside `hdl_to_minecraft.py`; the downloaded catalog needs no routing
helpers added to it. The exporter normalizes terminal directions, restores the
missing NAND output metadata, XOR/DFF supports and empty BUFFER entry, and builds
the existing local/shared-clock adapters in memory. It does not edit the catalog.
HDL still maps to basic gates and register cells, followed by OR-Tools placement
and automatic wiring; combined `ANDASYNCDFF`/`SYNCDFF` catalog entries do not change
the existing HDL mapping. Synchronous-reset HDL is not newly supported here.

If the repository already has this updated catalog, the runtime files to push
for this integration are `hdl_to_minecraft.py` and `requirements.txt`. There is no
additional Python helper module. The regression tests are useful to commit too,
but are not runtime dependencies. Existing generated Minecraft files do not need
to be rebuilt just for this compatibility update.

Install Yosys with ABC available and put it on PATH, or pass
`--yosys "C:/path/to/yosys.exe"`. VHDL additionally requires the
[GHDL Yosys plugin](https://github.com/ghdl/ghdl-yosys-plugin).
Use `--ghdl-plugin PATH` if it is not installed under the name `ghdl`.
For a Yosys build with GHDL built in, pass `--ghdl-plugin ""`.
Run Python and Yosys in the same environment (for example, both inside WSL).

### Generate JSON first

The repository's current HDL files are SystemVerilog, not VHDL:

```powershell
python hdl_to_minecraft.py "basic gates/comb version/AND_GATE.sv" --top AND_GATE --output build/and.json
```

For the combined example, pass all design sources, excluding the testbench:

```powershell
$sources = Get-ChildItem "basic gates/comb version/*.sv" | Where-Object { $_.Name -notlike '*_tb.sv' } | ForEach-Object { $_.FullName }
python hdl_to_minecraft.py @sources --top ALL_GATES --output build/all.json
```

For your own VHDL files, pass dependencies before the top-level file:

```powershell
python hdl_to_minecraft.py gates.vhd circuit.vhd --top circuit --output build/circuit.json
```

VHDL defaults to the 2008 standard; `--std 93` is also available. Files must
be synthesizable design sources, without testbench delays or stimulus.
Mixed VHDL/SystemVerilog projects are not supported in this first version.

Outputs:

- `circuit.json`: original Yosys netlist, including bit IDs and port connections.
- `circuit.gates.json`: basic gates, individual port bits, and source/sink nets.
- `circuit.ys`: the Yosys script used for synthesis.
- `circuit.log`: complete Yosys output after an attempted run.

Synthesis flattens hierarchy and maps logic to AND, OR, NOT, NAND, NOR, XOR,
XNOR, and buffers using ABC. Optimizations can change the number or kinds of
gates relative to the HDL. Constants, aliases, and fan-out are preserved in
the simplified JSON. Plain/asynchronous-reset DFFs and enabled registers are
supported as described below. Unsupported sequential cells, combinational loops,
undefined signals and multiple drivers are rejected; raw Yosys JSON remains
available for inspection.

### Experimental Minecraft export

```powershell
python hdl_to_minecraft.py --from-json build/and.json --top AND_GATE --output build/and.json --mcfunction build/and.mcfunction
```

This writes Java Edition `setblock` commands and `and.routes.json`, containing
gate/port positions, wire paths, and repeater directions. Placement defaults
to the executing player's position, aligned to the block grid. Run the function
as a player standing on the floor. The build extends east (+X) and south (+Z),
regardless of which direction the player faces. It does not detect ground
under a flying player.

Support blocks are at feet Y minus 1; the main redstone layer is at feet Y.
If the floor blocks are at Y=-60, standing on them puts your feet at Y=-59:
supports replace floor blocks at -60 and redstone goes at -59. If your displayed
player Y is -60 instead, the supports go at -61. No fixed world height is assumed.
Generated stone supports use stone bricks; the gate's wool and lamps are retained.

For a function installed as `gates:and`, run `/function gates:and` in player chat.
From a command block, select the intended player explicitly, for example
`execute as @p at @s run function gates:and`. The generated commands use `@s`,
so running without an entity executor will not place the relative build.

Use `--offset 3 0 3` to shift the build relative to the player. For a fixed world
location, explicitly pass `--origin X Y Z`; Y denotes the wire layer, so
`--origin 0 -59 0` puts supports at floor-block Y=-60. Origin and offset are
mutually exclusive. Route coordinates remain local; `.routes.json` records
the coordinate mode, offset/origin, local bounding box, and vertical layers.
Use an empty area: the commands replace blocks and do not clear surrounding
terrain. Load/run the function using your Minecraft version's datapack setup.

AND, OR, NOT, NAND, NOR, XOR, XNOR and BUFFER now have block templates.
The pipeline replaces demonstration levers with dust and connects the recorded
terminals. It validates terminal positions, outward sides and component supports
before routing. Terminals must be at local Y=0 on the west/east footprint edges;
input terminal sides are west and output sides east. This metadata is separate
from Minecraft block facing properties.

Test all eight templates independently (no Yosys required):

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py --gate-test ALL --output build/gate_tests.json --mcfunction build/gate_tests.mcfunction --placer ortools
```

Use `--gate-test XOR`, for example, to isolate one gate. The ALL layout has one
row per gate in alphabetical order: AND, BUFFER, NAND, NOR, NOT, OR, XNOR, XOR.
Each row has its own input levers and output lamp; named port coordinates are
recorded in `build/gate_tests.routes.json`. Try all four input combinations for
binary gates and both combinations for unary gates. Expected outputs:

| Gate | 00 | 01 | 10 | 11 |
|---|---|---|---|---|
| AND | 0 | 0 | 0 | 1 |
| NAND | 1 | 1 | 1 | 0 |
| OR | 0 | 1 | 1 | 1 |
| NOR | 1 | 0 | 0 | 0 |
| XOR | 0 | 1 | 1 | 0 |
| XNOR | 1 | 0 | 0 | 1 |

NOT inverts its input; BUFFER follows it. Allow redstone to settle after toggling.
These templates still need in-game truth-table verification.

Then synthesize a connected example with five scalar inputs and one output:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/MIXED_CHAIN.sv --top MIXED_CHAIN --output build/mixed_chain.json --mcfunction build/mixed_chain.mcfunction --placer ortools
```

It computes `y = ((a XOR b) AND (c OR d)) XOR (NOT e)`; Yosys currently maps it
to OR, XOR, AND and XNOR, with 168 placement commands. For example, all inputs
off gives y=1; only e on gives y=0; only a and c on gives y=0; a, c and e on
gives y=1. Copy the mcfunction into your datapack, run `/reload`, then run
`/function gates:mixed_chain` as a player in an empty area. Use your own datapack
namespace if different. Shared-input circuits now use branched routes, although crowded layouts can still fail routing.

OR-Tools chooses gate coordinates using measured footprints and dependency layers.
The old custom compaction implementation is commented out for reference. The
layer-order helper still supplies solver hints; the existing flat wire and bridge
router connects the resulting placement. All candidates must pass that router.

Input levers and output lamps sit directly at their terminal route endpoints.
Connected gate terminals can share a dust block when they carry the same net;
unrelated signals cannot share a position. For the two-AND chain, this aligns
the first output with the second input and leaves only output repeater, one dust
block, and input repeater between gate bodies. The gate origins are eight blocks
apart instead of fifteen. The whole chain uses 62 blocks in a 17 by 4 footprint,
instead of 94 blocks in a 28 by 3 footprint.

Routing first uses breadth-first search on a flat grid. It reserves gate footprints and
leaves a block of separation between unrelated wires. Gate connections use
repeaters for isolation; long routes receive repeaters on straight segments
at most 12 steps apart. Supports are placed before redstone components.
`--spacing` specifies a minimum gap between gate lanes (default: 2; fanout uses at least 4),
rather than the old diagonal placement stride. Increase it if routing needs
more room. The four-bit AND example now occupies 9 by 18 horizontal blocks and
generates 128 placement commands with these defaults. `.routes.json` includes
placement metrics and solver attempts.

Minecraft export supports branched fanout trees but still rejects constants.
It does not build arbitrary vertical routes or clocks, and
greedy route order can fail even when another layout would fit. Failures are
explicit and leave the generated gate JSON available. Generated builds are prototypes: verify the AND
truth table and wire behavior in Minecraft before relying on them. Redstone
propagation delays and torch burnout are not simulated.

### Connect one AND to another AND

`basic gates/comb version/AND_CHAIN.sv` implements `y = (a & b) & c`.
Unlike the four-bit AND example, this creates two gates connected in series:

```text
a ---\
      AND 1 ----\
b ---/          AND 2 ---- y
c -------------/
```

```powershell
python hdl_to_minecraft.py "basic gates/comb version/AND_CHAIN.sv" --top AND_CHAIN --output build/and_chain.json --mcfunction build/and_chain.mcfunction
```

The generated layout has three levers, one external output lamp, and a routed
connection from the first gate's output to an input of the second. The output
should light only when all three levers are on. Wait for the redstone to settle
between changes. `.routes.json` identifies each route's source and sink so the
inter-gate connection can be inspected directly. Synthesis may swap equivalent
AND input pins without changing the result.

Gate-terminal repeaters send power east. In Java Edition the repeater's
`facing` property points toward its input, so eastward signal flow requires
`facing=west`. Route repeaters apply the same opposite-direction conversion;
their metadata distinguishes `output_direction` from the block-state `facing`.
Regenerate and replace older function files to get this direction correction.

### Crossings and the eight-input circuit

When a flat route fails, the router tries whole staircase bridges in all four
horizontal directions. A bridge rises one block per step to dust height Y=3,
crosses on a flat deck, then descends to Y=0. Its stone-brick deck is at Y=2,
leaving air at Y=1 above a lower Y=0 wire. Supported spans are 8, 10 and 12
horizontal steps. Taller bridges use height 5 and spans 16, 20 or 24 to clear
intervening gates. These use solid blocks supporting dust, not Minecraft stair blocks.

The complete bridge is checked for block collisions, dust headroom, and proximity
to existing signals. A bridge crossing a gate footprint must clear the highest
nearby block by at least three blocks. Later ground routes conservatively avoid
existing bridge footprints. Repeaters are inserted only on flat straight sections, at most 12
steps apart including ramp steps. A* search is bounded to 40,000 expanded positions;
this is a conservative prototype and cannot guarantee routing every circuit.
Use an empty area with at least six blocks of clearance above the wire layer.

The eight-input design is four bits wide: it synthesizes to 28 two-input ANDs.
With dependency-tree placement it currently routes without any bridges:

```powershell
python hdl_to_minecraft.py --from-json build/and_8.json --top AND_GATE_8in --output build/and_8.json --mcfunction build/and_8.mcfunction
```

If JSON does not exist yet, replace `--from-json build/and_8.json` with
`"basic gates/comb version/AND_GATE_8in.sv"`. The generated result currently has
60 nets, 1,296 placement commands, and a 39 by 78 block footprint. Each output
bit should light only when the corresponding bit of all eight inputs is on.

Route metadata now includes `path_xyz` (the authoritative route, including
height), `bridge_count`, and repeater `xyz`. `path_xz` remains a projection for
older readers and must not be used alone to place elevated wires.

Generate a small independent crossing test before relying on bridges in-game:

```powershell
python hdl_to_minecraft.py --bridge-demo --mcfunction build/bridge_crossing.mcfunction
```

Install the result as `gates:bridge_crossing`, then run `/reload` and
`/function gates:bridge_crossing` while standing in a separate empty area.
Relative to your aligned feet position, the lower line's lever is `(8,0,2)`
and lamp `(8,-1,16)`; the bridge line's lever is `(2,0,9)` and lamp `(14,-1,9)`.
Test both off, only lower on, only upper on, and both on. Each lamp should follow
only its own lever. The test function contains 56 placement commands.

Python geometry checks cover all four bridge directions, ramp clearance,
support blocks, signal separation, and repeater placement. Bridge turnarounds
also require a gap from earlier wire sections. Each new branch attaches at only
one point; it cannot reconnect around a repeater through a parallel wire or
ramp. These checks apply to generated routes, preserving internal gate clocks:

```powershell
python -m unittest discover -s tests -v
```

These checks are not an in-game redstone simulation. The bridge has not yet been
verified in Minecraft; report the results of the four lever combinations.

### Google OR-Tools placement

OR-Tools is the default and only active placer. Install its dependency:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

`--placer ortools` is accepted but no longer necessary. The old custom placer
is commented out. The solver uses fixed dependency layers and lane order,
optimizing all inter-gate connections plus shared-control vertical spans, followed
by bounding extent. It also separates unrelated terminal dust outside the gate
footprints. The objective is an estimate, not the full routed wire cost. Solver optimality is not global Minecraft optimality.

Failed routes trigger up to five solves with wider columns. `--solver-seconds`
limits solving time, not routing time. Increase `--spacing` for congested lanes.
The existing breadth-first wire search and staircase bridge router remain active.
For shared signals feeding one column, the model reserves crossing space and the
router builds a straight control trunk five blocks west of the input terminals.
Commutative gate inputs put the most shared signal on A. The trunk's taps remain
dust, with repeaters placed between them. Other fanout uses the general tree router.
After shared signals, short data connections route before long ones so detours
cannot consume the short connections' corridors. Each branch accounts for the
distance since its last repeater. Branches avoid
rejoining their tree, overwriting components and touching unrelated signals.

### Test the four-bit 2-to-1 mux

`examples/mux_2.sv` is the supplied design, with WIDTH=4. It has eight data
levers, one select lever and four output lamps. It is four bit lanes, not four
independently controlled muxes: one select controls all lanes.

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/mux_2.sv --top mux_2 --output build/mux_2.json --mcfunction build/mux_2.mcfunction
```

The verified export on the current Yosys version contains 13 basic gates,
994 block commands and four bridge crossings in a 1,760-block horizontal area.
The previous export used 1,388 commands, eight crossings and area 3,555. Fanout
now automatically uses at least four blocks between lanes; no spacing override
is needed. This remains a heuristic layout, not a globally optimal mux. Copy `build/mux_2.mcfunction` into your
existing datapack function directory, then run `/reload` and `/function gates:mux_2`
while standing on the floor in a clear area. Use your datapack namespace if it
is different. Placement follows your feet, including floor height.

Expected behavior: sel OFF copies in1 to out1; sel ON copies in2 to out1.
For example, set in1=0101 and in2=1010 (written MSB to LSB), then flip sel.
The four output lamps should change from 0101 to 1010 after settling.

Current relative coordinates (east X, south Z; inputs at feet Y, lamps at Y-1):

| Port | X | Z |
|---|---:|---:|
| in1[0] | 34 | 9 |
| in1[1] | 34 | 16 |
| in1[2] | 34 | 23 |
| in1[3] | 34 | 30 |
| in2[0] | 12 | 7 |
| in2[1] | 12 | 19 |
| in2[2] | 12 | 26 |
| in2[3] | 12 | 33 |
| sel | 7 | 2 |
| out1[0] | 54 | 7 |
| out1[1] | 54 | 14 |
| out1[2] | 54 | 22 |
| out1[3] | 54 | 29 |

Coordinates can change with synthesis/solver versions; `.routes.json` records
those for each export. Automated checks cover all 512 mux input combinations,
all sink connections, shared-source routing, repeater distance and wire separation.
They do not simulate Minecraft redstone physics; in-game validation remains needed.

### Structural 4-to-1 mux

Yes: module instances and parameter overrides work with Yosys. `examples/mux_4.sv`
instantiates three mux_2 modules. Two choose input pairs using sel[0], and the
third chooses between the pair outputs using sel[1]. Supply both files:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/mux_2.sv examples/mux_4.sv --top mux_4 --output build/mux_4.json --mcfunction build/mux_4.mcfunction
```

The pipeline flattens hierarchy and maps the logic to basic gates. It does not
preserve each mux instance as a prebuilt Minecraft module. `$scopeinfo` cells
are hierarchy metadata and are ignored by the JSON reader. Unknown logic cells
are still rejected. Current synthesis produces 37 basic gates. sel=00,01,10,11
selects in1,in2,in3,in4 respectively. Tests cover all combinations per bit lane
and 1,024 deterministic whole-bus input patterns.

The 4-to-1 now also routes successfully with default options: 3,348 block
commands, 14 bridge crossings, three reserved control trunks and horizontal
area 7,800. Copy `build/mux_4.mcfunction` into your datapack, then run `/reload`
and `/function gates:mux_4` in a fresh empty area. Do not overwrite the old build
in place: the new function does not remove blocks left by an earlier layout.

For a simple in-game test, set in1=0001, in2=0010, in3=0100, in4=1000
(MSB first). The output should follow this table after settling:

| sel[1] | sel[0] | out1[3:0] |
|---|---|---|
| 0 | 0 | 0001 |
| 0 | 1 | 0010 |
| 1 | 0 | 0100 |
| 1 | 1 | 1000 |

Find lever and lamp offsets for the current build with:

```powershell
(Get-Content build/mux_4.routes.json -Raw | ConvertFrom-Json).ports | Format-Table name, direction, xz
```

Geometry tests verify every sink, control-trunk attachment, wire support,
headroom, signal separation and repeater distance for both mux builds. Tests also
check high bridges against gate roofs. In-game redstone physics still requires
manual verification; route success alone does not prove the physical truth table.

### One-bit full adder

`examples/Full_Adder.sv` is the supplied arithmetic design. Each input is one
bit, so this is a one-bit full adder, despite the original four-bit comment.
`out1` is the sum bit and `C_out` is the carry bit.

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/Full_Adder.sv --top Full_Adder --output build/full_adder.json --mcfunction build/full_adder.mcfunction
```

Current export: five gates, 488 blocks and two crossings. Install the function
in the datapack and run `/reload`, then `/function gates:full_adder` in an empty
area. Relative input X/Z offsets are in1=(10,4), in2=(2,6), C_in=(32,6).
The floor lamps are C_out=(58,6) and out1=(50,14). Consult the generated
`.routes.json` if changing placement settings or synthesis versions.

| in1 | in2 | C_in | out1 (sum) | C_out (carry) |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 1 | 0 |
| 0 | 1 | 0 | 1 | 0 |
| 0 | 1 | 1 | 0 | 1 |
| 1 | 0 | 0 | 1 | 0 |
| 1 | 0 | 1 | 0 | 1 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | 1 | 1 |

Unlike the mux, this circuit shares two interleaved inputs in the same column.
The router detects overlapping control-trunk ranges, uses separate fanout trees,
reserves their input approaches and separates their external controls. Mux
columns with a single shared control retain the dedicated-trunk strategy.
All eight logical combinations and export geometry are checked automatically;
the physical redstone circuit still needs in-game testing.

Run all regressions with Yosys on PATH:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

For larger circuits, `--solver-workers 8` enables parallel OR-Tools placement:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py --from-json build/alu_4bit.json --top ALU_4bit --output build/alu_parallel.json --mcfunction build/alu_parallel.mcfunction --solver-seconds 600 --solver-workers 8
```

The default remains one worker to preserve existing small-circuit behavior.
Multiple workers can produce different placements and do not guarantee a
routable result. This option parallelizes placement, not the Python wire router.
The solving budget is shared across five attempts; routing takes additional
time. Successful `.routes.json` exports record the worker count and separate
solver and routing times. The ALU is still an experimental routing workload.

### Compact synthesis for the 4-bit ALU

The original synthesis already runs Yosys optimizations and ABC. For a large
case selector such as `examples/ALU_4bit.sv`, the optional `compact` profile runs
`pmux2shiftx` before gate lowering, then ABC Boolean optimization and mapping
with an edge-cost tradeoff. This preserves all 16 operations and still maps to
the existing basic gate templates. It requires no additional Python libraries.

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/ALU_4bit.sv --top ALU_4bit --synth-profile compact --output build/alu_compact.json --mcfunction build/alu_compact.mcfunction --solver-seconds 60 --solver-workers 8
```

Start from the HDL when changing the synthesis profile. `--from-json` skips
Yosys, so it cannot apply this optimization to an old netlist. After synthesis,
the new JSON can be reused for placement experiments as usual.

With the installed Yosys 0.70 build:

| ALU netlist | Basic gates | Connections to route |
|---|---:|---:|
| Default synthesis | 179 | 354 |
| Compact synthesis | 154 | 308 |

Both profiles pass all 4,096 combinations of the two operands and selector.
Fewer gates do not guarantee shorter wiring: synthesis can increase fanout.
The latest full CLI export completed placement and routing in 112 seconds
(12 seconds solving, 99 seconds routing), using 51,986 block commands. It
passed the connection, separation, support,
headroom and repeater-distance checks. This is a measured result, not a runtime
or size guarantee; parallel placement can vary between runs. Minecraft physics
still needs in-game validation.

Circuits with more than 128 connections use layered routing and bounded
rip-up/reroute passes. Each failed pass discards its wiring and promotes the
blocked net before trying again; later passes expand placement to create room.
Smaller circuits retain their existing routing path. The default synthesis
profile is unchanged, including the mixed-chain regression at 168 blocks.

The generated `.ys` and `.log` files record exactly what Yosys ran. See the
[Yosys technology-mapping reference](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/index_passes_techmap.html)
for the ABC mapping interface.

### DFF and sequential tests

The supplied `ASYNCDFF` is available as a standalone template. All 50 pasted
blocks are retained, with six stone-brick supports added beneath repeaters.
Inputs use the existing west-side terminal convention. The local clock,
observer, reset sign and three levers remain intact. Supports are placed before
components, including the ceiling above the hanging sign.

Generate its player-relative test function:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py --template-test ASYNCDFF --mcfunction build/dff_template.mcfunction
```

Copy `build/dff_template.mcfunction` into the datapack function directory,
then run `/reload` and `/function gates:dff_template` while standing on the
floor in an empty area. This places 56 blocks. The adjacent `.template.json`
records controls relative to that starting position:

| Control | X | Y | Z |
|---|---:|---:|---:|
| Data A lever | 0 | 0 | 2 |
| RESET lever | 0 | 0 | 0 |
| Local clock trigger lever | 5 | 0 | 7 |
| Y output lamp | 9 | -1 | 1 |

For the in-game behavior check, capture both 0 and 1, then check that the stored
value holds between clock events. To distinguish an edge-triggered DFF from a
transparent latch, change A while the clock stays at the same level: Y should
not follow A. To check that reset clears storage rather than only masking the
output, store 1, pause the clock with the storage repeater locked, and turn RESET
on and then off while A stays 1. Y must remain 0 until a new capture event.
An independently running local clock must be paused for that last check.

The JSON converter now keeps plain and asynchronous-reset DFFs in a separate
`registers` list with data/clock/reset pins, edge polarity, reset level/value and
declared initial state. Register outputs break dependency cycles; purely
combinational loops are still rejected. These examples generate JSON:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/DFF.sv --top DFF --output build/dff.json
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/ASYNCDFF.sv --top ASYNCDFF --output build/asyncdff.json
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/ASYNCDFF.sv examples/REGISTER_CHAIN.sv --top REGISTER_CHAIN --output build/register_chain.json
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/TOGGLE_FF.sv --top TOGGLE_FF --output build/toggle_ff.json
```

`REGISTER_CHAIN` has two flip-flops on one clock; the second captures the
previous value of the first. `TOGGLE_FF` tests legal feedback through a register.
The supplied physical template declares `CLK=None` because its redstone clock
is already inside the circuit. To use that clock in the normal Yosys -> OR-Tools
-> router pipeline, select `--clock-source integrated`:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/ASYNCDFF.sv --top ASYNCDFF --clock-source integrated --output build/asyncdff.json --mcfunction build/asyncdff.mcfunction
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/DFF.sv --top DFF --clock-source integrated --output build/dff.json --mcfunction build/dff.mcfunction
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/DFF_LOGIC.sv --top DFF_LOGIC --clock-source integrated --output build/dff_logic.json --mcfunction build/dff_logic.mcfunction
```

This places the complete DFF footprint using OR-Tools, keeps its clock
lever/observer/oscillator intact, and routes data, reset and output connections.
The logical `CLK` input is supplied by that oscillator, so no external CLK lever
is created. The `.gates.json` retains the original clock net; `.routes.json`
records the physical clock binding and the clock lever's coordinates
relative to the build origin. In the plain DFF variant, the unused reset lever
becomes unpowered dust. The ASYNCDFF build uses 68 blocks; `DFF_LOGIC` connects
an AND into the DFF and an OR after it, using 126 blocks.

Integrated mode supports rising-edge registers with optional active-high
asynchronous reset to zero. An independent single-register clock retains the
entire original DFF footprint. Registers sharing one HDL clock instead use one
copy of the original oscillator and `ASYNCDFF_SHARED`/`DFF_SHARED` receivers.
Each receiver exposes a west-side CLK input at `(0,0,7)`, which drives the
original clock-controlled torch block at `(1,0,5)` through an isolating repeater.
Its storage and reset geometry is retained; its private oscillator is removed.
The shared oscillator keeps the supplied observer/lever and starts on placement.
The `.routes.json` contains a `clocks` list with the source and its registers;
a single clock domain also retains the `clock` metadata entry.

Register feedback is allowed: the placer cuts storage-input dependencies when
it encounters a cycle, then the router still connects those inputs, including
westward returns. `feedback_sinks` records these placement cuts. They do not
delete any logical or physical connection. Pure combinational loops, explicit
initialization, and clocks also used by other logic are still rejected.
The standalone template command remains available
for checking the original build without synthesis or routing.

### Shared-clock RALU

The supplied `examples/RALU_async.sv` has twelve registers: four bits each for
the two stored inputs and the result. Clock enables are lowered automatically
with Yosys `dffunmap -ce-only` and `techmap`, so hold/load operations become
ordinary DFFs plus feedback logic before ABC mapping. No manual JSON lowering
step is needed:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/RALU_async.sv --top RALU_async --clock-source integrated --output build/ralu_async.json --mcfunction build/ralu_async.mcfunction --solver-seconds 30 --solver-workers 8
```

For smaller shared-clock and feedback tests:

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/ASYNCDFF.sv examples/REGISTER_CHAIN.sv --top REGISTER_CHAIN --clock-source integrated --output build/register_chain_shared.json --mcfunction build/register_chain_shared.mcfunction
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/TOGGLE_FF.sv --top TOGGLE_FF --clock-source integrated --output build/toggle_ff.json --mcfunction build/toggle_ff.mcfunction
```

Shared-clock export verifies connectivity and clearance, not clock timing.
Different routed repeater counts introduce clock skew; the original oscillator
period is not adjusted to the RALU's combinational propagation delay. The new
receivers and feedback builds require in-game timing validation before claiming
cycle-accurate HDL behavior. The clock metadata reports per-register repeater
delay and `skew_repeater_ticks`; these counts exclude dust/block-update timing.
`tests/test_ralu.py` separately verifies all sixteen
instructions, hold, transfers, feedback, overflow and asynchronous reset against
both RTL and the mapped netlist over an 82-step trace.

### Two-DFF half-adder test

`examples/REGISTERED_HALF_ADDER.sv` samples A and B into separate DFFs, using
explicitly independent `CLK_A` and `CLK_B` inputs supplied by their original
integrated oscillators. An XOR produces the sum bit and an AND produces carry.
RESET clears both stored inputs. This tests two registers, shared reset,
register-output fanout, and routing into two combinational gates.

```powershell
.\venv\Scripts\python.exe hdl_to_minecraft.py examples/REGISTERED_HALF_ADDER.sv --top REGISTERED_HALF_ADDER --clock-source integrated --output build/registered_half_adder.json --mcfunction build/registered_half_adder.mcfunction
```

The generated build has 503 blocks and uses OR-Tools plus one rip-up/reroute pass.
After copying the mcfunction into the datapack, run `/reload`, then
`/function gates:registered_half_adder` in an empty area. Leave the clocks alone.
Use a fresh empty area when replacing an earlier generated layout: placement
commands do not remove obsolete wires from a previous build.
Set the input levers and allow both DFFs to sample and the output to settle:

| A | B | Carry `result[1]` | Sum `result[0]` | Value |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 |
| 1 | 1 | 1 | 0 | 2 |

Because the clocks are independent, the output can temporarily reflect one new
input and one old input while changing both levers. This is intentional in the
HDL; it is not a test of simultaneous sampling on a shared clock. RESET should
clear both output bits after propagation through the combinational gates.
The adjacent `.routes.json` lists the input/output positions and both clocks.

`tests/test_sequential.py` checks explicit clock/data/reset traces for both the
original HDL and mapped Yosys cells: rising-edge capture, holding with a high
clock or on a falling edge, asynchronous reset, reset release, two-stage
shifting, toggling feedback and logic around a DFF. It also exports the plain DFF,
ASYNCDFF, DFF_LOGIC and REGISTERED_HALF_ADDER through OR-Tools and checks every template block, routed
connection, preserved clock control and support placement. The logical checks
exercise both clock orders, simultaneous edges, all four stable input values,
hold, reset and reset release for the half-adder. They use Yosys `clk2fflogic` and SAT verification
with the installed `simcells.v` models; it needs no extra Python dependency.
These are logical checks and template geometry checks, not a Minecraft physics
simulation. [Yosys documents the FF cell semantics here](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cell/gate_reg_ff.html).

