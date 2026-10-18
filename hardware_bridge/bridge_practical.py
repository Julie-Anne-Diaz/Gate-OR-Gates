"""Ten switch inputs and two fixed-pulse DE10 buttons; vanilla Minecraft 26.3."""
import getpass
import os
import re
import time
import serial
from mcrcon import MCRcon

PORT = os.environ.get("DE10_SERIAL_PORT", "COM10")
RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
MAX_REPLAY = 32

def parse_binding(text):
    values = {}
    for key in ("x", "y", "z"):
        m = re.search(r'\b' + key + r'\s*:\s*(-?\d+)\b', text)
        if not m:
            return None
        values[key] = int(m.group(1))
    for key, allowed in {
        "dimension": {"minecraft:overworld", "minecraft:the_nether", "minecraft:the_end"},
        "face": {"floor", "wall", "ceiling"},
        "facing": {"north", "south", "east", "west"},
    }.items():
        m = re.search(r'\b' + key + r'\s*:\s*"([a-z_:]+)"', text)
        if not m or m.group(1) not in allowed:
            return None
        values[key] = m.group(1)
    return values

def make_command(b, powered):
    xyz = f"{b['x']} {b['y']} {b['z']}"
    state = f"face={b['face']},facing={b['facing']},powered={str(powered).lower()}"
    return (f"execute in {b['dimension']} if block {xyz} minecraft:lever "
            f"unless block {xyz} minecraft:lever[powered={str(powered).lower()}] "
            f"run setblock {xyz} minecraft:lever[{state}] replace")

def parse_frame(line):
    fields = line.split()
    if len(fields) == 4 and fields[0] == "V2":
        try:
            switches = int(fields[1], 16)
            counts = (int(fields[2], 10), int(fields[3], 10))
        except ValueError:
            return None
        if 0 <= switches <= 1023 and all(0 <= c <= 0xFFFFFFFF for c in counts):
            return switches, counts
    # Existing ten-switch sketch remains usable while upgrading hardware.
    elif len(fields) == 1:
        try:
            switches = int(fields[0], 16)
        except ValueError:
            return None
        if 0 <= switches <= 1023:
            return switches, None
    return None


def press_deltas(previous, current):
    if previous is None:
        return (0, 0)
    deltas = tuple((c-p) & 0xFFFFFFFF for p, c in zip(previous, current))
    # A reboot/reset or stale backlog should not generate a burst of pulses.
    return tuple(d if d <= MAX_REPLAY else 0 for d in deltas)


def main():
    password = os.environ.get("DE10_RCON_PASSWORD") or getpass.getpass("RCON password: ")
    print("Close Serial Monitor. Ctrl+C stops the bridge.")
    while True:
        try:
            with MCRcon(RCON_HOST, password, port=RCON_PORT, timeout=5) as mc:
                meta = mc.command("data get storage bridge:meta pulse_version")
                if not re.search(r"(?<![0-9])2(?![0-9])", meta):
                    raise RuntimeError("Install the new bridge_controls datapack and run /reload first. " + meta)
                with serial.Serial(PORT, 115200, timeout=0.05) as device:
                    time.sleep(2)
                    print("Connected. SW0..9 control levels; KEY0/KEY1 generate four-tick pulses.")
                    bindings = [None] * 10
                    value = None
                    last_counts = None
                    protocol_notice = False
                    refresh = sync = 0
                    while True:
                        now = time.monotonic()
                        if now >= refresh:
                            for bit in range(10):
                                binding = parse_binding(mc.command(f"data get storage bridge:bindings sw{bit}"))
                                if binding != bindings[bit]:
                                    print(f"SW{bit}: {binding if binding else 'unbound'}")
                                    bindings[bit] = binding
                                    sync = 0
                            refresh = now + 1
                        line = device.readline().decode("ascii", errors="ignore").strip()
                        frame = parse_frame(line) if line else None
                        if frame:
                            switches, counts = frame
                            if switches != value:
                                value = switches
                                sync = 0
                                print(f"SW9..SW0: {value:010b}")
                            if counts is not None:
                                if not protocol_notice:
                                    print("V2 button reader detected. Release buttons, then press to test.")
                                    protocol_notice = True
                                deltas = press_deltas(last_counts, counts)
                                last_counts = counts
                                for key, count in enumerate(deltas):
                                    for _ in range(count):
                                        mc.command(f"function bridge:pulse/key{key}")
                                        print(f"KEY{key}: pulse requested (bind with /function bridge:bind/key{key})")
                            elif not protocol_notice:
                                print("Old Arduino sketch detected: switches work; upload SwitchReader12 for buttons.")
                                protocol_notice = True
                        if value is not None and now >= sync:
                            for bit, binding in enumerate(bindings):
                                if binding:
                                    mc.command(make_command(binding, bool(value & (1 << bit))))
                            sync = now + 1
        except (OSError, serial.SerialException, ConnectionError) as exc:
            print(f"Connection lost: {exc}. Retrying in 3 seconds...")
            time.sleep(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBridge stopped. Minecraft finishes any active pulse.")
    except Exception as exc:
        print(f"Bridge stopped: {exc}")
