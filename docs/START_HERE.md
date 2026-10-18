# Start here: from a fresh PC to physical Minecraft controls

Follow these steps in order on **Windows 10/11, 64-bit**. Each teammate gets their
own world and joins **localhost** on their own computer. No public hosting,
Playit, Minecraft mods, or connection to another teammate's PC is needed.

You will finish with **ten DE10-Lite switches controlling Minecraft levers** and
**KEY0/KEY1 creating short pulses**. The same world also has functions that place
your gates, muxes, full adder and ALU.

## 1. Download this project

1. On the repository page, click **Code → Download ZIP**. If the setup PR has not
   been merged, first select the **codex/de10-hardware-bridge** branch.
2. Right-click the downloaded ZIP → **Extract All**.
3. Move the extracted folder somewhere easy to find, such as Documents. You may
   rename it **Gate-OR-Gates**. Do not run the project while it is still in the ZIP.
4. Keep the folders together. In particular, do not move `hardware_bridge`
   away from `minecraft`: setup needs both.

All paths below start inside this project folder.

## 2. Install the software

| Install | Version / selection | Download |
|---|---|---|
| Minecraft Launcher | Use **Minecraft: Java Edition 26.3**, not Bedrock | [Minecraft](https://www.minecraft.net/download/) |
| Eclipse Temurin Java | **JDK 25**, Windows x64, MSI installer | [Java 25](https://adoptium.net/temurin/releases/?version=25) |
| Python | **Python 3.12 or 3.13**, Windows 64-bit, normal installer | [Python](https://www.python.org/downloads/windows/) |
| Quartus Prime Lite | **25.1**, with **MAX 10 FPGA device support** | [Quartus Lite 25.1](https://www.altera.com/downloads/fpga-development-tools/quartus-prime-lite-edition-design-software-version-25-1-windows) |
| Arduino IDE | **IDE 2.x** | [Arduino](https://www.arduino.cc/en/software/) |

During Java installation, enable **Add to PATH** and, if offered, **JAVA_HOME**.
During Python installation, enable **Add python.exe to PATH** and leave **pip**
selected. Use the normal Python installer, not the embeddable ZIP. The project
also supports an existing Python 3.10+ environment, but standard Windows Python
is the simplest choice for a fresh PC.

Quartus Lite needs MAX 10 support for this board. You do not need Questa or an
extra paid Quartus edition for these steps. Install any selected device package
using the same Quartus 25.1 installer/version.

After installing, open a **new Windows Command Prompt** (Start → type `cmd`) and
run these separately:

```bat
java -version
```

```bat
python --version
```

Java should report **25**. Python should report the version you installed. If
Java still reports 8, setup can use the full path to Java 25's `bin\java.exe`;
you do not need to uninstall your older Java to continue.

## 3. Select Minecraft Java 26.3

1. Open Minecraft Launcher and sign in with your own Minecraft account.
2. Select **Minecraft: Java Edition → Installations → New installation**.
3. Name it **Gate-OR-Gates** and select **release 26.3**.
4. Create/install that profile, then select it before playing.

Use exactly **26.3** for both client and the bundled server setup. Minecraft
Launcher manages the client runtime; the Java 25 installed above runs the
separate local server.

## 4. Wire the DE10-Lite to the UNO

You need a **DE10-Lite**, an **Arduino/Elegoo UNO R3**, signal jumper wires, and
a common ground. Both boards connect to the PC using their own USB cables.

**Unplug both boards before connecting wires.** Use the FC-40P breakout labels
in this table; breadboard row numbers are not FPGA pin labels.

| DE10 control | FC-40P label | JP1 physical pin | UNO pin |
|---|---|---:|---|
| SW0 | V10 | 1 | D2 |
| SW1 | W10 | 2 | D3 |
| SW2 | V9 | 3 | D4 |
| SW3 | W9 | 4 | D5 |
| SW4 | V8 | 5 | D6 |
| SW5 | W8 | 6 | D7 |
| SW6 | V7 | 7 | D8 |
| SW7 | W7 | 8 | D9 |
| SW8 | W6 | 9 | D10 |
| SW9 | V5 | 10 | D11 |
| KEY0 | W5 | 13 | D12 |
| KEY1 | AA15 | 14 | A0 |
| Common ground | GND | 12 or 30 | GND |

A0 is used as a digital input; it is **not D0**. Leave UNO D0/D1 free.
JP1 **pin 11 is 5 V** and **pin 29 is 3.3 V**: do not connect either to Arduino
power rails. The signal direction is **FPGA outputs → UNO inputs**.

Reconnect both USB cables after wiring. Program the FPGA next: unplugging it
later removes its loaded configuration.

## 5. Program the FPGA in Quartus

1. Open Quartus → **File → Open Project**.
2. Select **hardware_bridge/quartus/switch_bridge.qpf**. Keep its `.qsf` and `.sv`
   files in the same folder. Close/save another project if prompted.
3. Open **Assignments → Device** and confirm **10M50DAF484C7G**. Click OK.
4. Click **Processing → Start Compilation**. Wait for successful compilation.
   The project already contains the pin assignments; no manual entry is needed.
5. Open **Tools → Programmer**.
6. Click **Hardware Setup**, select **USB-Blaster**, then **Close**.
7. Set **Mode: JTAG**. Use **Add File** if no file is listed, or **Change File**
   on the existing row, and select this project's newly generated file:

   ```text
   hardware_bridge/quartus/output_files/switch_bridge.sof
   ```

8. Check **Program/Configure**, click **Start**, and wait for **100% Successful**.
9. Flip SW0 through SW9. Each matching red onboard LED should follow its switch.

If USB-Blaster is missing, first check the DE10's USB-Blaster cable/power. In
Windows Device Manager, install/update the USB-Blaster driver from your Quartus
installation's `quartus/drivers` folder, including subfolders, then reopen
Hardware Setup. See the [hardware reference](WIRING_AND_PROGRAMMING.md).

The `.sof` must be loaded again whenever the DE10 loses power. UNO programming,
on the other hand, survives unplugging.

## 6. Program and check the Arduino

1. Open **hardware_bridge/SwitchReader12/SwitchReader12.ino** in Arduino IDE.
2. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**. If that package
   is missing, install **Arduino AVR Boards** in Boards Manager.
3. Select the UNO under **Tools → Port**. Note its COM number for setup later.
   It may be COM3, COM10, etc.; do not assume everyone uses COM10.
4. Click **Upload** (right-arrow button) and wait for upload success.
5. Open **Serial Monitor**, set **115200 baud**, and inspect the messages.
   With all switches off, a fresh Arduino starts with something like:

   ```text
   V2 0 0 0
   ```

   The first value is the ten switches in hexadecimal (`0` through `3FF`).
   The last two values count KEY0 and KEY1 presses. Press KEY0: its count
   increases once. Keep holding it: no repeats. Release/press again: another
   increment. Test KEY1 too.
6. **Close Serial Monitor before continuing.** Only one program can use the
   Arduino COM port. If upload says Access denied, stop any running Python
   bridge and close Serial Monitor/Plotter before retrying.

All twelve signal wires and ground must be connected; floating inputs can
produce false values. Keep the successfully programmed boards connected.

## 7. Check the redstone builder files

Your team puts generated **`.mcfunction`** files here:

```text
minecraft/datapacks/redstone/data/redstone/function/
```

`pack.mcmeta` is already provided at `minecraft/datapacks/redstone/pack.mcmeta`.
Keep any helper functions/tags needed by the current complete builder pack.
Do not rename the namespace folder to `redstne`, use `.mc`, or let Windows save
files as `.mcfunction.txt`.

If the team has not added functions there yet, setup automatically uses the
included older snapshot of gates, muxes, full adder and ALU. Once functions exist
in the source folder, setup installs that complete folder instead.

The builder and `bridge_controls` are **separate packs**. Setup installs both
side by side; there is no need to manually construct another datapack.

## 8. Create your local server automatically

1. Stop any other Minecraft server using ports 25565/25575. Close Serial Monitor.
2. In File Explorer, open **hardware_bridge**.
3. Double-click **01_Setup.bat**.
4. At the Java prompt, press Enter if the displayed Java is version 25.
   Otherwise paste the full path to Java 25's `java.exe`. For Temurin it is
   normally inside `C:\Program Files\Eclipse Adoptium\<your JDK folder>\bin`.
5. Open/read the linked Minecraft EULA. Type **YES** only if you agree.
6. Setup creates a private Python environment and installs the bridge packages.
7. At the serial-port prompt, enter the COM port you noted in Arduino IDE.
8. At the memory prompt, press Enter for the default **2 GB**. You can choose
   more if your PC has room, while leaving RAM for Windows and Minecraft.
9. Wait for **Setup complete**.

This step downloads the official Minecraft 26.3 server and creates its
`server.properties`, a random local RCON password, the accepted EULA file,
a creative flat-world folder, and both installed datapacks. **You do not need
to download server.jar manually, edit server.properties, or invent/share a
password.** The bridge reads your locally generated password automatically.

Your resulting world packs are:

| Folder | Job |
|---|---|
| `hardware_bridge/runtime/world/datapacks/redstone/` | Places gates and circuits |
| `hardware_bridge/runtime/world/datapacks/bridge_controls/` | Binds physical inputs and runs pulses |

The server listens only on your own computer. No router/firewall port forwarding
or Playit setup is needed. Keep the generated `runtime` folder out of Git.

## 9. Start the server and bridge

1. With both devices connected/programmed and Serial Monitor closed,
   double-click **hardware_bridge/02_Start.bat**.
2. A **server window** opens. Wait for startup and world generation.
3. The launcher then opens a **Python bridge window**. Keep both windows open.
4. The bridge should report that it connected and detected the V2 reader.

If the server is already running and only the bridge stopped, use
**03_Restart_bridge.bat** instead. Do not run two bridges or two servers on the
same ports. The launch scripts target Windows; the complete launcher flow still
needs a first end-to-end check on each teammate's machine.

## 10. Join your world and enable commands

1. Launch your **Minecraft Java 26.3** profile.
2. Click **Multiplayer → Direct Connection**.
3. Enter **localhost**, then **Join Server**.
4. Find your **server window**. Type the following there, without a slash,
   replacing the name with your actual Minecraft username:

   ```text
   op YourMinecraftUsername
   ```

5. Back in Minecraft chat, run:

   ```mcfunction
   /gamemode creative
   /time set day
   /reload
   /datapack list enabled
   ```

Both packs should be enabled. The new world is intentionally empty until you
place circuits. **Multiplayer → localhost is your private local world**, not a
connection to another person's machine.

| Where you type | What belongs there |
|---|---|
| Server window | `op YourName`, `stop` — no slash |
| Minecraft chat | `/function ...`, `/reload`, `/gamemode ...` |
| Windows Command Prompt | `java -version`, `python --version` |
| Python bridge window | Watch input messages; Ctrl+C stops it |

## 11. Place a circuit and bind switches

1. Stand on the ground in a clear empty area. Run in **Minecraft chat**:

   ```mcfunction
   /function redstone:and
   ```

2. Wait for the gate to finish placing.
3. Look directly at its first floor-mounted input lever, within six blocks:

   ```mcfunction
   /function bridge:bind/sw0
   ```

4. Look at its other input lever:

   ```mcfunction
   /function bridge:bind/sw1
   ```

5. Flip physical SW0 and SW1. The assigned Minecraft levers should follow them.
   Check the gate with all input combinations, allowing redstone to settle.
6. Assign other controls the same way using `sw2` through `sw9`. Each physical
   control needs a separate lever. Bindings are saved with the world.

If the current team builder uses different names, type `/function redstone:`
and use autocomplete to see available functions. A file `alu.mcfunction`
creates `/function redstone:alu`; the extension is omitted in commands.

## 12. Bind the two pulse buttons

1. Place or choose two separate floor levers. Do not use levers already bound
   to slide switches or the other button.
2. Look at one and run:

   ```mcfunction
   /function bridge:bind/key0
   ```

3. Look at the other and run:

   ```mcfunction
   /function bridge:bind/key1
   ```

4. Press physical KEY0. Its lever turns ON for **four Minecraft game ticks**,
   about **0.2 seconds** at normal speed, then OFF even if you hold the button.
5. Release and press again for another pulse. Test KEY1 too.

For a manual check without pressing hardware, use `/function bridge:pulse/key0`.
Quick presses queue separate pulses with a one-tick OFF gap. Paused or lagging
servers stretch real time. Use these for circuit inputs that are meant to pulse.

To change an assignment, look at a different lever and run its bind command
again. To remove one: `/function bridge:unbind/key0` (or the relevant input).

## 13. Place larger circuits, including the ALU

Use a separate large empty area for each build. Examples in the bundled snapshot:

```mcfunction
/function redstone:test_all_gates
/function redstone:full_adder
/function redstone:mux_2
/function redstone:mux_4
/function redstone:alu_compact
```

Commands replace blocks, generally extending east (+X) and south (+Z) from your
aligned feet, regardless of where you look. Stay on the floor. Large circuits
can take time to place and settle; keep their chunks loaded. Assign the input
levers you want to control, and check each circuit's behavior. A new export may
change lever positions, so rebuilding can require rebinding.

The supplied functions are an earlier snapshot, not the host's existing built
world or a guarantee of every generated circuit's timing. For your exact current
world, follow [WORLD_BACKUPS.md](WORLD_BACKUPS.md). The current vanilla bridge is
for the floor-lever layouts already tested; mounting-block update limitations
remain documented in the [builder guide](REDSTONE_BUILDER.md).

## 14. Stop safely and use it again tomorrow

To stop:

1. In the bridge window press **Ctrl+C**. Answer **Y** if asked to terminate a
   batch job.
2. In the server window type **stop** and wait for world saving to finish.
3. Then disconnect hardware if desired.

Next time:

1. Reconnect the boards. Reload the FPGA `.sof` through Quartus if it lost power.
   You do not need to recompile unchanged code or upload Arduino again.
2. Close Serial Monitor and run **02_Start.bat**.
3. Join **localhost** using Java 26.3. Your builds, bindings, and operator access
   are still saved.

Setup is one-time unless you change COM port/memory or need to repair it.
Rerunning setup preserves your existing world, server properties and datapacks.
It does not overwrite an already installed builder after teammates update Git:
copy the updated complete builder into the runtime world's `datapacks/redstone`
folder, keeping controls alongside it, then `/reload`. Back up before replacing.

## Optional: turn another HDL circuit into a build

Skip this section if you only want the included gates/functions.

1. Install [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build/releases).
   Extract it and open its `start.bat` terminal. Confirm `yosys -V` works.
2. In that terminal, change to this repository's root folder. For example, if
   you placed and named it as described in step 1:

   ```bat
   cd /d "%USERPROFILE%\Documents\Gate-OR-Gates"
   ```

3. With standard Windows Python, install the generator dependency using the
   environment setup already created:

   ```bat
   "hardware_bridge\.venv\Scripts\python.exe" -m pip install -r requirements.txt
   ```

   If your existing Python uses MSYS2's venv layout, substitute `bin` for
   `Scripts` in these interpreter paths.
4. Generate the supplied full adder:

   ```bat
   "hardware_bridge\.venv\Scripts\python.exe" hdl_to_minecraft.py examples/Full_Adder.sv --top Full_Adder --output build/full_adder.json --mcfunction build/full_adder.mcfunction
   ```

5. Copy `build/full_adder.mcfunction` into:

   ```text
   hardware_bridge/runtime/world/datapacks/redstone/data/redstone/function/
   ```

6. In Minecraft chat: `/reload`, then `/function redstone:full_adder` in a new
   empty area. Use your own synthesizable HDL instead of the example when ready;
   do not pass a testbench as a design source.

[HDL_PIPELINE.md](HDL_PIPELINE.md) has the full generator options and supported
circuits. Root requirements are for generation; hardware requirements are for
serial/RCON. Installing the generator is not needed to run existing functions.

## If something fails

| Message/problem | Fix |
|---|---|
| `python` not recognized or opens the Store | Install normal Windows Python with PATH enabled; reopen the terminal |
| Java class-file error / Java 8 selected | Rerun setup with Java 25's full `java.exe` path |
| USB-Blaster not listed | Check the DE10 USB connection and install its Quartus driver |
| Cannot find `.sof` | Run full compilation; select this project's `output_files` folder |
| UNO upload Access denied | Stop Python and close Serial Monitor/Plotter; retry upload |
| COM port missing | Reconnect UNO and check Tools → Port; rerun setup if COM changed |
| Old Arduino sketch detected | Upload **SwitchReader12**, not an older SwitchReader10 sketch |
| Unknown function | Check pack structure and namespace, `/reload`, then the server log |
| Commands denied | `op YourName` in the server console, not chat |
| Another server is using the ports | Stop the old server; use Restart bridge if this workspace is already running |
| Switches work, buttons do not | Inspect V2 press counters, new FPGA `.sof`, W5/D12 and AA15/A0 wires |
| Lever moves but redstone through its support does not | Known vanilla command-update limitation; use the tested floor-lever layout |
| ALU seems slow | `/tick query` checks server cost; 20 TPS allows 50 ms/tick. FPS is a separate client issue |

For a server startup failure, read **hardware_bridge/runtime/logs/latest.log**.
Do not share `runtime/server.properties`: it contains your local RCON password.

## Official installation references

- [Minecraft Launcher installations](https://help.minecraft.net/hc/en-us/articles/23431114561037-Troubleshooting-Launching-Minecraft-from-the-Minecraft-Launcher)
- [Temurin Windows installer options](https://adoptium.net/installation/windows)
- [Python Windows installation](https://docs.python.org/3.12/using/windows.html)
- [Arduino board/port selection](https://support.arduino.cc/hc/en-us/articles/4406856349970-Select-board-and-port-in-Arduino-IDE)
- [DE10-Lite manual and pin tables](https://fpgacademy.org/Downloads/DE10_Lite_User_Manual.pdf)
