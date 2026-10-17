"""Sequential HDL/mapped-cell formal traces and standalone template checks.

These tests do not simulate Minecraft block updates.
"""
import json
import copy
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import hdl_to_minecraft as h

t = h.load_templates()
from test_routing import assert_no_unplanned_contacts


ROOT = Path(__file__).resolve().parents[1]


class StandaloneDffTests(unittest.TestCase):
    def test_declared_initial_state_is_preserved(self):
        raw = {'modules': {'dff': {
            'ports': {'D': {'direction':'input','bits':[2]},
                      'CLK': {'direction':'input','bits':[3]},
                      'Q': {'direction':'output','bits':[4]}},
            'netnames': {'Q': {'bits':[4], 'attributes': {'init':'1'}}},
            'cells': {'state': {'type':'$_DFF_P_',
                                'connections': {'D':[2], 'C':[3], 'Q':[4]}}}}}}
        net = h.basic_netlist(raw, 'dff')
        self.assertEqual(net['registers'][0]['initial_value'], 1)

    def test_supports_controls_and_ceiling_are_placed_first(self):
        template = t.STANDALONE_GATES['ASYNCDFF']
        h.validate_template('ASYNCDFF', require_routable=False)
        commands, details = h.standalone_template('ASYNCDFF')
        self.assertEqual(len(commands), 56)
        self.assertEqual(sum('minecraft:lever[' in c for c in commands), 3)
        self.assertEqual(details['terminals']['A'], [0,0,2])
        self.assertEqual(details['terminals']['RESET'], [0,0,0])
        self.assertIsNone(details['terminals']['CLK'])
        self.assertFalse(details['automatic_wiring_ready'])
        for b in template.blocks:
            if 'minecraft:repeater' in b.state:
                self.assertTrue(any((s.x,s.y,s.z)==(b.x,b.y-1,b.z) for s in template.blocks))
        ceiling = next(i for i,c in enumerate(commands) if 'setblock ~ ~2 ~ minecraft:brown_wool' in c)
        sign = next(i for i,c in enumerate(commands) if 'hanging_sign' in c)
        self.assertLess(ceiling, sign)

    def test_missing_clock_cannot_be_silently_routed(self):
        with self.assertRaisesRegex(ValueError, 'CLK: terminal is missing'):
            h.validate_template('ASYNCDFF')
        self.assertNotIn('ASYNCDFF', t.GATES)
        self.assertEqual(len(t.GATES), 8)


@unittest.skipUnless(shutil.which('yosys'), 'Yosys executable unavailable')
class SequentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.folder = Path(cls.directory.name)
        cls.nets, cls.sources = {}, {}
        for top in ('DFF', 'ASYNCDFF', 'REGISTER_CHAIN', 'TOGGLE_FF', 'DFF_LOGIC', 'REGISTERED_HALF_ADDER'):
            sources = [ROOT/'examples'/f'{top}.sv']
            if top == 'REGISTER_CHAIN':
                sources.insert(0, ROOT/'examples/ASYNCDFF.sv')
            cls.sources[top] = sources
            output = cls.folder/f'{top}.json'
            h.synthesize(sources, top, output)
            cls.nets[top] = h.basic_netlist(json.loads(output.read_text()), top)

    def test_clock_reset_and_shared_clock_nets(self):
        plain = self.nets['DFF']['registers'][0]
        self.assertEqual(plain['clock_edge'], 'rising')
        self.assertNotIn('reset', plain)
        async_cell = self.nets['ASYNCDFF']['registers'][0]
        self.assertEqual(async_cell['reset'], {'kind':'asynchronous','active_level':1,'value':0})
        chain = self.nets['REGISTER_CHAIN']
        self.assertEqual(len(chain['registers']), 2)
        clocks = {r['pins']['CLK'] for r in chain['registers']}
        self.assertEqual(len(clocks), 1)
        clock_net = next(n for n in chain['nets'] if n['bit'] in clocks)
        self.assertEqual([s[1] for s in clock_net['sinks']], ['CLK', 'CLK'])

    def test_register_feedback_and_combinational_loop_are_distinguished(self):
        toggle = self.nets['TOGGLE_FF']
        self.assertEqual(len(toggle['registers']), 1)
        self.assertEqual([g['gate'] for g in toggle['gates']], ['NOT'])
        loop = {'modules': {'loop': {'ports': {}, 'cells': {
            'bad': {'type':'$_NOT_', 'connections': {'A':[2], 'Y':[2]}}}}}}
        with self.assertRaisesRegex(ValueError, 'Combinational feedback'):
            h.basic_netlist(loop, 'loop')

    def test_unassigned_physical_clock_is_actionable(self):
        with self.assertRaisesRegex(ValueError, '--clock-source integrated'):
            h.minecraft(self.nets['ASYNCDFF'])

    @unittest.skipUnless(importlib.util.find_spec('ortools'), 'OR-Tools unavailable')
    def test_integrated_clock_is_preserved_with_routed_logic(self):
        for top in ('DFF', 'ASYNCDFF', 'DFF_LOGIC'):
            with self.subTest(top=top):
                original = copy.deepcopy(self.nets[top])
                commands, layout = h.minecraft(self.nets[top], clock_source='integrated', origin=(10,-59,20))
                self.assertEqual(len(commands), {'DFF': 64, 'ASYNCDFF': 68, 'DFF_LOGIC': 126}[top])
                self.assertEqual(self.nets[top], original)
                self.assertEqual(layout['placement']['method'], 'ortools_cp_sat')
                self.assertEqual(layout['placement']['solver_status'], 'OPTIMAL')
                self.assertTrue(layout['placement']['routing_validated'])
                self.assertEqual(len(layout['gates']), len(original['gates']) + 1)
                self.assertNotIn('CLK', {p['name'] for p in layout['ports']})
                self.assertEqual(layout['clock']['hdl_ports'], ['CLK'])
                clock_bit = original['registers'][0]['pins']['CLK']
                self.assertEqual({(r['bit'], tuple(r['sink'])) for r in layout['routes']},
                                 {(n['bit'], tuple(s)) for n in original['nets']
                                  if n['bit'] != clock_bit for s in n['sinks']})
                # Check every supplied block after translation, including all
                # clock repeaters, observer, clock lever and locking circuit.
                placed = next(g for g in layout['gates'] if g['name'] == original['registers'][0]['name'])
                gx, gz = placed['xz']
                xyz = layout['clock']['trigger_local_xyz']
                self.assertEqual(xyz, [gx+5, 0, gz+7])
                for b in t.STANDALONE_GATES['ASYNCDFF'].blocks:
                    state = ('minecraft:redstone_wire' if (b.x,b.y,b.z) in {(0,0,0),(0,0,2)}
                             else b.state)
                    self.assertIn(f'setblock {10+gx+b.x} {-59+b.y} {20+gz+b.z} {state} replace', commands)
                ceiling = next(i for i,c in enumerate(commands)
                               if c.startswith(f'setblock {10+gx} -57 {20+gz} '))
                sign = next(i for i,c in enumerate(commands) if 'hanging_sign' in c)
                self.assertLess(ceiling, sign)
                self.assertEqual(sum('minecraft:lever[' in c for c in commands),
                                 1 + sum(p['direction'] == 'input' for p in layout['ports']))
                self.assertTrue(all('minecraft:stone ' not in c for c in commands))
                if top == 'DFF_LOGIC':
                    cell_links = [r for r in layout['routes']
                                  if r['source'][0] != 'port' and r['sink'][0] != 'port']
                    self.assertEqual(len(cell_links), 2)

    def test_integrated_clock_does_not_drop_observable_clock(self):
        # An output copy of CLK cannot be dropped or replaced by a dummy lever.
        net = copy.deepcopy(self.nets['ASYNCDFF'])
        bit = net['registers'][0]['pins']['CLK']
        net['ports'].append({'name':'clock_out', 'bit':bit, 'direction':'output'})
        next(n for n in net['nets'] if n['bit'] == bit)['sinks'].append(['port','clock_out'])
        with self.assertRaisesRegex(ValueError, 'external tap'):
            h.minecraft(net, clock_source='integrated')

    def test_shared_clock_has_one_source_and_reaches_every_register(self):
        net = self.nets['REGISTER_CHAIN']
        original = copy.deepcopy(net)
        commands, layout = h.minecraft(net, clock_source='integrated')
        self.assertEqual(net, original)
        self.assertEqual(len(layout['clocks']), 1)
        clock = layout['clock']
        self.assertEqual(clock['source'], 'integrated_shared')
        self.assertEqual(len(clock['registers']), 2)
        clock_routes = [r for r in layout['routes'] if r['bit'] == clock['bit']]
        self.assertEqual({tuple(r['sink']) for r in clock_routes},
                         {(r['name'], 'CLK') for r in net['registers']})
        self.assertTrue(all(r['source'] == [clock['clock_gate'], 'Y'] for r in clock_routes))
        self.assertEqual(len(clock['terminal_delays']), 2)
        self.assertFalse(clock['timing_validated'])
        delays = [d['to_clk_pin_repeater_ticks'] for d in clock['terminal_delays']]
        self.assertEqual(clock['skew_repeater_ticks'], max(delays)-min(delays))
        self.assertEqual(sum('minecraft:observer[' in c for c in commands), 1)
        self.assertEqual({(r['bit'], tuple(r['sink'])) for r in layout['routes']},
                         {(n['bit'], tuple(s)) for n in net['nets'] for s in n['sinks']})
        assert_no_unplanned_contacts(self, layout['routes'])
        for name in ('ASYNCDFF_SHARED', 'DFF_SHARED', 'CLOCK_SOURCE'):
            h.validate_template(name)
        receiver = {(b.x,b.y,b.z): b.state for b in t.CLOCKED_GATES['ASYNCDFF_SHARED'].blocks}
        for b in t.STANDALONE_GATES['ASYNCDFF'].blocks:
            if b.z <= 4 or (b.x,b.y,b.z) == (1,0,5):
                self.assertEqual(receiver[(b.x,b.y,b.z)], b.state)
        self.assertFalse(any('observer' in state for state in receiver.values()))

    def test_register_feedback_routes_without_wire_feedback(self):
        net = self.nets['TOGGLE_FF']
        commands, layout = h.minecraft(net, clock_source='integrated')
        reg = net['registers'][0]
        self.assertEqual(layout['feedback_sinks'], [(reg['name'], 'A')])
        feedback = next(r for r in layout['routes'] if r['sink'] == [reg['name'], 'A'])
        self.assertGreater(feedback['path_xyz'][0][0], feedback['path_xyz'][-1][0])
        self.assertEqual({(r['bit'], tuple(r['sink'])) for r in layout['routes']},
                         {(n['bit'], tuple(s)) for n in net['nets']
                          if n['bit'] != reg['pins']['CLK'] for s in n['sinks']})
        assert_no_unplanned_contacts(self, layout['routes'])
        self.assertTrue(commands)

    def test_two_bit_counter_combines_shared_clock_and_feedback(self):
        source = self.folder / 'counter.sv'
        source.write_text('''module counter(input clk, rst, output reg [1:0] q);
            always @(posedge clk or posedge rst)
                if (rst) q <= 0; else q <= q + 1'b1;
            endmodule''')
        output = self.folder / 'counter.json'
        h.synthesize([source], 'counter', output)
        net = h.basic_netlist(json.loads(output.read_text()), 'counter')
        commands, layout = h.minecraft(net, clock_source='integrated')
        self.assertEqual(len(net['registers']), 2)
        self.assertEqual(len(layout['clock']['registers']), 2)
        self.assertEqual(len(layout['feedback_sinks']), 2)
        self.assertEqual(sum('minecraft:observer[' in c for c in commands), 1)
        self.assertEqual({(r['bit'], tuple(r['sink'])) for r in layout['routes']},
                         {(n['bit'], tuple(s)) for n in net['nets'] for s in n['sinks']})
        assert_no_unplanned_contacts(self, layout['routes'])

    @unittest.skipUnless(importlib.util.find_spec('ortools'), 'OR-Tools unavailable')
    def test_two_independent_dffs_feed_half_adder_with_original_clocks(self):
        net = self.nets['REGISTERED_HALF_ADDER']
        original = copy.deepcopy(net)
        self.assertEqual(len(net['registers']), 2)
        self.assertCountEqual([g['gate'] for g in net['gates']], ['AND', 'XOR'])
        commands, layout = h.minecraft(net, clock_source='integrated', origin=(0,-59,0))
        self.assertEqual(len(commands), 503)
        self.assertEqual(net, original)
        self.assertEqual(len(layout['clocks']), 2)
        self.assertNotIn('clock', layout)
        self.assertEqual({tuple(c['hdl_ports']) for c in layout['clocks']}, {('CLK_A',), ('CLK_B',)})
        self.assertEqual(len(layout['gates']), 4)
        self.assertTrue(layout['placement']['routing_validated'])
        self.assertEqual(layout['placement']['method'], 'ortools_cp_sat')
        self.assertEqual({p['name'] for p in layout['ports']}, {'A','B','RESET','result[0]','result[1]'})
        assert_no_unplanned_contacts(self, layout['routes'])
        clock_bits = {r['pins']['CLK'] for r in net['registers']}
        self.assertEqual({(r['bit'], tuple(r['sink'])) for r in layout['routes']},
                         {(n['bit'], tuple(s)) for n in net['nets']
                          if n['bit'] not in clock_bits for s in n['sinks']})
        for register in net['registers']:
            placed = next(g for g in layout['gates'] if g['name'] == register['name'])
            gx, gz = placed['xz']
            for b in t.STANDALONE_GATES['ASYNCDFF'].blocks:
                state = ('minecraft:redstone_wire' if (b.x,b.y,b.z) in {(0,0,0),(0,0,2)}
                         else b.state)
                self.assertIn(f'setblock {gx+b.x} {-59+b.y} {gz+b.z} {state} replace', commands)
        self.assertEqual(sum('minecraft:observer[' in c for c in commands), 2)
        self.assertEqual(sum('minecraft:lever[' in c for c in commands), 5)

    def test_integrated_template_rejects_unsupported_edge_reset_and_initialization(self):
        for change in ({'clock_edge':'falling'},
                       {'reset':{'kind':'asynchronous','active_level':0,'value':0}},
                       {'reset':{'kind':'asynchronous','active_level':1,'value':1}},
                       {'initial_value':1}):
            with self.subTest(change=change):
                net = copy.deepcopy(self.nets['ASYNCDFF'])
                net['registers'][0].update(change)
                with self.assertRaisesRegex(ValueError, 'template'):
                    h.minecraft(net, clock_source='integrated')

    def test_rtl_and_yosys_cells_capture_hold_reset_and_pipeline(self):
        # Use explicit clock levels, not an implicit "one step = one edge".
        # Each tuple is (*inputs, expected output). None leaves initial Q
        # unspecified until the first capture; reset cases start with RESET=1.
        cases = {
            'DFF': (('D','CLK'), 'Q', 1,
                [(0,0,None),(1,0,None),(1,1,1),(0,1,1),(0,0,1),(0,1,0)]),
            'ASYNCDFF': (('A','CLK','RESET'), 'Y', 1,
                [(0,0,1,0),(1,0,0,0),(1,1,0,1),(0,1,0,1),(0,0,0,1),
                 (0,1,0,0),(1,0,0,0),(1,1,0,1),(1,1,1,0),(1,1,0,0),
                 (1,0,0,0),(1,1,0,1)]),
            'REGISTER_CHAIN': (('A','CLK','RESET'), 'Y', 2,
                [(0,0,1,0),(1,0,0,0),(1,1,0,1),(0,1,0,1),(0,0,0,1),
                 (0,1,0,2),(0,0,0,2),(0,1,0,0)]),
            'TOGGLE_FF': (('CLK','RESET'), 'Q', 1,
                [(0,1,0),(0,0,0),(1,0,1),(1,0,1),(0,0,1),(1,0,0)]),
            'DFF_LOGIC': (('a','b','c','CLK','RESET'), 'Y', 1,
                [(0,0,0,0,1,0),(1,1,0,0,0,0),(1,1,0,1,0,1),
                 (0,0,0,1,0,1),(0,0,0,0,0,1),(0,0,0,1,0,0),
                 (0,0,1,1,0,1),(0,0,0,1,0,0)]),
            # Exercise A-first, B-first and simultaneous sampling, all four
            # stable input combinations, hold, reset and reset release.
            'REGISTERED_HALF_ADDER': (('A','B','CLK_A','CLK_B','RESET'), 'result', 2,
                [(0,0,0,0,1,0),(1,1,0,0,0,0),(1,1,1,0,0,1),(1,1,1,1,0,2),
                 (0,0,1,1,0,2),(0,0,0,0,0,2),(0,0,0,1,0,1),(0,0,1,1,0,0),
                 (1,0,0,0,0,0),(1,0,1,1,0,1),(0,1,1,1,0,1),(0,1,0,0,0,1),
                 (0,1,1,1,0,1),(1,1,0,0,0,1),(1,1,1,1,0,2),(1,1,1,1,1,0),
                 (1,1,1,1,0,0),(1,1,0,0,0,0),(1,1,0,1,0,1),(1,1,1,1,0,2)]),
        }
        for top, (inputs, output, width, trace) in cases.items():
            wrapper = self.folder/f'{top}_check.sv'
            connections = ','.join([*(f'.{p}({p})' for p in inputs), f'.{output}(value)'])
            wrapper.write_text(f'module check_ff(input {",".join(inputs)}, '
                f'input [{width-1}:0] expected, output ok); wire [{width-1}:0] value; '
                f'{top} dut({connections}); assign ok = value == expected; endmodule')
            constraints = []
            skip = sum(row[-1] is None for row in trace)
            for step, row in enumerate(trace, 1):
                for name, value in zip((*inputs, 'expected'), row):
                    constraints.append(f'-set-at {step} {name} {value or 0}')
            proof = f'sat -verify -seq {len(trace)} -prove ok 1 -prove-skip {skip} ' + ' '.join(constraints)
            for mode in ('rtl', 'mapped'):
                with self.subTest(top=top, mode=mode):
                    load = (f'read_verilog -sv {" ".join(map(h.yosys_quote,self.sources[top]))}'
                            if mode == 'rtl' else f'read_json {h.yosys_quote(self.folder/f"{top}.json")}')
                    script = [load, f'read_verilog {h.yosys_quote(wrapper)}',
                              'hierarchy -top check_ff', 'flatten']
                    if mode == 'mapped':
                        script.append('techmap -autoproc -map +/simcells.v')
                    script.extend(['proc', 'clk2fflogic', 'opt_clean', proof])
                    result = subprocess.run(['yosys','-Q','-T','-p','; '.join(script)],
                                            capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                    self.assertIn('SAT proof finished - no model found: SUCCESS!', result.stdout)
