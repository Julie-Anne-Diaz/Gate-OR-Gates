"""The optional CP-SAT placer must still pass the real Minecraft router."""
import builtins
import importlib.util
import unittest
from unittest.mock import patch

import hdl_to_minecraft as h


def chain():
    return h.basic_netlist({'modules': {'chain': {
        'ports': {'a': {'direction': 'input', 'bits': [2]},
                  'b': {'direction': 'input', 'bits': [3]},
                  'c': {'direction': 'input', 'bits': [4]},
                  'y': {'direction': 'output', 'bits': [6]}},
        'cells': {'g0': {'type': '$_AND_', 'connections': {'A': [2], 'B': [3], 'Y': [5]}},
                  'g1': {'type': '$_AND_', 'connections': {'A': [4], 'B': [5], 'Y': [6]}}}
    }}}, 'chain')


class OptionalDependencyTests(unittest.TestCase):
    def test_adjacent_sink_is_not_blocked_by_its_own_source(self):
        _, layout = h.build_layout(chain(), {'g0': (0, 0), 'g1': (8, -2)})
        link = next(r for r in layout['routes'] if r['source'] == ['g0', 'Y'])
        self.assertEqual(link['path_xyz'], [(6, 0, 1), (6, 0, 0)])
        self.assertEqual(link['bridge_count'], 0)

    def test_missing_required_ortools_is_actionable(self):
        original = builtins.__import__
        def unavailable(name, *args, **kwargs):
            if name == 'ortools' or name.startswith('ortools.'):
                raise ImportError('not installed')
            return original(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=unavailable):
            with self.assertRaisesRegex(ValueError, 'pip install -r requirements.txt'):
                h.minecraft(chain())


@unittest.skipUnless(importlib.util.find_spec('ortools'), 'optional OR-Tools is not installed')
class OrtoolsTests(unittest.TestCase):
    def test_parallel_workers_and_timing(self):
        commands, layout = h.minecraft(chain(), solver_workers=8)
        self.assertTrue(commands)
        self.assertTrue(layout['placement']['routing_validated'])
        self.assertEqual(layout['placement']['solver_workers'], 8)
        self.assertGreaterEqual(layout['placement']['routing_seconds'], 0)
        for workers in (0, -1, 1.5, True):
            with self.subTest(workers=workers), self.assertRaisesRegex(ValueError, 'positive integer'):
                h.minecraft(chain(), solver_workers=workers)

    def test_chain_connections_materials_and_relative_coordinates(self):
        commands, layout = h.minecraft(chain(), placer='ortools')
        self.assertEqual(len(commands), 62)
        self.assertEqual(layout['placement']['solver_workers'], 1)
        self.assertEqual(layout['placement']['method'], 'ortools_cp_sat')
        self.assertEqual(layout['placement']['solver_status'], 'OPTIMAL')
        self.assertEqual(layout['placement']['wire_steps'], 0)
        self.assertTrue(layout['placement']['routing_validated'])
        self.assertTrue(all(c.startswith('execute at @s align xyz run setblock ~') for c in commands))
        self.assertTrue(all('minecraft:stone ' not in c for c in commands))
        link = next(r for r in layout['routes'] if r['source'][0] != 'port' and r['sink'][0] != 'port')
        self.assertEqual(len(link['path_xyz']), 1)

    def test_failed_route_retries_solver_with_more_space(self):
        original, calls = h.build_layout, []
        def route(*args, **kwargs):
            calls.append(args[1])
            if len(calls) == 1:
                raise h.RoutingError('test blocked initial candidate')
            return original(*args, **kwargs)
        with patch.object(h, 'build_layout', side_effect=route):
            _, layout = h.minecraft(chain(), placer='ortools')
        attempts = layout['placement']['attempts']
        self.assertEqual(attempts[0]['routing_error'], 'test blocked initial candidate')
        self.assertEqual(attempts[1]['extra_column_gap'], 4)

    def test_no_silent_custom_fallback(self):
        with patch.object(h, 'build_layout', side_effect=h.RoutingError('blocked')):
            with self.assertRaisesRegex(h.RoutingError, 'No custom fallback was exported'):
                h.minecraft(chain(), placer='ortools')

    def test_absolute_floor_and_invalid_time_budget(self):
        commands, _ = h.minecraft(chain(), placer='ortools', origin=(0, -59, 0))
        self.assertEqual(min(int(c.split()[2]) for c in commands), -60)
        for budget in (0, -1, float('nan'), float('inf')):
            with self.subTest(budget=budget), self.assertRaisesRegex(ValueError, 'finite positive'):
                h.minecraft(chain(), placer='ortools', solver_seconds=budget)


if __name__ == '__main__':
    unittest.main()
