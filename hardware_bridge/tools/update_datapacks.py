"""Refresh repository-managed datapacks, preserving a backup outside the world."""
from datetime import datetime
from pathlib import Path
import shutil
import tempfile
from common import ROOT, RUNTIME, properties, port_open
from setup import install_packs


def update_packs(world, backup_root):
    # Stage everything before touching the installed packs.
    with tempfile.TemporaryDirectory() as temp:
        staged = Path(temp)/'world'
        install_packs(staged)
        packs = staged/'datapacks'
        if not packs.is_dir():
            raise RuntimeError('No source datapacks found; nothing changed.')
        backup = Path(tempfile.mkdtemp(prefix=datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=backup_root))
        destination = world/'datapacks'
        destination.mkdir(parents=True, exist_ok=True)
        for source in sorted(packs.iterdir()):
            target = destination/source.name
            for existing in (target, target.with_suffix('.zip')):
                if existing.exists():
                    shutil.move(str(existing), str(backup/existing.name))
            try:
                shutil.copytree(source, target)
            except Exception:
                if target.exists():
                    shutil.rmtree(target)
                for saved in (backup/source.name, backup/(source.name+'.zip')):
                    if saved.exists():
                        shutil.move(str(saved), str(destination/saved.name))
                raise
            print('Updated datapack:', source.name)
        print('Previous packs backed up to:', backup)
        return backup


def main():
    props = properties()
    if port_open(props.get('server-port', '25565')) or port_open(props.get('rcon.port', '25575')):
        raise RuntimeError('Stop the server with stop, and close the bridge, before updating datapacks.')
    world = RUNTIME/props.get('level-name', 'world')
    if not world.is_dir():
        raise RuntimeError('World not found. Run setup and start the server once first.')
    backup_root = RUNTIME/'datapack_backups'
    backup_root.mkdir(parents=True, exist_ok=True)
    update_packs(world, backup_root)
    print('Start 02_Start.bat, then run /function redstone:display in game.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('ERROR:', error)
        raise SystemExit(1)
