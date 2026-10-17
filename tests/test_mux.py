"""Synthesis truth tables and fanout routing; not a Minecraft simulator."""
import itertools
import json
from pathlib import Path
import random
import re
import shutil
import tempfile
import unittest

import hdl_to_minecraft as h
from test_routing import assert_no_unplanned_contacts


def evaluate(netlist, inputs):
    values = {'0': 0, '1': 1}
    for p in netlist['ports']:
        if p['direction'] == 'input':
            name, _, index = p['name'].partition('[')
            values[p['bit']] = (inputs[name] >> int(index.rstrip(']') or 0)) & 1
    for g in netlist['gates']:
        pins = g['pins']
        a, b = values[pins['A']], values.get(pins.get('B'), 0)
        values[pins['Y']] = {'AND': a&b, 'OR': a|b, 'NAND': 1^(a&b),
                            'NOR': 1^(a|b), 'XOR': a^b, 'XNOR': 1^(a^b),
                            'NOT': 1^a, 'BUFFER': a}[g['gate']]
    return sum(values[p['bit']] << int(p['name'].partition('[')[2].rstrip(']') or 0)
               for p in netlist['ports'] if p['direction'] == 'output')


@unittest.skipUnless(shutil.which('yosys'), 'Yosys executable unavailable')
class MuxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1] / 'examples'
        cls.netlists = {}
        with tempfile.TemporaryDirectory() as directory:
            for top, files in [('mux_2', ['mux_2.sv']), ('mux_4', ['mux_2.sv', 'mux_4.sv'])]:
                output = Path(directory) / (top+'.json')
                h.synthesize([root/f for f in files], top, output)
                cls.netlists[top] = h.basic_netlist(json.loads(output.read_text()), top)

    def test_mux2_all_512_input_combinations(self):
        for a,b,sel in itertools.product(range(16), range(16), range(2)):
            self.assertEqual(evaluate(self.netlists['mux_2'], dict(in1=a,in2=b,sel=sel)), b if sel else a)

    def test_structural_mux4_all_lane_combinations_and_bus_patterns(self):
        netlist = self.netlists['mux_4']
        for bit in range(4):
            for data in itertools.product(range(2), repeat=4):
                for sel in range(4):
                    inputs = {f'in{i+1}': data[i]<<bit for i in range(4)}
                    self.assertEqual(evaluate(netlist, dict(inputs,sel=sel)), data[sel]<<bit)
        rng = random.Random(42)
        for _ in range(1024):
            data = [rng.randrange(16) for _ in range(4)]
            sel = rng.randrange(4)
            self.assertEqual(evaluate(netlist, dict(zip(('in1','in2','in3','in4'),data),sel=sel)), data[sel])

    def test_mux2_fanout_connections_signal_strength_and_separation(self):
        netlist = self.netlists['mux_2']
        commands, layout = h.minecraft(netlist)
        self.assertLess(len(commands), 1388)
        self.assertLess(layout['placement']['horizontal_area'], 3555)
        self.assertEqual(layout['placement']['effective_spacing'], 4)
        self.assertEqual(len(layout['control_buses']), 2)
        self.check_layout(netlist, commands, layout)
        self.assertEqual(sum(p['name']=='sel' for p in layout['ports']), 1)
        self.assertEqual(sum('minecraft:lever[' in c for c in commands), 9)

    def test_mux4_routes_all_connections_with_three_control_trunks(self):
        netlist = self.netlists['mux_4']
        commands, layout = h.minecraft(netlist)
        self.assertEqual(len(layout['control_buses']), 3)
        self.assertEqual(sum('minecraft:lever[' in c for c in commands), 18)
        self.check_layout(netlist, commands, layout)

    def check_layout(self, netlist, commands, layout):
        assert_no_unplanned_contacts(self, layout['routes'])
        self.assertEqual(len(layout['routes']), sum(len(n['sinks']) for n in netlist['nets']))
        blocks = {}
        for command in commands:
            match = re.search(r'setblock ~(-?\d*) ~(-?\d*) ~(-?\d*) (\S+)', command)
            self.assertIsNotNone(match)
            xyz = tuple(int(v or 0) for v in match.groups()[:3])
            self.assertNotIn(xyz, blocks)
            blocks[xyz] = match[4]
        actual = {(r['bit'], tuple(r['sink'])) for r in layout['routes']}
        expected = {(n['bit'],tuple(s)) for n in netlist['nets'] for s in n['sinks']}
        self.assertEqual(actual, expected)
        trees, owners = {}, {}
        for route in layout['routes']:
            bit = route['bit']
            path = [tuple(p) for p in route['path_xyz']]
            if bit in trees:
                self.assertIn(path[0], trees[bit])
                self.assertEqual(route['initial_signal_distance'], trees[bit][path[0]])
            tree = trees.setdefault(bit, {})
            boosts = {tuple(r['xyz']) for r in route['repeaters']}
            distance = route['initial_signal_distance']
            for i,p in enumerate(path):
                if i:
                    distance = 0 if p in boosts else distance+1
                self.assertLessEqual(distance, 12)
                tree[p] = distance
                x,y,z = p
                self.assertIn((x,y-1,z), blocks, 'Missing wire support')
                self.assertNotIn((x,y+1,z), blocks, 'Blocked wire headroom')
                self.assertIn(p, blocks)
                for nx,nz in [(x,z),*h.neighbors((x,z))]:
                    for ny in range(y-1,y+2):
                        self.assertIn(owners.get((nx,ny,nz), bit), [bit], 'Unrelated routes touch')
                owners[p] = bit
        for bus in layout['control_buses']:
            for _,z in bus['taps']:
                self.assertEqual(blocks[(bus['x'],0,z)], 'minecraft:redstone_wire',
                                 'A control tap must be dust, not a repeater')


class HierarchyMetadataTests(unittest.TestCase):
    def test_scopeinfo_is_ignored_but_unknown_logic_is_rejected(self):
        module = {'ports': {}, 'cells': {'scope': {'type': '$scopeinfo'}}}
        self.assertEqual(h.basic_netlist({'modules': {'top':module}}, 'top')['gates'], [])
        module['cells']['scope']['type'] = '$unknown'
        with self.assertRaisesRegex(ValueError, 'Unsupported cell'):
            h.basic_netlist({'modules': {'top':module}}, 'top')
