"""Check the user's single-bit full adder and its competing fanout routes."""
import itertools
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import hdl_to_minecraft as h
import test_mux as mux


@unittest.skipUnless(shutil.which('yosys'), 'Yosys executable unavailable')
class FullAdderTests(unittest.TestCase):
    def test_all_eight_combinations_and_export_geometry(self):
        source = Path(__file__).resolve().parents[1] / 'examples/Full_Adder.sv'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'adder.json'
            h.synthesize([source], 'Full_Adder', output)
            netlist = h.basic_netlist(json.loads(output.read_text()), 'Full_Adder')
        for a,b,carry in itertools.product((0,1), repeat=3):
            inputs = dict(in1=a,in2=b,C_in=carry)
            total = a+b+carry
            for name,expected in [('out1',total&1), ('C_out',total>>1)]:
                selected = {**netlist, 'ports': [p for p in netlist['ports']
                            if p['direction']=='input' or p['name']==name]}
                self.assertEqual(mux.evaluate(selected,inputs),expected)
        commands, layout = h.minecraft(netlist)
        self.assertEqual(sum('minecraft:lever[' in c for c in commands),3)
        self.assertEqual(sum(p['direction']=='output' for p in layout['ports']),2)
        self.assertEqual(len({tuple(p['xz']) for p in layout['ports']}),5)
        # Both inputs feed the same column: overlapping straight trunks must
        # fall back to independent trees instead of being shorted together.
        self.assertEqual(layout['control_buses'], [])
        mux.MuxTests().check_layout(netlist, commands, layout)
