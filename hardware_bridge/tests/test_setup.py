import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import common
import setup as installer

class SetupTests(unittest.TestCase):
    def test_new_properties_local_password_and_flat_world(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'server.properties';installer.create_properties(p)
            props=dict(x.split('=',1) for x in p.read_text().splitlines())
            self.assertEqual(props['server-ip'],'127.0.0.1')
            self.assertEqual(props['online-mode'],'true')
            self.assertRegex(props['rcon.password'],r'^[0-9a-f]{48}$')
            self.assertEqual(json.loads(props['generator-settings'])['layers'][-1]['block'],'minecraft:grass_block')
    def test_existing_properties_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'server.properties';p.write_text('existing=true\n');installer.create_properties(p)
            self.assertEqual(p.read_text(),'existing=true\n')
    def test_existing_pack_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'bridge_controls';p.mkdir(parents=True);(p/'pack.mcmeta').write_text('source')
            target=root/'world/datapacks/bridge_controls';target.mkdir(parents=True);(target/'pack.mcmeta').write_text('custom')
            with patch.object(installer,'ROOT',root):installer.install_packs(root/'world')
            self.assertEqual((target/'pack.mcmeta').read_text(),'custom')
    def test_installs_both_repo_packs(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d);root=repo/'hardware_bridge'
            controls=root/'bridge_controls';controls.mkdir(parents=True)
            (controls/'pack.mcmeta').write_text('source')
            archive=repo/'minecraft/snapshots/redstone.zip';archive.parent.mkdir(parents=True)
            with zipfile.ZipFile(archive,'w') as z:z.writestr('pack.mcmeta','source')
            with patch.object(installer,'ROOT',root):installer.install_packs(root/'runtime/world')
            for name in ('bridge_controls','redstone'):
                self.assertEqual((root/'runtime/world/datapacks'/name/'pack.mcmeta').read_text(),'source')
    def test_download_verified_and_atomic(self):
        payload=b'test download';checksum=hashlib.sha1(payload).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'server.jar'
            with patch.object(installer,'SERVER_SHA1',checksum),patch.object(installer.urllib.request,'urlopen',return_value=io.BytesIO(payload)):
                installer.download_server(p)
            self.assertEqual(p.read_bytes(),payload);self.assertFalse(p.with_suffix('.download').exists())
    def test_bad_checksum_leaves_no_server(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'server.jar'
            with patch.object(installer.urllib.request,'urlopen',return_value=io.BytesIO(b'bad')):
                with self.assertRaises(RuntimeError):installer.download_server(p)
            self.assertFalse(p.exists());self.assertFalse(p.with_suffix('.download').exists())
    def test_unrecognized_server_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'server.jar';p.write_bytes(b'custom')
            with self.assertRaises(RuntimeError):installer.download_server(p)
            self.assertEqual(p.read_bytes(),b'custom')
    def test_java8_rejected_java25_allowed(self):
        with patch.object(common,'java_major',return_value=8):
            with self.assertRaises(RuntimeError):common.require_java('java')
        with patch.object(common,'java_major',return_value=25):common.require_java('java')

if __name__=='__main__':unittest.main()
