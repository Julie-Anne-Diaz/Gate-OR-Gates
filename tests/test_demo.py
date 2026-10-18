"""Stopwatch adaptation and reuse of the recorded hex display component."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import hdl_to_minecraft as h

ROOT = Path(__file__).resolve().parents[1]


class HexComponentTests(unittest.TestCase):
    def test_adapter_preserves_catalog_and_restores_each_input(self):
        original = h.load_templates().STANDALONE_GATES['SEVENSEG_HEX']
        blocks, inputs, leads = h.connected_hex_template()
        terminals = {(t.x,t.y,t.z) for t in original.inputs.values()}
        for b in original.blocks:
            p = (b.x,b.y,b.z)
            self.assertEqual(blocks[p], 'minecraft:redstone_wire' if p in terminals else b.state)
        self.assertEqual(set(inputs), {'BIT0','BIT1','BIT2','BIT3'})
        for lead in leads:
            path = lead['path_xyz']
            h.validate_wire_branch(path)
            self.assertEqual(tuple(path[0]), inputs[lead['pin']])
            self.assertIn('repeater', blocks[tuple(path[1])])
            self.assertIn('repeater', blocks[tuple(path[-2])])
            distance = 0
            for i,p in enumerate(path):
                p = tuple(p)
                if i:
                    distance = 0 if 'repeater' in blocks[p] else distance+1
                self.assertLessEqual(distance, 12)
                x,y,z = p
                self.assertIn((x,y-1,z),blocks)
                self.assertNotIn((x,y+1,z),blocks)

    def test_connect_four_bits_and_preserve_coordinate_modes(self):
        net = {'top':'digit', 'gates':[], 'ports':[], 'nets':[]}
        for i in range(4):
            net['ports'] += [{'name':f'd[{i}]','bit':i+2,'direction':'input'},
                             {'name':f'HEX[{i}]','bit':i+2,'direction':'output'}]
            net['nets'].append({'bit':i+2,'source':['port',f'd[{i}]'],'sinks':[['port',f'HEX[{i}]']]})
        # Composition must not accidentally add 'replace' to block states twice.
        for origin,offset in ((None,(3,0,3)), ((10,-59,20),(0,0,0))):
            commands, layout = h.minecraft(net,origin=origin,offset=offset)
            attached, result = h.attach_hex_displays(commands,layout,['HEX'])
            self.assertNotIn('displays',layout)
            self.assertEqual(len(result['displays']),1)
            self.assertEqual(len(result['display_connections']),4)
            self.assertEqual(sum('minecraft:lever[' in c for c in attached),4)
            self.assertTrue(all(c.endswith(' replace') and not c.endswith('replace replace') for c in attached))
            for i,route in enumerate(result['display_connections']):
                self.assertEqual(route['bit'],i+2)
                self.assertEqual(route['sink'],['__display_HEX',f'BIT{i}'])
                h.validate_wire_branch(route['path_xyz'])
            # Existing core blocks retain their exact coordinates and states.
            self.assertTrue(set(commands) <= set(attached))


@unittest.skipUnless(shutil.which('iverilog') and shutil.which('vvp'), 'Icarus unavailable')
class DemoBehaviorTests(unittest.TestCase):
    def test_stopwatch_and_exhaustive_decimal_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory)/'demo.vvp'
            sources = [ROOT/'DEMO'/f for f in ('MINECRAFT_TOP.sv','TOP_LVL.sv','FSM_STOPWATCH.sv',
                       'FSM_STOPWATCH_DATAPATH.sv','tick_gen.sv')]
            result = subprocess.run(['iverilog','-g2012','-s','demo_stopwatch_tb','-o',str(binary),
                *map(str,sources),str(ROOT/'tests/demo_stopwatch_tb.sv')],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result = subprocess.run(['vvp',str(binary)],capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('PASS:',result.stdout)


@unittest.skipUnless(shutil.which('yosys'), 'Yosys unavailable')
class RegisterLegalizationTests(unittest.TestCase):
    def test_preset_is_preserved_using_supported_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder/'preset.sv'
            source.write_text('''module preset(input clk,rst,d,output reg q);
                always @(posedge clk or posedge rst)
                    if (rst) q <= 1'b1; else q <= d;
                endmodule''')
            output = folder/'preset.json'
            h.synthesize([source],'preset',output,legalize_dffs=True)
            net = h.basic_netlist(json.loads(output.read_text()),'preset')
            self.assertEqual([r['reset']['value'] for r in net['registers']],[0])
            h.integrated_clock_netlist(net)  # Must now be physically supported.
            wrapper = folder/'check.sv'
            wrapper.write_text('''module check_preset(input clk,rst,d,output ok);
                wire a,b;
                reference ref_dff(.*,.q(a)); preset mapped(.*,.q(b));
                assign ok = a == b;
                endmodule''')
            script = '; '.join([
                f'read_verilog -sv {h.yosys_quote(source)}', 'rename preset reference',
                f'read_json {h.yosys_quote(output)}', f'read_verilog -sv {h.yosys_quote(wrapper)}',
                'hierarchy -top check_preset', 'flatten', 'techmap -autoproc -map +/simcells.v',
                'proc', 'clk2fflogic', 'opt_clean',
                'sat -verify -seq 12 -prove ok 1 -set-at 1 rst 1 -set-at 1 clk 0'])
            result = subprocess.run(['yosys','-Q','-T','-p',script],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('no model found: SUCCESS!',result.stdout)


if __name__ == '__main__':
    unittest.main()
