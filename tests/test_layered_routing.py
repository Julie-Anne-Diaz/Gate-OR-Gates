"""Electrical-clearance and rollback checks for the complex-circuit router."""
import unittest
from unittest.mock import patch

import hdl_to_minecraft as h
import test_mux as mux
from test_ortools_placement import chain
from test_routing import assert_no_unplanned_contacts


class LayeredRoutingTests(unittest.TestCase):
    def test_forward_search_routes_a_westward_return_over_other_wires(self):
        root = (50, 0, 0)
        lower = {(25, 0, z) for z in range(-20, 51)}
        signals = lower | {root}
        blocks = {p: 'minecraft:redstone_wire' for p in signals}
        blocks.update({(x,y-1,z): 'minecraft:stone_bricks' for x,y,z in signals})
        air = {(x,y+1,z) for x,y,z in signals}
        path, boosts, initial = h.route_in_layers(
            [root], (0,25), {root:0}, set(), blocks, air, signals,
            (-10,60,-20,50), reverse=False, max_states=12000,
            keepouts={(25,z) for z in range(-20,51)}, keepout_height=9, preferred_y=9)
        self.assertEqual(path[0], root)
        self.assertEqual(path[-1], (0,0,25))
        self.assertTrue(all(y >= 9 for x,y,z in path if x == 25))
        assert_no_unplanned_contacts(self, [{'bit':1, 'path_xyz':path}])
        distance = initial
        for i,p in enumerate(path):
            if i:
                distance = 0 if p in boosts else distance+1
            self.assertLessEqual(distance, 12)
            self.assertFalse(any(abs(p[0]-q[0])+abs(p[2]-q[2]) <= 1 and
                                 abs(p[1]-q[1]) <= 1 for q in lower))

    def test_crossings_in_each_direction(self):
        for dx, dz in h.DIRECTIONS:
            with self.subTest(direction=(dx, dz)):
                lower = {(4*dx-i*dz, 0, 4*dz+i*dx) for i in range(-5, 6)}
                root = (0, 0, 0)
                signals = lower | {root}
                blocks = {p: 'minecraft:redstone_wire' for p in signals}
                blocks.update({(x,y-1,z): 'minecraft:stone_bricks' for x,y,z in signals})
                air = {(x,y+1,z) for x,y,z in signals}
                end = (8*dx, 8*dz)
                bounds = ((min(0,end[0]),max(0,end[0]),-5,5) if dx else
                          (-5,5,min(0,end[1]),max(0,end[1])))
                path, boosts, initial = h.route_in_layers(
                    [root], end, {root: 0}, set(), blocks, air, signals, bounds)
                assert_no_unplanned_contacts(self, [{'bit': 1, 'path_xyz': path}])
                self.assertEqual(path[0], root)
                self.assertEqual(path[-1], (end[0],0,end[1]))
                self.assertGreaterEqual(max(p[1] for p in path), 3)
                self.assertEqual(len(path), len(set(path)))
                distance = initial
                supports = {(x,y-1,z) for x,y,z in path}
                headroom = {(x,y+1,z) for x,y,z in path}
                self.assertFalse((supports | set(path)) & headroom)
                for i,p in enumerate(path):
                    if i:
                        prev = path[i-1]
                        self.assertEqual(abs(p[0]-prev[0])+abs(p[2]-prev[2]), 1)
                        self.assertLessEqual(abs(p[1]-prev[1]), 1)
                        distance = 0 if p in boosts else distance+1
                    self.assertLessEqual(distance, 12)
                    self.assertFalse(any(abs(p[0]-q[0])+abs(p[2]-q[2]) <= 1 and
                                         abs(p[1]-q[1]) <= 1 for q in lower))

    def test_reroute_discards_previous_pass_and_preserves_complete_geometry(self):
        net = chain()
        positions = {'g0': (0,0), 'g1': (8,-2)}
        original = h._build_layout_once
        calls = []
        def obstruct_first(*args, **kwargs):
            result = original(*args, **kwargs)
            calls.append(result)
            if len(calls) == 1:
                route = result[1]['routes'][0]
                raise h.NetRoutingError('Injected late conflict', route['bit'],
                                        route['sink'], [r['bit'] for r in result[1]['routes']])
            return result
        with patch.object(h, '_build_layout_once', side_effect=obstruct_first):
            commands, layout = h.build_layout(net, positions, reroute=True)
        self.assertEqual(layout['routing']['reroute_passes'], 1)
        self.assertEqual(layout['routing']['method'], 'rip_up_reroute')
        mux.MuxTests().check_layout(net, commands, layout)

    def test_invalid_templates_are_not_retried_as_congestion(self):
        with patch.object(h, '_build_layout_once', side_effect=ValueError('bad template')) as run:
            with self.assertRaisesRegex(ValueError, 'bad template'):
                h.build_layout(chain(), {'g0': (0,0), 'g1': (8,-2)})
        self.assertEqual(run.call_count, 1)
