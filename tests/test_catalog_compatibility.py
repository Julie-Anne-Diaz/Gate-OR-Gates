"""The exporter must work with the shared catalog and its hex component file."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import gate_templates as catalog
import hdl_to_minecraft as h


ROOT = Path(__file__).resolve().parents[1]


class CatalogCompatibilityTests(unittest.TestCase):
    def test_adaptation_preserves_the_recorded_catalog(self):
        original = copy.deepcopy(catalog.GATES)
        h.load_templates.cache_clear()
        library = h.load_templates()
        self.assertEqual(catalog.GATES, original)
        self.assertEqual(set(library.GATES), set(h.CELL_TYPES.values()))
        self.assertIn('ANDASYNCDFF', library.STANDALONE_GATES)
        self.assertIn('SYNCDFF', library.STANDALONE_GATES)
        # Local clock-start levers are not external HDL clock inputs.
        self.assertNotIn('ANDASYNCDFF', library.ROUTABLE_GATES)
        for name, template in library.ROUTABLE_GATES.items():
            with self.subTest(template=name):
                h.validate_template(name, template)
        nand = library.GATES['NAND']
        self.assertEqual(nand.outputs['Y'].x, 4)
        self.assertEqual(len(library.GATES['BUFFER'].blocks), 6)
        self.assertEqual(len(library.STANDALONE_GATES['ASYNCDFF'].blocks), 56)

    @unittest.skipUnless(importlib.util.find_spec('ortools'), 'OR-Tools unavailable')
    def test_runtime_distribution_generates_shared_clock_and_feedback(self):
        # No tests, backups, or andtemplate.py in this directory.
        # Q0 feeds D1, Q1 feeds D0; both DFFs use one top-level clock.
        raw = {'modules': {'counterexample': {
            'ports': {'clk': {'direction': 'input', 'bits': [2]},
                      'q': {'direction': 'output', 'bits': [3, 4]}},
            'cells': {
                'a': {'type': '$_DFF_P_', 'connections': {'D': [4], 'C': [2], 'Q': [3]}},
                'b': {'type': '$_DFF_P_', 'connections': {'D': [3], 'C': [2], 'Q': [4]}}}}}}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for filename in ('hdl_to_minecraft.py', 'gate_templates.py', 'sevenseg_hex_template.py'):
                shutil.copyfile(ROOT / filename, folder / filename)
            (folder / 'input.json').write_text(json.dumps(raw), encoding='utf-8')
            result = subprocess.run([
                sys.executable, 'hdl_to_minecraft.py', '--from-json', 'input.json',
                '--top', 'counterexample', '--output', 'out.json',
                '--mcfunction', 'out.mcfunction', '--clock-source', 'integrated'],
                cwd=folder, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            layout = json.loads((folder / 'out.routes.json').read_text())
            commands = (folder / 'out.mcfunction').read_text()
            self.assertEqual(layout['placement']['method'], 'ortools_cp_sat')
            self.assertTrue(layout['placement']['routing_validated'])
            self.assertEqual(len(layout['routes']), 6)
            self.assertEqual(len(layout['clocks']), 1)
            self.assertEqual(len(layout['clocks'][0]['registers']), 2)
            self.assertTrue(layout['feedback_sinks'])
            self.assertEqual(commands.count('minecraft:observer['), 1)
            self.assertIn('minecraft:redstone_wire', commands)


if __name__ == '__main__':
    unittest.main()
