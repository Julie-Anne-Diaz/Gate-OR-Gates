from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import setup
import update_datapacks

class DatapackUpdateTests(unittest.TestCase):
    def fixture(self, root):
        repo = root/'repo'
        pack = repo/'minecraft/datapacks/display_fixed'
        (pack/'data/redstone/function/display_staged').mkdir(parents=True)
        (pack/'pack.mcmeta').write_text('{}')
        (pack/'data/redstone/function/display.mcfunction').write_text('function redstone:display_staged/finish\n')
        (pack/'data/redstone/function/display_staged/finish.mcfunction').write_text('say complete\n')
        return repo/'hardware_bridge'

    def test_fresh_setup_copies_entry_and_helpers(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); hardware=self.fixture(root); world=root/'world'
            with patch.object(setup,'ROOT',hardware):setup.install_packs(world)
            self.assertTrue((world/'datapacks/display_fixed/data/redstone/function/display_staged/finish.mcfunction').is_file())
            (world/'datapacks/display_fixed/pack.mcmeta').write_text('custom')
            with patch.object(setup,'ROOT',hardware):setup.install_packs(world)
            self.assertEqual((world/'datapacks/display_fixed/pack.mcmeta').read_text(),'custom')

    def test_update_backs_up_folder_and_zip_keeps_world_and_unrelated_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); hardware=self.fixture(root); world=root/'world'
            old=world/'datapacks/display_fixed';old.mkdir(parents=True)
            (old/'obsolete.mcfunction').write_text('old')
            old.with_suffix('.zip').write_bytes(b'old archive')
            custom=world/'datapacks/custom';custom.mkdir();(custom/'keep').write_text('custom')
            (world/'level.dat').write_bytes(b'world')
            backups=root/'backups';backups.mkdir()
            with patch.object(setup,'ROOT',hardware):backup=update_datapacks.update_packs(world,backups)
            self.assertEqual((backup/'display_fixed/obsolete.mcfunction').read_text(),'old')
            self.assertEqual((backup/'display_fixed.zip').read_bytes(),b'old archive')
            self.assertFalse((old/'obsolete.mcfunction').exists())
            self.assertTrue((old/'data/redstone/function/display.mcfunction').is_file())
            self.assertEqual((custom/'keep').read_text(),'custom')
            self.assertEqual((world/'level.dat').read_bytes(),b'world')

    def test_update_refuses_running_server_before_writing(self):
        with patch.object(update_datapacks,'properties',return_value={'server-port':'25565'}), patch.object(update_datapacks,'port_open',return_value=True), patch.object(update_datapacks,'update_packs') as update:
            with self.assertRaisesRegex(RuntimeError,'Stop the server'):update_datapacks.main()
            update.assert_not_called()

if __name__=='__main__':unittest.main()
