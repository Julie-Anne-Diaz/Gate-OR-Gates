# Gate-OR-Gates

**Turn HDL into Minecraft redstone. Control it with real hardware.**

Write a circuit in SystemVerilog, synthesize it with Yosys, place its gates with
OR-Tools, and export a Minecraft build function. Connect a DE10-Lite through an
Arduino UNO R3 to drive the circuit with ten switches and two pushbuttons.

[Start a local workspace](docs/LOCAL_WORKSPACE.md) ·
[Wire the hardware](docs/WIRING_AND_PROGRAMMING.md) ·
[Generate a circuit](docs/HDL_PIPELINE.md) ·
[Copy a world](docs/WORLD_BACKUPS.md)

## Choose your starting point

| I want to… | Start here |
|---|---|
| Build and test on my own computer | [Local workspace](docs/LOCAL_WORKSPACE.md) |
| Program the FPGA and Arduino | [Wiring and programming](docs/WIRING_AND_PROGRAMMING.md) |
| Convert my HDL into blocks | [HDL pipeline reference](docs/HDL_PIPELINE.md) |
| Try the supplied ALU, muxes, or gates | [Minecraft build functions](minecraft/README.md) |
| Share my existing builds and input bindings | [World backups](docs/WORLD_BACKUPS.md) |
| Contribute with the team | [Contribution guide](CONTRIBUTING.md) |

## Run your own world

Each teammate runs an independent **Minecraft Java 26.3** workspace and joins
**localhost**. No public server, Playit, router changes, or client mods are needed.

1. Clone this repository or download and extract its ZIP.
2. Install Java 25, Python 3.10+, Quartus Prime Lite with MAX 10 support, and
   Arduino IDE. [Full setup instructions](docs/LOCAL_WORKSPACE.md).
3. Wire and program the devices using [this guide](docs/WIRING_AND_PROGRAMMING.md).
4. Open `hardware_bridge` and run **01_Setup.bat**. Select Java and your Arduino
   COM port. Setup downloads the official server, installs the Python bridge
   dependencies, and generates a private local RCON password.
5. Run **02_Start.bat**, join `localhost`, then type `op YourMinecraftName` in
   your own server console to enable commands.

In Minecraft chat, stand in a clear area and place a circuit:

```mcfunction
/function redstone:and
```

Look at a floor lever to assign a physical input:

```mcfunction
/function bridge:bind/sw0
/function bridge:bind/key0
```

`sw0` through `sw9` control steady states. `key0` and `key1` produce one four-tick
pulse per press, even when held. Bind each control to a different lever.

## Generate a new circuit

Install Yosys separately and the root `requirements.txt` into your generator
Python environment, then run from the repository root:

```text
python hdl_to_minecraft.py examples/Full_Adder.sv --top Full_Adder --output build/full_adder.json --mcfunction build/full_adder.mcfunction
```

Copy the generated function into your running world's redstone datapack and
run `/reload`. The [pipeline reference](docs/HDL_PIPELINE.md) covers supported
cells, placement, routing, shared clocks, examples, and validation.

## Where everything lives

| Location | Purpose |
|---|---|
| `hdl_to_minecraft.py` | HDL synthesis, netlist conversion, placement and routing |
| `gate_templates.py` | Minecraft gate and register block templates |
| `examples/` | Circuit sources ready for the pipeline |
| `hardware_bridge/quartus/` | DE10-Lite project and pin assignments |
| `hardware_bridge/SwitchReader12/` | UNO sketch: ten switches and two buttons |
| `hardware_bridge/bridge_practical.py` | USB serial to local Minecraft input bridge |
| `hardware_bridge/bridge_controls/` | Persistent input bindings and button pulses |
| `hardware_bridge/tools/` | Per-computer setup and launch helpers |
| `minecraft/snapshots/redstone.zip` | Supplied generated build-function snapshot |
| `docs/` | Setup, hardware, generator reference and world backups |
| `tests/` | Existing pipeline regression tests |
| `hardware_bridge/tests/` | Hardware protocol and local-setup tests |
| `DEMO/`, `seq/`, `quartus/`, `2+ input gates/`, `complex_comb_logic/` | Existing team HDL, Quartus work and reference material |

Your private world, configuration, server downloads and logs are created under
`hardware_bridge/runtime/` and ignored by Git. Reusable source files stay in
this repository. No world save, accepted EULA or RCON password is committed.

## Current scope

The hardware path has been exercised with physical switches/buttons. The
controls datapack passed twenty live pulse checks; protocol and setup tests
are included. The Windows setup/launch scripts still need a first full run
on a teammate's Windows machine.

HDL placement and routing remain experimental: verify generated circuits in
Minecraft, including timing. The vanilla input bridge is intended for the tested
floor-lever layouts and does not fix every mounting-block update case.
Included build functions are an earlier supplied snapshot; they are not a fresh
export of the latest generator and do not contain the host's current world.
