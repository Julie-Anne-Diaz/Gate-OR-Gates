"""Launch the known bridge with this computer's private port/password settings."""
import subprocess
import sys
from common import ROOT, load_config, private_python, bridge_environment, port_open

def main():
    config = load_config()
    if not port_open(25575):
        raise RuntimeError('The local Minecraft server is not ready. Run 02_Start.bat first.')
    print('Using Arduino port:', config['serial_port'])
    print('Close Serial Monitor before continuing. Ctrl+C stops the bridge.')
    return subprocess.call([str(private_python()),str(ROOT/'bridge_practical.py')],
                           env=bridge_environment(config),cwd=ROOT)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\nBridge stopped.')
    except Exception as exc:
        print('Bridge launch stopped:',exc)
        sys.exit(1)
