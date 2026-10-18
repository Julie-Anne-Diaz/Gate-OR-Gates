# Wire and program the devices

Unplug both boards before changing wires. Keep each board powered by its own
USB connection when in use. All signals below flow from FPGA outputs to UNO
inputs. Use common ground; do not connect 5 V Arduino outputs to FPGA GPIO.

| Control | FC-40P label | JP1 physical pin | UNO input |
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
| KEY1 | AA15 | 14 | A0 (digital input) |
| Common ground | GND | 12 or 30 | GND |

JP1 pin **11 is 5 V**, and pin **29 is 3.3 V**. Neither connects to an Arduino
power rail in this setup. The new button signals are pins **13 and 14**, not
11 and 12. A0 is not D0. D0/D1 remain unused for USB serial.
Pin mappings: [Terasic manual](https://fpgacademy.org/Downloads/DE10_Lite_User_Manual.pdf).

## Quartus

1. Open **File → Open Project** and select
   `hardware_bridge/quartus/switch_bridge.qpf`. Keep its `.sv` and `.qsf` beside it.
2. **Assignments → Device:** confirm **10M50DAF484C7G**.
3. The project already assigns all pins. Ten SW/LEDR signals and twelve GPIO
   outputs are defined; the two KEY inputs use their Schmitt trigger standard.
4. **Processing → Start Compilation**. Wait for success.
5. Connect the DE10-Lite USB-Blaster to the PC.
6. **Tools → Programmer → Hardware Setup:** select USB-Blaster, then Close.
7. Select **JTAG**. Add/Change File to this project's newly generated
   `hardware_bridge/quartus/output_files/switch_bridge.sof`.
8. Check **Program/Configure**, click **Start**, wait for **100% Successful**.
9. Verify each SW0..SW9 controls its matching onboard LED. KEY inputs are sent
   through GPIO; the design converts pressed buttons into HIGH levels for UNO.

Reload the `.sof` after DE10 power loss. The included project is source, so each
teammate compiles it using their installed Quartus MAX 10 device support.

## Arduino

1. Stop Python and close Serial Monitor/Plotter so COM is free.
2. Open `hardware_bridge/SwitchReader12/SwitchReader12.ino` in Arduino IDE.
3. Select **Arduino Uno** and the board's actual COM port, then **Upload**.
4. Optional test: open Serial Monitor at **115200 baud**. With all switches off:

   ```text
   V2 0 0 0
   ```

   The first value is the ten switch bits in hex (`0`..`3FF`). The last two are
   decimal KEY0/KEY1 press counters. Press once: one increment; hold: no repeats;
   release and press again: another increment. Each key debounces for 15 ms.
5. Close Serial Monitor before running the bridge. The sketch remains in UNO
   memory after power loss. All twelve signal inputs must be wired; an unconnected
   input can float and produce false changes.

Follow LOCAL_WORKSPACE.md to set up the local server and bind inputs. Never assign a
button and a switch to the same lever.
