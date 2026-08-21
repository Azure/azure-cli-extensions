# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Basic tests for the `arrange` layout engine.

Deliberately shallow. The layout is experimental and its exact coordinates are expected to change.
"""

import random
import unittest

from azext_health_models._layout import (
    DEFAULT_NODESEP,
    DEFAULT_RANKSEP,
    DEFAULT_NODE_HEIGHT,
    DEFAULT_NODE_WIDTH,
    layered_layout,
)


def _node(node_id, width=100.0, height=50.0):
    return {"id": node_id, "width": width, "height": height}


def _left_to_right(positions, node_ids):
    return sorted(node_ids, key=lambda node_id: positions[node_id]["x"])


class TestLayeredLayout(unittest.TestCase):

    def test_children_are_placed_below_parents_using_portal_spacing(self):
        nodes = [_node(n) for n in ("root", "A", "B", "C")]
        edges = [("root", "A"), ("root", "B"), ("A", "C")]

        positions = layered_layout(nodes, edges)

        self.assertLess(positions["root"]["y"], positions["A"]["y"])
        self.assertLess(positions["A"]["y"], positions["C"]["y"])
        self.assertEqual(positions["A"]["y"], positions["B"]["y"])
        self.assertAlmostEqual(positions["A"]["y"] - positions["root"]["y"], DEFAULT_RANKSEP + 50.0)
        self.assertAlmostEqual(abs(positions["B"]["x"] - positions["A"]["x"]), 100.0 + DEFAULT_NODESEP)

    def test_spacing_and_node_size_can_be_overridden(self):
        nodes = [_node("A"), _node("B"), _node("A1")]
        edges = [("A", "A1")]

        positions = layered_layout(nodes, edges, nodesep=250.0, ranksep=400.0)

        self.assertAlmostEqual(positions["A1"]["y"] - positions["A"]["y"], 400.0 + 50.0)
        self.assertAlmostEqual(abs(positions["B"]["x"] - positions["A"]["x"]), 100.0 + 250.0)

        # Omitted width/height fall back to the portal seed.
        seeded = layered_layout([{"id": "solo"}], [])
        explicit = layered_layout([{"id": "solo", "width": DEFAULT_NODE_WIDTH,
                                    "height": DEFAULT_NODE_HEIGHT}], [])
        self.assertEqual(seeded, explicit)

    def test_awkward_graphs_produce_a_position_for_every_node_without_raising(self):
        cases = {
            "empty": ([], []),
            "single node": (["solo"], []),
            "cycle": (["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]),
            "multiple parents": (["p1", "p2", "child"], [("p1", "child"), ("p2", "child")]),
            "self loop": (["a", "b"], [("a", "a"), ("a", "b")]),
            "edge to unknown node": (["a"], [("a", "ghost")]),
            "isolated plus connected": (["lone", "p", "c"], [("p", "c")]),
        }
        for name, (node_ids, edges) in cases.items():
            with self.subTest(name):
                positions = layered_layout([_node(n) for n in node_ids], edges)

                self.assertEqual(set(positions), set(node_ids))
                for node_id in node_ids:
                    self.assertIsInstance(positions[node_id]["x"], float)
                    self.assertIsInstance(positions[node_id]["y"], float)

    def test_the_same_model_lays_out_the_same_way_whatever_order_it_arrives_in(self):
        # Ids deliberately sort differently from the order declared here.
        node_ids = ["root", "mid_b", "mid_a", "d", "cyc2", "cyc1", "lone", "s2", "s1"]
        edges = [
            ("root", "mid_b"), ("root", "mid_a"),
            ("mid_a", "d"), ("mid_b", "d"),
            ("d", "cyc1"), ("cyc1", "cyc2"), ("cyc2", "cyc1"),
            ("s1", "s2"),
        ]
        baseline = layered_layout([_node(n) for n in node_ids], edges)

        for seed in range(10):
            shuffled_nodes = random.Random(seed).sample(node_ids, len(node_ids))
            shuffled_edges = random.Random(seed + 100).sample(edges, len(edges))
            with self.subTest(seed=seed):
                self.assertEqual(
                    layered_layout([_node(n) for n in shuffled_nodes], shuffled_edges), baseline
                )

    def test_priority_orders_listed_entities_left_to_right_and_leaves_the_rest_alone(self):
        # `b1x` is never listed: it must keep its slot and stay between the listed entities.
        node_ids = ["root", "b1", "b1x", "b2", "b3"]
        edges = [("root", n) for n in ("b1", "b1x", "b2", "b3")]
        nodes = [_node(n) for n in node_ids]

        baseline = layered_layout(nodes, edges)
        self.assertEqual(_left_to_right(baseline, ("b1", "b2", "b3")), ["b1", "b2", "b3"])

        positions = layered_layout(nodes, edges, priority=["b3", "b2", "b1"])

        self.assertEqual(_left_to_right(positions, ("b1", "b2", "b3")), ["b3", "b2", "b1"])
        self.assertEqual(_left_to_right(positions, node_ids[1:]), ["b3", "b1x", "b2", "b1"])

        for seed in range(5):
            shuffled = random.Random(seed).sample(node_ids, len(node_ids))
            with self.subTest(seed=seed):
                shuffled_positions = layered_layout(
                    [_node(n) for n in shuffled], edges, priority=["b3", "b2", "b1"]
                )
                self.assertEqual(_left_to_right(shuffled_positions, ("b1", "b2", "b3")), ["b3", "b2", "b1"])

        for priority in (None, [], ["b2"], ["b1", "ghost"]):
            with self.subTest(priority=priority):
                self.assertEqual(layered_layout(nodes, edges, priority=priority), baseline)


if __name__ == "__main__":
    unittest.main()
