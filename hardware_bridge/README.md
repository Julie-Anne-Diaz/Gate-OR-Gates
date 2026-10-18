# Physical DE10 inputs for Minecraft

This folder connects a **DE10-Lite** to an **Arduino UNO R3** over GPIO, then to a
**Minecraft Java 26.3** dedicated server over USB serial and local RCON. Ten slide
switches control steady lever states. KEY0 and KEY1 generate fixed four-tick
pulses (about 0.2 seconds at normal server speed) without repeating while held.

The host's physical inputs are shared by everyone watching the same live world.
Visitors do not need an FPGA, Arduino, Python, Yosys, Fabric, or client mods.
They need Minecraft Java 26.3 and the host's server address.

## Join the live demo

Ask the host for the Playit server address. In Minecraft Java 26.3, open
**Multiplayer → Add Server**, paste the full supplied address (including a port
if present), then join. Your own `localhost` points to your own computer, not the
host's. Ask to be whitelisted if the server requires it.

## Reproduce the hardware setup

Use [READ_ME.txt](READ_ME.txt) for the complete wiring, Quartus, Arduino, and
installation walkthrough. All twelve GPIO signals go **from the FPGA to UNO
inputs**, with common ground; do not drive FPGA pins from UNO 5 V outputs.

| Control | FPGA input pin | FC-40P output label | JP1 physical pin | UNO input |
|---|---|---|---:|---|
| SW0 | C10 | V10 | 1 | D2 |
| SW1 | C11 | W10 | 2 | D3 |
| SW2 | D12 | V9 | 3 | D4 |
| SW3 | C12 | W9 | 4 | D5 |
| SW4 | A12 | V8 | 5 | D6 |
| SW5 | B12 | W8 | 6 | D7 |
| SW6 | A13 | V7 | 7 | D8 |
| SW7 | A14 | W7 | 8 | D9 |
| SW8 | B14 | W6 | 9 | D10 |
| SW9 | F15 | V5 | 10 | D11 |
| KEY0 | B8 | W5 | 13 | D12 |
| KEY1 | A7 | AA15 | 14 | A0 (digital input) |

JP1 pin 12 or 30 provides common GND. Pin 11 is **5 V**, and pin 29 is **3.3 V**;
neither is a signal or an Arduino power connection. Disconnect both boards before
changing wires. The FPGA design inverts the active-low physical buttons.

1. Compile `quartus/switch_bridge.qpf` in Quartus and program its generated
   `output_files/switch_bridge.sof`. Reload it after FPGA power loss.
2. Upload `SwitchReader12/SwitchReader12.ino` to UNO. Select your actual COM port.
3. Run `setup_python.bat` or create a Python virtual environment and install
   `requirements.txt`. Both standard Windows `Scripts` and MSYS2 `bin` venv
   layouts are supported by `start_bridge.bat`.
4. Set `PORT` in `bridge_practical.py` to the UNO's COM port (the demo host uses
   COM10). Close Serial Monitor before starting the bridge.
5. Copy the complete `bridge_controls` folder into the server world's
   `datapacks` folder, replacing an earlier controls pack. Keep your generated
   redstone gate datapack alongside it. Run `/reload` in-game as an operator.
6. Enable local RCON in the server's private `server.properties`, restart the
   server, and run `start_bridge.bat`. The password is requested interactively.

Host-only server properties, merged into your existing file (use your own secret):

```properties
server-ip=127.0.0.1
server-port=25565
enable-rcon=true
rcon.port=25575
rcon.password=CHOOSE_A_PRIVATE_PASSWORD
online-mode=true
```

A vanilla server JAR and Java 25 are installed separately. Keep `server.jar`,
`server.properties`, world, and launch scripts together in the runtime folder.
If copying these files into an existing `MinecraftBridge` runtime, keep its
existing `.venv`, server properties, and world. `start_server.bat` launches the
vanilla server; no modded launcher is needed for this floor-lever workflow.

## Assign inputs in Minecraft

Look at a lever within six blocks and run one of these as an operator:

```mcfunction
/function bridge:bind/sw0
/function bridge:bind/sw9
/function bridge:bind/key0
/function bridge:bind/key1
```

All switch names `sw0` through `sw9` exist. Use a distinct lever for each input.
`bridge:stand/<name>` binds the lever directly under your feet.
`bridge:unbind/<name>` removes an assignment. To inspect saved coordinates:

```mcfunction
/data get storage bridge:bindings
```

Bindings are stored with the world and survive restarts. The two button bindings
start at OFF. Pressing a key queues a four-tick ON pulse followed by OFF, even if
the key stays held. Rapid presses queue separate pulses with a one-tick low gap;
the two keys operate independently. A pulse captures its target so rebinding
mid-pulse still turns the old target off. Minecraft schedules OFF, so the bridge
need not remain running for an already-started pulse to end while the server ticks.
Pending presses are cleared on reload/restart. Offline/startup presses are not
replayed. A paused or lagging server stretches the pulse's real-world duration.

Keep builds loaded/nearby for predictable behavior. This vanilla `/setblock`
bridge is intended for the tested floor-lever circuits; it does not fix the
missing updates for all redstone powered through lever mounting blocks.
Do not claim universal wall-lever support for this package.

For a test without hardware:

```mcfunction
/function bridge:pulse/key0
```

The Arduino serial protocol is `V2 <SW_HEX> <KEY0_COUNT> <KEY1_COUNT>`, with ten
switch bits and decimal 32-bit cumulative press counters. Arduino debounces keys
for 15 ms and sends a heartbeat every 500 ms. The bridge establishes a counter
baseline on connection, handles wraparound, and limits stale event replay.

## Share the live server or a world copy

See [SHARING.md](SHARING.md) for Playit setup, team access, world backups, and
which files to commit. Keep RCON private; teammates join the game port only.

Run the dependency-free protocol tests from this folder:

```text
python -m unittest discover -s tests -v
```

[VALIDATION.txt](VALIDATION.txt) records the live pulse checks and the limits of
host-side hardware simulation. Board pin mappings come from the
[Terasic DE10-Lite manual](https://fpgacademy.org/Downloads/DE10_Lite_User_Manual.pdf).
