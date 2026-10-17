""" YO YO YO. This is our Verilog To Minecraft Project.
This file is specifically for translating the yosys into minecraft blocks.
We use setblock commands in Minecraft to place each block.
The setblock command works likle this:
    setblock <x> <y> <z> <minecraft block id>
"""

from dataclasses import dataclass
from pathlib import Path
import argparse


@dataclass(frozen=True)
class Block:
    x: int
    y: int
    z: int
    state: str  # This is where you put the minecraft block ID. You can follow it by a property (ex: facing east)

@dataclass(frozen=True)
class Terminal:
    # This is where the different gates connect to each other. 
    x: int
    y: int
    z: int
    side: str


@dataclass(frozen=True)
class GateTemplate:
    # The big guns. Gate templates will store all blocks, input terminals, output terminal. And maybe needed notes
    blocks: tuple[Block, ...]
    inputs: dict[str, Terminal | None]
    outputs: dict[str, Terminal | None]
    notes: str = ""  # notes if specific block setups are needed.



GATES: dict[str, GateTemplate] = {
    "NOT": GateTemplate(
        blocks=(
            
        ),
        inputs={"A": None},
        outputs={"Y": None},
    ),
    "AND": GateTemplate(
        blocks=(
            Block(0, -1, 0, "minecraft:redstone_lamp"),
            Block(0, 0, 0, "minecraft:lever[face=floor,facing=west,powered=false]"),
            Block(1, -1, 0, "minecraft:orange_wool"),
            Block(1, 0, 0, "minecraft:redstone_wire"),
            Block(0, -1, 2, "minecraft:redstone_lamp"),
            Block(0, 0, 2, "minecraft:lever[face=floor,facing=west,powered=false]"),
            Block(1, -1, 2, "minecraft:orange_wool"),
            Block(1, 0, 2, "minecraft:redstone_wire"),
            Block(2, 0, 2, "minecraft:orange_wool"),
            Block(2, 0, 1, "minecraft:orange_wool"),
            Block(2, 0, 0, "minecraft:orange_wool"),
            Block(2, 1, 0, "minecraft:redstone_torch"),
            Block(2, 1, 2, "minecraft:redstone_torch"),
            Block(2, 1, 1, "minecraft:redstone_wire"),
            Block(3, -1, 2, "minecraft:orange_wool"),
            Block(3, -1, 1, "minecraft:orange_wool"),
            Block(3, -1, 0, "minecraft:orange_wool"),
            Block(3, 0, 1, "minecraft:redstone_wall_torch[facing=east]"),
            Block(4,-1,1, "minecraft:redstone_lamp"),
            Block(4,0,1, "minecraft:redstone_wire"),
        ),
        inputs={"A": None, "B": None},
        outputs={"Y": None},
    ),
    "OR": GateTemplate(
        blocks=(
            # Add blocks here.
        ),
        inputs={"A": None, "B": None},
        outputs={"Y": None},
    ),
    "NAND": GateTemplate(
        blocks=(
            # Add blocks here.
        ),
        inputs={"A": None, "B": None},
        outputs={"Y": None},
    ),
    "NOR": GateTemplate(
        blocks=(
            Block(0, -1, 0, "minecraft:redstone_lamp"),
            Block(0, 0, 0, "minecraft:lever[face=floor,facing=west,powered=false]"),
            Block(1, -1, 0, "minecraft:yellow_wool"),
            Block(1,0,0, "minecraft:redstone_wire"),
            Block(2, 0, 0, "minecraft:yellow_wool"),
            Block(3, 0, 0, "minecraft:redstone_wall_torch[facing=east]"),
            Block(4,-1,0, "minecraft:redstone_lamp"),
            Block(4,0,0, "minecraft:redstone_wire"),
        ),
        inputs={"A": None, "B": None},
        outputs={"Y": None},
    ),
    "XOR": GateTemplate(
        blocks=(
            # Add blocks here.
        ),
        inputs={"A": None, "B": None},
        outputs={"Y": None},
    ),
    "XNOR": GateTemplate(
        blocks=(
            # Add blocks here.
        ),
        inputs={"A": None, "B": None},
        outputs={"Y": None},
    ),
    "BUFFER": GateTemplate(
        blocks=(
            # Add blocks here.
        ),
        inputs={"A": None},
        outputs={"Y": None},
    ),
}


#GUYS IMPORTANT NOTE. We have to change the lever for redstone for gates without the initial inputs.
# i thought of a method. when placing the redstone torch, for a terminal, we can check if there is already a piece of redstone wire there, and then if there is, we use a keep command, and if not, we place it. 

def placement_commands(
    gate_name: str, origin: tuple[int, int, int] = (0, 0, 0)
) -> list[str]:
    """Translate a single gate to absolute world coordinates.

    Terminal metadata and the tested flag do not affect placement, so you can
    export a gate while still measuring its terminals and testing its behavior.
    This does not route connections, rotate gates, or simulate redstone.
    """
    gate = GATES[gate_name.upper()]
    if not gate.blocks:
        raise ValueError(f"{gate_name.upper()} has no blocks yet. Fill in its template first.")
    ox, oy, oz = origin
    return [
        f"setblock {ox + b.x} {oy + b.y} {oz + b.z} {b.state} replace"
        for b in gate.blocks
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export one manually recorded gate.")
    parser.add_argument("gate", type=str.upper, choices=GATES)
    parser.add_argument("--origin", type=int, nargs=3, default=(0, 0, 0), metavar=("X", "Y", "Z"))
    parser.add_argument("--output", type=Path, help="Write an mcfunction file instead of printing.")
    args = parser.parse_args()
    try:
        commands = placement_commands(args.gate, tuple(args.origin))
    except ValueError as exc:
        parser.error(str(exc))
    content = "\n".join(commands) + "\n"
    if args.output:
        # Replaces the specified file. Choose a separate test file if needed.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(f"Wrote {len(commands)} commands to {args.output}")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
