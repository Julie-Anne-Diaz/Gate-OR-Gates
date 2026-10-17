"""Geometry/regression tests; these do not simulate Minecraft redstone."""
import unittest

import hdl_to_minecraft as h


def assert_no_unplanned_contacts(test, routes):
    """Check actual spatial adjacency, independently of the router's checks.

    Route metadata describes trees. Touching any non-edge in those trees
    provides a shortcut/feedback path, even when every block is unique.
    Intentional circuitry inside gate templates is not part of these routes.
    """
    points, edges = {}, set()
    for route in routes:
        path = [tuple(p) for p in route['path_xyz']]
        edges.update(frozenset((a,b)) for a,b in zip(path, path[1:]))
        for p in path:
            test.assertIn(points.get(p, route['bit']), [route['bit']])
            points[p] = route['bit']
    for x,y,z in points:
        p = (x,y,z)
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (-1,0,1):
                q = (x+dx,y+dy,z+dz)
                if q in points:
                    test.assertIn(frozenset((p,q)), edges,
                                  f'Unplanned wire contact {p} -> {q}; possible repeater feedback')


class BridgeTests(unittest.TestCase):
    def test_bridge_hairpin_cannot_reconnect_around_repeater(self):
        # Actual turnaround from the half-adder reset bridge. The repeater
        # at (4,3,-4) fed (4,3,-3), which touched the earlier (5,3,-3) wire.
        bad = [(5,3,-3),(5,3,-4),(5,3,-5),(4,3,-5),(4,3,-4),(4,3,-3)]
        for rotation in range(4):
            def rotate(p):
                x,y,z = p
                for _ in range(rotation):
                    x,z = -z,x
                return x,y,z
            with self.subTest(rotation=rotation), self.assertRaisesRegex(h.RoutingError, 'reconnects'):
                h.validate_wire_branch(list(map(rotate, bad)))
        # The same turnaround with a vacant column between parallel legs.
        good = [(5,3,-3),(5,3,-4),(5,3,-5),(4,3,-5),(3,3,-5),(3,3,-4),(3,3,-3)]
        h.validate_wire_branch(good)

    def test_branch_cannot_feed_a_repeater_output_back_into_the_trunk(self):
        # Actual stored-B branch from the half-adder. This bypasses the
        # westbound repeater at (25,0,15) through the trunk at z=14.
        trunk = [(x,0,14) for x in range(17,28)]
        bad = [(26,0,14),(26,0,15),(25,0,15),(24,0,15),(23,1,15)]
        with self.assertRaisesRegex(h.RoutingError, 'reconnects'):
            h.validate_wire_branch(bad, trunk)
        good = [(26,0,14),(26,0,15),(26,0,16),(25,0,16),(24,0,16)]
        h.validate_wire_branch(good, trunk)

    def test_ramp_side_contact_is_rejected_but_vertical_crossing_is_clear(self):
        with self.assertRaisesRegex(h.RoutingError, 'reconnects'):
            h.validate_wire_branch([(0,0,0),(1,0,0),(2,1,0)], {(2,0,1)})
        h.validate_wire_branch([(0,3,0),(1,3,0),(2,3,0)], {(1,0,0)})

    def crossing(self, direction):
        dx, dz = direction
        # Perpendicular lower wire spans the entire bounded routing area.
        signals = {(4*dx-i*dz, 0, 4*dz+i*dx) for i in range(-5, 6)}
        blocks = {p: "minecraft:redstone_wire" for p in signals}
        blocks.update({(x, y-1, z): "minecraft:stone_bricks" for x, y, z in signals})
        air = {(x, y+1, z) for x, y, z in signals}
        blocked = {(px, pz) for x, _, z in signals
                   for px, pz in [(x, z), *h.neighbors((x, z))]}
        end = (8*dx, 8*dz)
        bounds = ((min(0, end[0]), max(0, end[0]), -5, 5) if dx else
                  (-5, 5, min(0, end[1]), max(0, end[1])))
        return end, blocks, air, signals, blocked, bounds

    def test_forced_crossings_in_all_four_directions(self):
        for direction in h.DIRECTIONS:
            with self.subTest(direction=direction):
                end, blocks, air, signals, blocked, bounds = self.crossing(direction)
                with self.assertRaises(h.RoutingError):
                    h.route_wire((0, 0), end, blocked, bounds)
                path = h.route_with_bridges((0, 0), end, blocked, set(), blocks, air, signals, bounds)
                self.assertEqual(path, h.bridge_path((0, 0), direction))
                self.assertEqual(max(y for _, y, _ in path), 3)
                for x, y, z in path:
                    self.assertNotIn((x, y-1, z), air)
                    self.assertNotIn((x, y, z), blocks)
                    for sx, sy, sz in signals:
                        self.assertFalse(abs(x-sx)+abs(z-sz) <= 1 and abs(y-sy) <= 1)

    def test_ramp_cannot_touch_lower_wire(self):
        path = h.bridge_path((0, 0), (1, 0))
        # A lower wire beneath the second ramp step would lose its air gap.
        self.assertFalse(h.bridge_clear(path, {(2, 0, 0): "minecraft:redstone_wire"},
                                        {(2, 1, 0)}, {(2, 0, 0)}, set(), (0, 8, -5, 5)))

    def test_bridge_cannot_cross_gate_or_headroom_obstruction(self):
        path = h.bridge_path((0, 0), (1, 0))
        self.assertFalse(h.bridge_clear(path, {}, set(), set(), {(4, 0)}, (0, 8, -5, 5)))
        self.assertFalse(h.bridge_clear(path, {(4, 4, 0): "minecraft:stone_bricks"},
                                        set(), set(), set(), (0, 8, -5, 5)))

    def test_repeaters_are_flat_and_restore_within_twelve_steps(self):
        path = [(x, 0, 0) for x in range(-20, 0)] + h.bridge_path((0, 0), (1, 0))
        path += [(x, 0, 0) for x in range(9, 35)]
        boosts = h.repeaters_3d(path)
        indices = [0] + sorted(path.index(p) for p in boosts) + [len(path)-1]
        self.assertTrue(all(b-a <= 12 for a, b in zip(indices, indices[1:])))
        for p, direction in boosts.items():
            i = path.index(p)
            self.assertEqual(path[i-1][1], p[1])
            self.assertEqual(p[1], path[i+1][1])
            self.assertEqual(direction, "east")
            self.assertIn("facing=west", h.repeater_state(direction))

    def test_high_bridge_clears_gate_roof_and_restores_power(self):
        path = h.bridge_path((0,0), (1,0), span=20, height=5)
        gate = {(x,1,0): 'minecraft:redstone_wire' for x in range(7,14)}
        obstacles = {(x,z) for x in range(6,15) for z in range(-1,2)}
        self.assertTrue(h.bridge_clear(path, gate, set(), set(gate), obstacles, (0,20,-2,2)))
        boosts = h.repeaters_3d(path)
        self.assertTrue(boosts)
        self.assertTrue(all(p[1] == 5 for p in boosts))
        gate[(10,3,0)] = 'minecraft:stone_bricks'
        self.assertFalse(h.bridge_clear(path, gate, set(), set(), obstacles, (0,20,-2,2)))

    def test_control_tap_is_not_replaced_by_a_repeater(self):
        path = [(0,0,z) for z in range(26)]
        junctions = {(0,0,12), (0,0,23)}
        boosts = h.repeaters_3d(path, junctions=junctions)
        self.assertFalse(set(boosts) & junctions)
        indices = [0] + sorted(path.index(p) for p in boosts) + [len(path)-1]
        self.assertTrue(all(b-a <= 12 for a,b in zip(indices,indices[1:])))

    def test_demo_independent_layers_and_materials(self):
        commands, metadata = h.bridge_demo(origin=(0, -59, 0))
        blocks = {}
        for command in commands:
            tokens = command.split()
            p = tuple(map(int, tokens[1:4]))
            self.assertNotIn(p, blocks)
            blocks[p] = tokens[4]
        self.assertEqual(len(commands), 56)
        self.assertNotIn("minecraft:stone", blocks.values())
        self.assertEqual(min(y for _, y, _ in blocks), -60)
        paths = [r["path_xyz"] for r in metadata["routes"]]
        overlaps = [(a, b) for a in paths[0] for b in paths[1] if (a[0], a[2]) == (b[0], b[2])]
        self.assertTrue(overlaps)
        self.assertTrue(all(abs(a[1]-b[1]) == 3 for a, b in overlaps))
        for route in metadata["routes"]:
            for x, y, z in route["path_xyz"]:
                self.assertIn((x, y-1-59, z), blocks)
                self.assertNotIn((x, y+1-59, z), blocks)


if __name__ == "__main__":
    unittest.main()
