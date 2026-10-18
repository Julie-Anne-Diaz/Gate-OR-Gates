DE10 BUTTON PULSES — ten switches + KEY0 and KEY1, Minecraft Java 26.3

WHAT IT DOES
SW0..SW9 keep controlling steady lever states as before.
Each KEY0 or KEY1 press generates one ON pulse lasting 4 Minecraft game ticks
(about 0.2 seconds at normal 20 TPS), then switches its lever OFF. Holding the
physical button does not repeat. Release and press again for another pulse.
Rapid repeated presses queue separate pulses with a one-tick OFF gap; each key
has its own queue (up to 32 pending presses). Delayed input does not replay more
than 32 events per key per serial packet. Presses during disconnect/startup are
not replayed. Both keys can operate different levers simultaneously.

Minecraft schedules OFF, not Python: stopping the bridge after starting a pulse
does not prevent its scheduled end while the server keeps ticking. A paused or
lagging server stretches wall-clock time. If the target chunk unloads, OFF retries
when it loads again. A /reload or server restart clears pending presses and ends
any saved active pulse as soon as the target chunk is loaded.

This uses your existing vanilla server and /setblock approach for the floor-lever
circuits you already tested. It does not install or require Fabric or a mod.
The previously discussed command-update limitation for redstone powered through
mounting blocks is not changed by this upgrade; wall-lever support is separate.

1 — STOP BRIDGE, BACK UP FILES
Stop the current Python bridge with Ctrl+C; answer Y if asked to terminate batch.
Keep backups of your current Quartus project, Arduino sketch, bridge_practical.py,
and bridge_controls datapack. Keep your working redstone gate datapack untouched.

2 — ADD TWO WIRES (WITH BOTH BOARDS UNPLUGGED)
Keep all ten switch wires and your existing common GND.
New connection for KEY0: FC-40P W5 (JP1 physical pin 13, GPIO[10]) -> UNO D12.
New connection for KEY1: FC-40P AA15 (JP1 physical pin 14, GPIO[11]) -> UNO A0.
A0 is used as a DIGITAL input; this is the Arduino's A0, not D0.
JP1 pins 11 and 12 are NOT the new signals: 11 is 5 V and 12 is GND.
No FPGA/Arduino power-rail connection. Do not enable UNO pullups. The signal
flow stays FPGA outputs -> UNO inputs. Both boards use their own USB power.
Reconnect USB after wiring. The DE10 loses its loaded .sof when unplugged.

3 — QUARTUS
Open this package's quartus/switch_bridge.qpf (keep its .qsf and .sv beside it).
It preserves SW[9:0] and LEDR[9:0], adds KEY[1:0] and expands GPIO to [11:0].
KEY0 is FPGA pin B8, KEY1 is A7, using 3.3 V SCHMITT TRIGGER input standard.
The design inverts the active-low KEY inputs so UNO sees HIGH when pressed.
Run Processing > Start Compilation. Then Tools > Programmer, USB-Blaster,
JTAG, select this project's output_files/switch_bridge.sof, Program/Configure,
Start. Verify the ten slide switches still control their ten onboard LEDs.
Reload this new .sof after every FPGA power cycle.

4 — ARDUINO
Open SwitchReader12/SwitchReader12.ino. Choose Arduino UNO and COM10; upload.
The bridge and Serial Monitor must be closed during upload.
For an optional serial test, open Serial Monitor at 115200 baud. You will see:
V2 000 0 0
Fields: V2, ten switch bits as HEX (000..3FF), KEY0 press count, KEY1 press count.
Press KEY0 once: its count increases once. Hold it: count should not increase.
Release and press again: count increases once more. KEY1 has a separate count.
Close Serial Monitor before running Python.

5 — DATAPACK AND PYTHON
Copy bridge_practical.py and start_bridge.bat into:
%USERPROFILE%\Documents\MinecraftBridge
Replace the previous bridge_practical.py; keep the existing .venv folder.
Replace the EXISTING bridge_controls folder in:
%USERPROFILE%\Documents\MinecraftBridge\world\datapacks
with this package's bridge_controls folder. Do not install it alongside a second
copy of the old controls pack. Do not replace/delete your redstone gate pack.
Your existing SW0..SW9 bindings live in world storage and remain saved.
In Minecraft chat as an operator: /reload
Double-click start_bridge.bat and enter your existing RCON password.
The script checks for the updated pulse datapack before reading COM10.
It supports the old ten-switch serial format temporarily, but button pulses
require the new Arduino sketch and two wires.

6 — BIND BUTTONS AND TEST
Look at a separate floor lever and run:
/function bridge:bind/key0
Look at another floor lever and run:
/function bridge:bind/key1
Binding a button sets that lever OFF as its idle state.
Press KEY0: assigned lever ON for four ticks, then OFF even while held.
Release, then press again for another pulse. Repeat for KEY1.
Do NOT assign a slide switch and a button (or both buttons) to the same lever;
they would fight over its state. Use a distinct lever for each hardware input.
SW binding commands remain /function bridge:bind/sw0 through sw9.
Alternative button commands:
/function bridge:stand/key0       (stand directly on lever)
/function bridge:unbind/key0      (remove assignment)
/data get storage bridge:bindings (inspect all saved assignments)

Optional manual pulse test, even without hardware:
/function bridge:pulse/key0
/function bridge:pulse/key1
If this works but physical buttons don't, inspect the V2 counts in Serial Monitor
with Python stopped, then recheck FPGA programming, W5/D12 and AA15/A0 wires.

NOTES
Only one program can use COM10 at a time. No extra Python packages are needed.
The Arduino debounces keys for 15 ms; taps shorter than this are ignored.
The serial reader sends cumulative press counts so a slow PC poll doesn't lose
normal short presses after the bridge has received its first counter snapshot.
Keep the circuit nearby/loaded for predictable visible timing.
No passwords, world saves or user-specific secrets are included in this ZIP.

PIN SOURCES
Terasic DE10-Lite manual, Tables 3-3, 3-4, 3-5 and 3-7:
https://fpgacademy.org/Downloads/DE10_Lite_User_Manual.pdf

See VALIDATION.txt for checks performed and limitations.
