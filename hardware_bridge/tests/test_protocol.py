"""Run with python -m unittest discover -s tests from the package directory."""
import ast
from pathlib import Path
import re
import unittest
source = Path(__file__).resolve().parents[1] / 'bridge_practical.py'
tree = ast.parse(source.read_text())
namespace = {'re': re, 'MAX_REPLAY': 32}
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('parse_frame', 'press_deltas', 'parse_binding', 'make_command')]
exec(compile(ast.Module(body=functions,type_ignores=[]), str(source), 'exec'), namespace)

class ProtocolTests(unittest.TestCase):
    def test_ten_switches_and_both_counters(self):
        self.assertEqual(namespace['parse_frame']('V2 3FF 10 25'),(1023,(10,25)))
    def test_legacy_switches(self):
        self.assertEqual(namespace['parse_frame']('3FF'),(1023,None))
    def test_invalid_frames(self):
        for s in ('V2 400 0 0','V2 1 -1 0','V2 1 0 4294967296','V2 1 0','junk','V2 XX 0 0'):
            self.assertIsNone(namespace['parse_frame'](s))
    def test_startup_and_hold_do_not_pulse(self):
        self.assertEqual(namespace['press_deltas'](None,(5,8)),(0,0))
        self.assertEqual(namespace['press_deltas']((5,8),(5,8)),(0,0))
    def test_separate_and_repeated_presses(self):
        self.assertEqual(namespace['press_deltas']((5,8),(6,8)),(1,0))
        self.assertEqual(namespace['press_deltas']((5,8),(7,10)),(2,2))
    def test_counter_wrap_and_reset(self):
        self.assertEqual(namespace['press_deltas']((0xFFFFFFFF,8),(0,8)),(1,0))
        self.assertEqual(namespace['press_deltas']((100,100),(0,0)),(0,0))
    def test_binding_compatibility(self):
        b=namespace['parse_binding']('{x:-94,y:-59,z:17,dimension:"minecraft:overworld",face:"floor",facing:"west"}')
        self.assertEqual(b['x'],-94)
        self.assertIn('face=floor,facing=west,powered=false',namespace['make_command'](b,False))

if __name__ == '__main__':
    unittest.main()
