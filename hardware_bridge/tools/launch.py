"""Open a private server and hardware bridge in separate Windows consoles."""
import os
import subprocess
import sys
import time
from common import ROOT, RUNTIME, load_config, require_java, private_python, port_open

def main():
    if os.name != 'nt':
        raise RuntimeError('This launcher is for Windows. See START_HERE.md for manual commands.')
    config = load_config()
    require_java(config['java'])
    python = private_python()
    if port_open(25565) or port_open(25575):
        raise RuntimeError('A server is already using these local ports. Stop it, or use 03_Restart_bridge.bat if this starter server is already running.')
    server = subprocess.Popen([config['java'],'-Xms512M',f'-Xmx{config["memory_gb"]}G',
                               '-jar','server.jar','nogui'],cwd=RUNTIME,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
    print('Server window opened. Waiting for its RCON listener...')
    for seconds in range(180):
        if server.poll() is not None:
            raise RuntimeError('Server exited. Check runtime/logs/latest.log.')
        if port_open(25575):
            break
        if seconds and seconds % 15 == 0:
            print('Still waiting for first-world startup...')
        time.sleep(1)
    else:
        raise RuntimeError('Server is taking longer than three minutes. Check its window; once ready, run 03_Restart_bridge.bat.')
    subprocess.Popen([str(python),str(ROOT/'tools/run_bridge.py')],cwd=ROOT,
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    print('Server and bridge windows opened. Keep both running.')
    print('Join localhost using Minecraft JAVA 26.3.')
    print('First time: in the SERVER window type: op YourMinecraftName')
    print('Then use /function redstone:and and /function bridge:bind/sw0 in chat.')
    print('To quit: stop the bridge with Ctrl+C, then type stop in the SERVER window.')

if __name__ == '__main__':
    try:
        main()
    except (Exception,KeyboardInterrupt) as exc:
        print('Launch stopped:',exc)
        sys.exit(1)
