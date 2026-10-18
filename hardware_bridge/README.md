# Physical inputs and local workspace

Ten DE10-Lite switches control steady Minecraft lever states. KEY0 and KEY1
produce fixed four-tick pulses through an Arduino UNO R3 and the local Python
bridge. Each teammate can run their own independent world on `localhost`.

**Start here:** [the complete from-scratch guide](../docs/START_HERE.md).
It covers Minecraft/Java/Python installation, wiring, Quartus, Arduino, server setup,
and testing all controls in one sequence.

| File or folder | Purpose |
|---|---|
| `01_Setup.bat` | Select Java/COM/RAM, install Python dependencies, download server and install datapacks |
| `02_Start.bat` | Open the local server and bridge in separate consoles |
| `03_Restart_bridge.bat` | Restart only the bridge while the local server is running |
| `quartus/` | Compile and program the DE10-Lite project |
| `SwitchReader12/` | Upload the twelve-input UNO sketch |
| `bridge_practical.py` | Read USB serial and control saved lever assignments |
| `bridge_controls/` | Persistent bindings and queued button pulses |
| `tools/` | Setup, launch and local configuration helpers |
| `tests/` | Protocol and setup checks |

[Wiring and programming](../docs/WIRING_AND_PROGRAMMING.md) ·
[World backups](../docs/WORLD_BACKUPS.md) ·
[Optional shared live session](SHARING.md)

Run tests from this folder:

```text
python -m unittest discover -s tests -v
```

`.venv` and `runtime` are generated locally and ignored by Git. Do not commit
server passwords, world saves, logs, downloaded JARs or accepted EULA files.
Minecraft/Java are downloaded or installed separately under their own terms.
