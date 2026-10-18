"""Interactive per-computer setup. Creates private runtime files, never ships them."""
from pathlib import Path
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import urllib.request
import venv
import zipfile
from common import ROOT, RUNTIME, CONFIG, private_python, require_java, port_open

SERVER_URL = 'https://piston-data.mojang.com/v1/objects/33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c/server.jar'
SERVER_SHA1 = '33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c'
EULA_URL = 'https://aka.ms/MinecraftEULA'

def download_server(path):
    if path.exists() and hashlib.sha1(path.read_bytes()).hexdigest() == SERVER_SHA1:
        print('Minecraft 26.3 server already downloaded and verified.')
        return
    if path.exists():
        raise RuntimeError('An unrecognized server.jar exists. Back it up and remove it before rerunning setup.')
    temp = path.with_suffix('.download')
    print('Downloading the official Minecraft Java 26.3 server (about 62 MB)...')
    try:
        with urllib.request.urlopen(SERVER_URL, timeout=90) as response, temp.open('wb') as output:
            shutil.copyfileobj(response, output)
        if hashlib.sha1(temp.read_bytes()).hexdigest() != SERVER_SHA1:
            raise RuntimeError('Server download checksum mismatch. Run setup again.')
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()

def install_packs(world):
    controls = ROOT/'bridge_controls'
    target = world/'datapacks/bridge_controls'
    if controls.is_dir():
        if target.exists():
            print('Keeping existing datapack: bridge_controls')
        else:
            shutil.copytree(controls, target)
            print('Installed datapack: bridge_controls')
    archive = ROOT.parent/'minecraft/snapshots/redstone.zip'
    target = world/'datapacks/redstone'
    if archive.is_file():
        if target.exists() or target.with_suffix('.zip').exists():
            print('Keeping existing datapack: redstone')
        else:
            with zipfile.ZipFile(archive) as pack:
                for name in pack.namelist():
                    path = Path(name)
                    if path.is_absolute() or '..' in path.parts:
                        raise RuntimeError('Unsafe path in redstone snapshot.')
                pack.extractall(target)
            print('Installed datapack: redstone')


def create_properties(path):
    if path.exists():
        print('Keeping existing server.properties.')
        return
    generator = json.dumps({'biome':'minecraft:plains','layers':[
        {'block':'minecraft:bedrock','height':1},
        {'block':'minecraft:dirt','height':2},
        {'block':'minecraft:grass_block','height':1}]},separators=(',',':'))
    values = {
        'server-ip':'127.0.0.1','server-port':'25565','enable-rcon':'true',
        'rcon.port':'25575','rcon.password':secrets.token_hex(24),
        'broadcast-rcon-to-ops':'false','online-mode':'true','white-list':'false',
        'gamemode':'creative','difficulty':'peaceful','spawn-protection':'0',
        'level-name':'world','level-type':'minecraft:flat','generator-settings':generator,
        'generate-structures':'false','view-distance':'10','simulation-distance':'10',
        'motd':'Gate-OR-Gates local hardware workspace'}
    path.write_text(''.join(f'{key}={value}\n' for key,value in values.items()),encoding='utf-8')

def main():
    if sys.version_info < (3,10):
        raise RuntimeError('Python 3.10 or newer is required.')
    if port_open(25565) or port_open(25575):
        raise RuntimeError('Stop your existing Minecraft server before setting up this separate starter.')
    print('This installs a separate local Minecraft 26.3 workspace in this folder.')
    existing = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
    default_java = existing.get('java') or shutil.which('java') or 'java'
    print('Java 25 is required. Default:', default_java)
    java = input('java.exe path, or Enter to use the default: ').strip().strip('"') or default_java
    require_java(java)
    print('Minecraft EULA:', EULA_URL)
    if input('Have you read and agreed to the Minecraft EULA? Type YES to continue: ').strip().upper() != 'YES':
        print('Setup cancelled. EULA was not accepted.')
        return
    if not (ROOT/'.venv').exists():
        print('Creating a private Python environment...')
        venv.EnvBuilder(with_pip=True).create(ROOT/'.venv')
    python = private_python()
    subprocess.run([str(python),'-m','pip','install','-r',str(ROOT/'requirements.txt')],check=True)
    print('\nDetected serial ports:')
    subprocess.run([str(python),'-m','serial.tools.list_ports'])
    default_port = existing.get('serial_port','COM10')
    port = input(f'Arduino port [{default_port}]: ').strip() or default_port
    memory_text = input(f'Server maximum RAM in GB [{existing.get("memory_gb",2)}]: ').strip()
    memory = int(memory_text) if memory_text else int(existing.get('memory_gb',2))
    if not 1 <= memory <= 32:
        raise RuntimeError('Choose a server memory limit from 1 to 32 GB, leaving enough for Minecraft and Windows.')
    RUNTIME.mkdir(exist_ok=True)
    download_server(RUNTIME/'server.jar')
    create_properties(RUNTIME/'server.properties')
    install_packs(RUNTIME/'world')
    (RUNTIME/'eula.txt').write_text('eula=true\n',encoding='utf-8')
    CONFIG.write_text(json.dumps({'java':str(java),'serial_port':port,'memory_gb':memory},indent=2),encoding='utf-8')
    print('\nSetup complete. Program the FPGA and UNO using HARDWARE.md.')
    print('Then run 02_Start.bat and join localhost in Minecraft Java 26.3.')
    print('After joining, type op YourMinecraftName in the SERVER console to enable commands.')
    print('Your private RCON password is generated locally; the bridge reads it automatically.')

if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as exc:
        print('\nSetup stopped:', exc)
        sys.exit(1)
