# Local Minecraft workspace

Each teammate runs their own local server and joins `localhost`. The server is
private to that computer; it needs no public address, account with a tunnel
service, router changes, or client mods. The hardware bridge uses local RCON.

## Prerequisites

- Minecraft **Java 26.3**, using your own Minecraft account.
- **Java 25** for the server: [Temurin downloads](https://adoptium.net/temurin/releases/?version=25).
- **Python 3.10+** with venv/pip: [Windows downloads](https://www.python.org/downloads/windows/).
  Enable the Python installer's PATH option; `python --version` should work.
- Quartus Prime Lite with **MAX 10** support and USB-Blaster driver.
- Arduino IDE, DE10-Lite, UNO R3, twelve signal wires, and common ground.

You can use the included Minecraft functions without hardware; the bridge will
need the connected, programmed UNO for physical input. Yosys and OR-Tools are
only needed to generate new circuits, not to place the supplied functions.

## First setup

1. Clone the repository or extract its downloaded ZIP to a writable folder.
2. [Wire and program the devices](WIRING_AND_PROGRAMMING.md).
3. Stop any other local Minecraft server on ports 25565/25575. Close Serial Monitor.
4. Open `hardware_bridge` and double-click **01_Setup.bat**.
5. Select Java 25's `bin/java.exe` if the default Java is older. Setup checks it.
6. Read the linked Minecraft EULA and explicitly type YES only if you agree.
7. Choose the UNO's actual COM port from those listed. Each computer may differ.
8. Choose server memory: default **2 GB**. Leave enough memory for Windows and
   the Minecraft client. More RAM does not fix a CPU-limited redstone simulation.
9. Setup creates `.venv`, downloads and verifies the official Minecraft 26.3
   server, generates a local RCON password and installs both datapacks in a
   fresh creative flat world under `hardware_bridge/runtime/world`.
10. Double-click **02_Start.bat**. It opens the server, waits until ready,
    then opens the bridge. Keep both windows running.
11. Join **Minecraft Java 26.3 → Multiplayer → Direct Connection → localhost**.
12. In the **server console**, without `/`, enter:

    ```text
    op YourMinecraftUsername
    ```

    In Minecraft chat, you can now run:

    ```mcfunction
    /gamemode creative
    /function redstone:and
    /function bridge:bind/sw0
    ```

    Run the bind command while looking at a floor lever within six blocks.
    Use distinct levers for each hardware input. `sw0`..`sw9` are steady inputs;
    `key0` and `key1` are four-tick pulses. Binding a button starts its lever OFF.

All paths in the launch scripts are relative to `hardware_bridge`; you can keep
the repository anywhere. The bridge reads the local password automatically.
The server listens on 127.0.0.1, with the whitelist disabled for local use and
normal Minecraft authentication enabled. Teammates do not connect to one another.

## Daily use

- Reload `hardware_bridge/quartus/output_files/switch_bridge.sof` after the FPGA
  loses power. UNO retains its uploaded sketch.
- Close Serial Monitor, run **02_Start.bat**, and join `localhost`.
- If the server is already running and only Python stopped, use
  **03_Restart_bridge.bat**. Do not start a second server or second bridge.
- To quit, Ctrl+C stops Python; type `stop` in the server console and wait for
  world saving. Do this before copying the world or changing its files.
- Run setup again with the server stopped to change COM or memory settings.
  It preserves existing server properties, world and datapacks.
- Existing source-pack changes are not automatically copied over a customized
  runtime pack. Copy the updated pack manually while preserving your world,
  then run `/reload`. This avoids overwriting a teammate's customized datapack.

## Bindings and pulses

```mcfunction
/function bridge:bind/sw0
/function bridge:bind/sw9
/function bridge:bind/key0
/function bridge:bind/key1
/function bridge:stand/key0
/function bridge:unbind/key0
/data get storage bridge:bindings
```

Assignments are global to this one physical board and saved with this world.
Each button press queues a four-game-tick ON pulse and then OFF, even if held.
Quick repeated presses have a one-tick OFF gap; the two buttons are independent.
Minecraft schedules OFF, so an already-started pulse ends even if Python stops
while the server continues ticking. Rebinding mid-pulse still turns the old
lever off. Reload/restart clears queued presses and cleans up saved active
pulses when their chunks are loaded. Paused/lagging servers stretch real time.
Keep the circuit nearby/loaded for predictable operation.

## Common issues

| Symptom | Action |
|---|---|
| Java class-version error | Rerun setup and select Java 25, not Java 8 |
| COM access denied | Stop Python and close Serial Monitor/Plotter before upload |
| Old Arduino sketch detected | Upload `SwitchReader12/SwitchReader12.ino` |
| Commands unavailable | `op YourName` in your server console |
| Unknown function | Check `runtime/world/datapacks`, then `/reload` |
| Existing server detected | Stop it; use Restart bridge if this workspace is already running |
| Switches work but buttons do not | Check V2 press counters and W5/D12, AA15/A0 wiring |
| Lever moves but mounting-block circuit fails | Known vanilla `/setblock` update limitation; this setup targets tested floor layouts |
| Slow ALU | `/tick query` checks simulation cost; 20 TPS allows 50 ms/tick; FPS is separate |

The double-click launchers target Windows and have not been run on Windows in
this development environment. Tests cover configuration generation and protocol
logic, not a complete driver/Quartus/USB install on another PC.

## Generate more circuits

Follow the [pipeline reference](HDL_PIPELINE.md) from the repository root. Root
`requirements.txt` installs OR-Tools for generation; `hardware_bridge/requirements.txt`
installs only serial/RCON dependencies. Separate environments are fine.
Copy a generated `.mcfunction` into:

```text
hardware_bridge/runtime/world/datapacks/redstone/data/redstone/function/
```

Run `/reload`, then `/function redstone:<filename>` in Minecraft chat from a fresh
empty area. Builds generally extend east/south from aligned player feet; support
blocks go one block lower. The starter flat world's floor differs from the
host's old world, so use the generated coordinates rather than assuming Y=-59.

To start with existing built circuits, see [world backups](WORLD_BACKUPS.md).
