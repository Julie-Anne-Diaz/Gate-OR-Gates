"""Exhaustive logical verification; physical ALU routing is checked separately."""
import itertools
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import hdl_to_minecraft as h
import test_mux as mux


@unittest.skipUnless(shutil.which('yosys'), 'Yosys executable unavailable')
class AluTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parents[1] / 'examples/ALU_4bit.sv'
        cls.netlists = {}
        with tempfile.TemporaryDirectory() as directory:
            for profile in ('default', 'compact'):
                output = Path(directory) / f'{profile}.json'
                h.synthesize([source], 'ALU_4bit', output, profile=profile)
                cls.netlists[profile] = h.basic_netlist(json.loads(output.read_text()), 'ALU_4bit')

    def test_all_4096_input_combinations(self):
        def reverse(value):
            return sum(((value >> bit) & 1) << (3-bit) for bit in range(4))
        for a, b, sel in itertools.product(range(16), repeat=3):
            expected = [a & b, a | b, ~a, ~(a | b), ~(a & b),
                        a ^ b, ~(a ^ b), a << 1, a >> 1, -a,
                        reverse(a), reverse(b), a+1, a-1, a, b][sel] & 15
            for profile, netlist in self.netlists.items():
                self.assertEqual(mux.evaluate(netlist, dict(in1=a, in2=b, sel=sel)),
                                 expected, (profile, a, b, sel))

    def test_compact_alu_reduces_gates_and_connections(self):
        default, compact = (self.netlists[p] for p in ('default', 'compact'))
        self.assertLess(len(compact['gates']), len(default['gates']))
        self.assertLess(sum(len(n['sinks']) for n in compact['nets']),
                        sum(len(n['sinks']) for n in default['nets']))
        self.assertFalse(any(n['source'][0] == 'constant' for n in compact['nets']))
