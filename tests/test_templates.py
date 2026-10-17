"""Template geometry and optional end-to-end synthesis regressions."""
from dataclasses import replace
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import hdl_to_minecraft as h

t = h.load_templates()


class TemplateTests(unittest.TestCase):
    def test_all_templates_supported_and_routed(self):
        for name in t.GATES:
            with self.subTest(gate=name):
                h.validate_template(name)
                commands, layout = h.minecraft(h.gate_test_netlist(name))
                self.assertTrue(commands)
                self.assertEqual(len(layout['gates']), 1)
                self.assertEqual(len(layout['routes']), len(t.GATES[name].inputs) + 1)

    def test_bad_terminal_rejected(self):
        gate = t.GATES['NAND']
        broken = replace(gate, outputs={'Y': replace(gate.outputs['Y'], x=5)})
        with self.assertRaisesRegex(ValueError, 'terminal'):
            h.validate_template('NAND', broken)

    def test_missing_xor_support_rejected(self):
        gate = t.GATES['XOR']
        broken = replace(gate, blocks=tuple(b for b in gate.blocks if (b.x,b.y,b.z) != (7,-1,1)))
        with self.assertRaisesRegex(ValueError, 'unsupported component'):
            h.validate_template('XOR', broken)

    @unittest.skipUnless(importlib.util.find_spec('ortools'), 'optional OR-Tools unavailable')
    def test_all_templates_ortools(self):
        _, layout = h.minecraft(h.gate_test_netlist(), placer='ortools')
        self.assertEqual(len(layout['gates']), 8)
        self.assertTrue(layout['placement']['routing_validated'])

    @unittest.skipUnless(shutil.which('yosys'), 'Yosys executable unavailable')
    def test_mixed_hdl_truth_table_and_routing(self):
        source = Path(__file__).resolve().parents[1] / 'examples/MIXED_CHAIN.sv'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'mixed.json'
            h.synthesize([source], 'MIXED_CHAIN', output)
            netlist = h.basic_netlist(json.loads(output.read_text()), 'MIXED_CHAIN')
        operations = {'AND': lambda a,b:a&b, 'OR':lambda a,b:a|b,
                      'XOR':lambda a,b:a^b, 'XNOR':lambda a,b:1^(a^b),
                      'NAND':lambda a,b:1^(a&b), 'NOR':lambda a,b:1^(a|b),
                      'NOT':lambda a,b:1^a, 'BUFFER':lambda a,b:a}
        ports = {p['name']:p['bit'] for p in netlist['ports']}
        for inputs in itertools.product((0,1), repeat=5):
            values = {'0':0, '1':1, **dict(zip((ports[n] for n in 'abcde'), inputs))}
            pending = list(netlist['gates'])
            while pending:
                ready = [g for g in pending if all(v in values for k,v in g['pins'].items() if k != 'Y')]
                self.assertTrue(ready, 'No evaluable gates')
                for gate in ready:
                    pins = gate['pins']
                    values[pins['Y']] = operations[gate['gate']](values[pins['A']], values.get(pins.get('B'), 0))
                    pending.remove(gate)
            a,b,c,d,e = inputs
            self.assertEqual(values[ports['y']], ((a^b)&(c|d))^(1^e))
        commands, layout = h.minecraft(netlist)
        self.assertEqual(len(layout['routes']), len(netlist['nets']))
        # Fanout improvements must not force this compact, single-sink circuit
        # into a wider retry just because two connected terminals are adjacent.
        self.assertEqual(len(commands), 168)
        self.assertEqual(layout['placement']['wire_steps'], 7)
        self.assertEqual(layout['placement']['horizontal_area'], 288)
        self.assertEqual(layout['placement']['bridges'], 0)
        self.assertEqual(len(layout['placement']['attempts']), 1)
