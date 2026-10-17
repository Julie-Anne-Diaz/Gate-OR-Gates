"""Clock-enable lowering and instruction traces; no Minecraft physics simulation."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import hdl_to_minecraft as h

ROOT = Path(__file__).resolve().parents[1]


def instruction_trace():
    trace, covered = [], set()
    a = b = out = last_clock = 0

    def sample(clk, rst, in1=0, in2=0, sel=3):
        nonlocal a, b, out, last_clock
        if rst:
            a = b = out = 0
        elif clk and not last_clock:
            covered.add(sel)
            values = {0: a & b, 1: a | b, 2: ~a, 4: a+b, 5: a^b,
                      6: a-b, 7: a << 1, 8: a >> 1, 9: -a,
                      12: a+1, 13: a-1, 14: a}
            if sel in values:
                out = values[sel] & 15
            elif sel == 10:
                a = b
            elif sel == 11:
                a = out
            elif sel == 15:
                a, b = in1, in2
        trace.append((clk, rst, in1, in2, sel, out))
        last_clock = clk

    def cycle(sel, in1=0, in2=0):
        sample(0, 0, in1, in2, sel)
        sample(1, 0, in1, in2, sel)
        sample(1, 0, in1 ^ 15, in2 ^ 15, sel ^ 15)

    sample(0, 1)
    sample(0, 0)
    cycle(15, 3, 5)
    for op in range(10):
        cycle(op)
    for op in (10, 14, 4, 11, 14, 12, 13):
        cycle(op)
    cycle(15, 15, 1)
    for op in (4, 6, 9, 14):
        cycle(op)
    sample(1, 1)
    sample(1, 0)
    cycle(14)
    cycle(15, 9, 6)
    cycle(4)
    assert covered == set(range(16))
    return trace


@unittest.skipUnless(shutil.which('yosys'), 'Yosys executable unavailable')
class RaluTests(unittest.TestCase):
    def test_enabled_registers_and_all_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = ROOT / 'examples/RALU_async.sv'
            output = folder / 'ralu.json'
            h.synthesize([source], 'RALU_async', output)
            net = h.basic_netlist(json.loads(output.read_text()), 'RALU_async')
            self.assertEqual(len(net['registers']), 12)
            self.assertEqual({r['cell_type'] for r in net['registers']}, {'$_DFF_PP0_'})
            physical = h.integrated_clock_netlist(net)
            self.assertEqual(len(physical['clock_bindings']), 1)
            clock = physical['clock_bindings'][0]
            self.assertEqual(len(clock['registers']), 12)
            self.assertEqual(len(physical['placement_cuts']), 12)
            self.assertEqual({(n['bit'], tuple(s)) for n in physical['nets'] for s in n['sinks']},
                             {(n['bit'], tuple(s)) for n in net['nets'] for s in n['sinks']})
            wrapper = folder / 'check.sv'
            wrapper.write_text('''module check_ralu(input clk, rst,
                input [3:0] in1, in2, sel, expected, output ok);
                wire [3:0] value;
                RALU_async dut(.clk(clk), .rst(rst), .in1(in1), .in2(in2), .sel(sel), .out1(value));
                assign ok = value == expected;
                endmodule''')
            trace = instruction_trace()
            constraints = ' '.join(f'-set-at {i} {name} {value}'
                for i, row in enumerate(trace, 1)
                for name, value in zip(('clk','rst','in1','in2','sel','expected'), row))
            for mode in ('rtl', 'mapped'):
                with self.subTest(mode=mode):
                    load = (f'read_verilog -sv {h.yosys_quote(source)}' if mode == 'rtl'
                            else f'read_json {h.yosys_quote(output)}')
                    script = [load, f'read_verilog {h.yosys_quote(wrapper)}',
                              'hierarchy -top check_ralu', 'flatten']
                    if mode == 'mapped':
                        script.append('techmap -autoproc -map +/simcells.v')
                    script.extend(['proc', 'clk2fflogic', 'opt_clean',
                                   f'sat -verify -seq {len(trace)} -prove ok 1 {constraints}'])
                    result = subprocess.run(['yosys', '-Q', '-T', '-p', '; '.join(script)],
                                            capture_output=True, text=True, timeout=45)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn('SAT proof finished - no model found: SUCCESS!', result.stdout)
