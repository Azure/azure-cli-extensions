# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_health_models._layout import (
    DEFAULT_NODESEP,
    DEFAULT_RANKSEP,
    layered_layout,
)


def _node(node_id, width=100.0, height=50.0):
    return {"id": node_id, "width": width, "height": height}


def _rank_extent_mid(positions, node_ids):
    """(min + max) / 2 of the given nodes' final x — the "occupied x-extent midpoint" the
    corrected blueprint's centerline criteria assert on. Operates on the public function's
    output (top-left x), never on internals, matching the file's black-box test convention.
    """
    xs = [positions[node_id]["x"] for node_id in node_ids]
    return (min(xs) + max(xs)) / 2.0


class TestLayeredLayout(unittest.TestCase):

    def test_layout_matches_dagre_defaults(self):
        # Two roots (A, B) each with one child in the next rank; with default nodesep/ranksep
        # this proves: (1) rank grouping - children strictly below parents, (2) in-rank
        # ordering - siblings placed at distinct x positions, (3) spacing - the gap between
        # A and B's centers equals width + nodesep (portal default 50), and the gap between a
        # rank's top and the next rank's top equals height + ranksep (portal default 100).
        nodes = [_node("A"), _node("B"), _node("A1"), _node("B1")]
        edges = [("A", "A1"), ("B", "B1")]

        positions = layered_layout(nodes, edges)

        # Rank grouping: A/B share a rank (top), A1/B1 share the next rank, strictly below.
        self.assertEqual(positions["A"]["y"], positions["B"]["y"])
        self.assertEqual(positions["A1"]["y"], positions["B1"]["y"])
        self.assertGreater(positions["A1"]["y"], positions["A"]["y"])

        # Rank spacing: consecutive ranks are separated by ranksep + the rank's node height.
        self.assertAlmostEqual(positions["A1"]["y"] - positions["A"]["y"], DEFAULT_RANKSEP + 50.0)

        # In-rank ordering/spacing: same-rank siblings are offset by width + nodesep.
        gap = abs(positions["B"]["x"] - positions["A"]["x"])
        self.assertAlmostEqual(gap, 100.0 + DEFAULT_NODESEP)

    def test_layout_preserves_rank_hierarchy_for_three_level_tree(self):
        # root -> {mid1, mid2} -> {leaf1, leaf2, leaf3}; every child's y must be strictly
        # greater than every one of its parents' y (top-to-bottom hierarchy preserved).
        nodes = [_node(n) for n in ("root", "mid1", "mid2", "leaf1", "leaf2", "leaf3")]
        edges = [
            ("root", "mid1"), ("root", "mid2"),
            ("mid1", "leaf1"), ("mid1", "leaf2"),
            ("mid2", "leaf3"),
        ]

        positions = layered_layout(nodes, edges)

        self.assertLess(positions["root"]["y"], positions["mid1"]["y"])
        self.assertLess(positions["root"]["y"], positions["mid2"]["y"])
        self.assertLess(positions["mid1"]["y"], positions["leaf1"]["y"])
        self.assertLess(positions["mid1"]["y"], positions["leaf2"]["y"])
        self.assertLess(positions["mid2"]["y"], positions["leaf3"]["y"])
        # root is the unique minimum-y (topmost) node.
        self.assertEqual(min(p["y"] for p in positions.values()), positions["root"]["y"])

    def test_layout_handles_isolated_node_and_empty_graph_without_raising(self):
        cases = [
            ("isolated_node", [_node("solo")], []),
            ("empty_graph", [], []),
        ]
        for name, nodes, edges in cases:
            with self.subTest(name):
                positions = layered_layout(nodes, edges)
                if not nodes:
                    self.assertEqual(positions, {})
                else:
                    self.assertIn("solo", positions)
                    self.assertIsInstance(positions["solo"]["x"], float)
                    self.assertIsInstance(positions["solo"]["y"], float)

    def test_layout_respects_custom_spacing_over_defaults(self):
        nodes = [_node("A"), _node("B"), _node("A1")]
        edges = [("A", "A1")]
        custom_nodesep, custom_ranksep = 250.0, 400.0

        default_positions = layered_layout(nodes, edges)
        custom_positions = layered_layout(nodes, edges, nodesep=custom_nodesep, ranksep=custom_ranksep)

        default_rank_gap = default_positions["A1"]["y"] - default_positions["A"]["y"]
        custom_rank_gap = custom_positions["A1"]["y"] - custom_positions["A"]["y"]
        self.assertAlmostEqual(custom_rank_gap, custom_ranksep + 50.0)
        self.assertNotAlmostEqual(custom_rank_gap, default_rank_gap)

        default_sibling_gap = abs(default_positions["B"]["x"] - default_positions["A"]["x"])
        custom_sibling_gap = abs(custom_positions["B"]["x"] - custom_positions["A"]["x"])
        self.assertAlmostEqual(custom_sibling_gap, 100.0 + custom_nodesep)
        self.assertNotAlmostEqual(custom_sibling_gap, default_sibling_gap)

    def test_layout_uses_portal_measured_seed_for_omitted_dimensions_and_respects_overrides(self):
        # Human-adjudicated correction (blueprint Decisions/User feedback): "Use Portal seed
        # 200x81 (Recommended)". `ModelActionsSlice.ts` initializes every V2/V3 health entity
        # with `measured: { width: 200, height: 81 }`, and `.react-flow__node` separately
        # fixes `width: 200px` in `_designer-blade.scss` - two independent subsystems
        # corroborating 200 for width. Height (81) is that same initial *measured seed*. not
        # a fixed CSS rule; ReactFlow may replace it with a runtime-measured value once
        # content is rendered. The CLI has no DOM, so 81 is the best Portal-sourced headless
        # default for height, superseding the prior 36 approximation - not a claim that 81 is
        # a guaranteed final DOM height. Omitting a node's "width"/"height" must fall back to
        # this seed; supplying explicit values (as `--node-width`/`--node-height` forward
        # through `custom.py`/`layered_layout`) must still override it, since these are
        # defaults, not hardcoded constants.
        edges = [("P", "A"), ("P", "B")]
        cases = [
            (
                "dimensions_omitted_use_portal_200x81_measured_seed",
                [{"id": "P"}, {"id": "A"}, {"id": "B"}],
                200.0,
                81.0,
            ),
            (
                "explicit_dimensions_override_the_seed",
                [
                    {"id": "P", "width": 300.0, "height": 120.0},
                    {"id": "A", "width": 300.0, "height": 120.0},
                    {"id": "B", "width": 300.0, "height": 120.0},
                ],
                300.0,
                120.0,
            ),
        ]
        for name, nodes, expected_width, expected_height in cases:
            with self.subTest(name):
                positions = layered_layout(nodes, edges)
                horizontal_gap = abs(positions["B"]["x"] - positions["A"]["x"])
                vertical_gap = positions["A"]["y"] - positions["P"]["y"]
                self.assertAlmostEqual(horizontal_gap, expected_width + DEFAULT_NODESEP)
                self.assertAlmostEqual(vertical_gap, expected_height + DEFAULT_RANKSEP)

    def test_layout_does_not_hang_on_cycles_and_multiple_parents(self):
        # A <-> B is a direct cycle; C has two parents (A and B). A naive recursive/tree-only
        # implementation could loop forever or crash; this must terminate deterministically
        # and give every node a well-defined position.
        nodes = [_node("A"), _node("B"), _node("C")]
        edges = [("A", "B"), ("B", "A"), ("A", "C"), ("B", "C")]

        positions = layered_layout(nodes, edges)

        self.assertEqual(set(positions), {"A", "B", "C"})
        for position in positions.values():
            self.assertIsInstance(position["x"], float)
            self.assertIsInstance(position["y"], float)
        # C has an incoming edge from both A and B, so it must not be above either of them.
        self.assertGreaterEqual(positions["C"]["y"], positions["A"]["y"])
        self.assertGreaterEqual(positions["C"]["y"], positions["B"]["y"])

        # Re-running with the same input is deterministic (no reliance on set/dict ordering
        # instability).
        repeat_positions = layered_layout(nodes, edges)
        self.assertEqual(positions, repeat_positions)

    # ------------------------------------------------------------------
    # CORRECTED primary criteria: whole-graph "middle center" (single shared
    # centerline across every real-connected rank; disconnected nodes excluded
    # from that centerline's extent computation). See blueprint
    # 2026-07-24-centered-health-model-arrange.blueprint.md, corrected Acceptance
    # criteria section.
    # ------------------------------------------------------------------

    def test_layout_shares_one_centerline_across_all_ranks(self):
        # Screenshot-mirroring shape: root -> A,B,C,D (uneven fan-out: only A and
        # both C and D have children; B has none), and cd has two real parents
        # (C, D). Every rank's real-connected extent midpoint must land on one
        # shared graph centerline, and root (rank 0's only node) must sit there
        # too - not merely at its own-rank-only local median.
        nodes = [_node(n) for n in ("root", "A", "B", "C", "D", "a1", "cd")]
        edges = [
            ("root", "A"), ("root", "B"), ("root", "C"), ("root", "D"),
            ("A", "a1"), ("C", "cd"), ("D", "cd"),
        ]

        positions = layered_layout(nodes, edges)

        rank0_mid = _rank_extent_mid(positions, ["root"])
        rank1_mid = _rank_extent_mid(positions, ["A", "B", "C", "D"])
        rank2_mid = _rank_extent_mid(positions, ["a1", "cd"])

        self.assertAlmostEqual(rank0_mid, rank1_mid)
        self.assertAlmostEqual(rank1_mid, rank2_mid)
        # Root itself sits exactly on the shared centerline (it IS rank 0's only
        # node, so this restates rank0_mid == rank1_mid, but asserted directly on
        # the node the human's screenshot called out as "centered over the full
        # span").
        self.assertAlmostEqual(positions["root"]["x"], rank1_mid)
        # NOTE: this shape's rank1 is 4-wide (A,B,C,D) while cd's real parents
        # are only the inner pair (C, D) - the primary whole-graph centerline
        # (this test) and "a multi-parent node sits at its real parents' mean"
        # (see test_layout_aligns_node_to_real_edge_median_not_positional_index)
        # can genuinely disagree on a shape like this, per the blueprint's own
        # Self-challenge. The human's correction ("supersedes a merely local
        # edge-aware nudge") means the shared-centerline outcome wins here;
        # cd's own real-parent-mean guarantee is proven separately on shapes
        # (2-node ranks) where the two goals do not conflict.

    def test_layout_excludes_disconnected_node_from_rank_extent_normalization(self):
        # G -> F is a fully disconnected component from root's tree, but
        # _assign_ranks's longest-path/Kahn rule still lands F in rank 1
        # alongside real children A,B,C,D. F must not skew where rank 1's real
        # connected content (A,B,C,D) is centered relative to root/rank2.
        connected_nodes = [_node(n) for n in ("root", "A", "B", "C", "D", "a1", "cd")]
        connected_edges = [
            ("root", "A"), ("root", "B"), ("root", "C"), ("root", "D"),
            ("A", "a1"), ("C", "cd"), ("D", "cd"),
        ]
        disconnected_nodes = connected_nodes + [_node("G"), _node("F")]
        disconnected_edges = connected_edges + [("G", "F")]

        positions_without_gf = layered_layout(connected_nodes, connected_edges)
        positions_with_gf = layered_layout(disconnected_nodes, disconnected_edges)

        # The disconnected component's mere presence must not move any
        # main-component node - the strongest possible "does not distort" proof.
        for node_id in ("root", "A", "B", "C", "D", "a1", "cd"):
            self.assertAlmostEqual(
                positions_with_gf[node_id]["x"], positions_without_gf[node_id]["x"],
                msg=f"{node_id} shifted when an unrelated disconnected component was added",
            )
            self.assertAlmostEqual(
                positions_with_gf[node_id]["y"], positions_without_gf[node_id]["y"]
            )

        # Rank 1's real-connected-only extent midpoint (excluding F) still shares
        # the graph's centerline.
        rank1_connected_mid = _rank_extent_mid(positions_with_gf, ["A", "B", "C", "D"])
        self.assertAlmostEqual(rank1_connected_mid, positions_with_gf["root"]["x"])

    def test_layout_isolated_node_keeps_own_position_and_does_not_shift_other_components(self):
        # Decision (recorded in the blueprint's Decisions table): a fully
        # isolated node (zero edges anywhere) is its own single-rank component -
        # there is nothing for it to share a centerline with, so it is excluded
        # from every other component's extent-normalization AND is not itself
        # forced onto the main component's centerline. It keeps whatever x its
        # own local left-to-right packing/nodesep-enforcement produced (here:
        # immediately to the right of whatever real node shares its rank, since
        # nodesep must still be enforced between unrelated same-rank nodes).
        base_nodes = [_node(n) for n in ("root", "A", "B", "C")]
        base_edges = [("root", "A"), ("root", "B"), ("root", "C")]
        isolated_nodes = base_nodes + [_node("E")]

        positions_without_e = layered_layout(base_nodes, base_edges)
        positions_with_e = layered_layout(isolated_nodes, base_edges)

        for node_id in ("root", "A", "B", "C"):
            self.assertAlmostEqual(
                positions_with_e[node_id]["x"], positions_without_e[node_id]["x"],
                msg=f"{node_id} shifted when an isolated zero-edge node was added",
            )

        # E shares rank 0 with root and must stay nodesep-separated from it
        # (deterministic spacing enforcement), but is never pulled toward the
        # children's centerline itself since it has no real edges to anyone.
        self.assertAlmostEqual(
            positions_with_e["E"]["x"], positions_with_e["root"]["x"] + 100.0 + DEFAULT_NODESEP
        )

    # ------------------------------------------------------------------
    # SUPERSEDED-AS-PRIMARY (still-required supporting/local criteria): each
    # node's neighbor lookup must use real edges, not a positional-index proxy
    # across adjacent ranks of possibly-different sizes.
    # ------------------------------------------------------------------

    def test_layout_centers_root_over_children_group(self):
        # 1 root fanning out to 3 children (odd count, so median == mean,
        # avoiding a false ambiguity between the two conventions).
        nodes = [_node(n) for n in ("root", "A", "B", "C")]
        edges = [("root", "A"), ("root", "B"), ("root", "C")]

        positions = layered_layout(nodes, edges)

        self.assertAlmostEqual(positions["root"]["x"], 150.0)

    def test_layout_centers_narrower_rank_on_wider_adjacent_rank_extent(self):
        # 1 root fanning out to 5 children: root's own rank is narrower than the
        # child rank's occupied extent, so root must center on that extent
        # ((min_x + max_x) / 2 = 300.0 under default spacing), not left-anchor
        # at x=0.
        nodes = [_node(n) for n in ("root", "A", "B", "C", "D", "E")]
        edges = [("root", n) for n in ("A", "B", "C", "D", "E")]

        positions = layered_layout(nodes, edges)

        self.assertAlmostEqual(positions["root"]["x"], 300.0)

    def test_layout_aligns_node_to_real_edge_median_not_positional_index(self):
        # Parameterized: both cases assert a node's x tracks the median/mean of
        # its REAL parents, not whichever node merely shares its positional
        # column index in the adjacent rank.
        cases = [
            (
                "diamond_plus_unrelated_node",
                [_node(n) for n in ("A", "B", "C", "D", "E")],
                [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")],
                lambda p: self.assertAlmostEqual(p["D"]["x"], (p["B"]["x"] + p["C"]["x"]) / 2.0),
            ),
            (
                "single_real_parent_with_unrelated_sibling",
                [_node(n) for n in ("A", "B", "C")],
                [("B", "C")],
                lambda p: self.assertAlmostEqual(p["C"]["x"], p["B"]["x"]),
            ),
        ]
        for name, nodes, edges, check in cases:
            with self.subTest(name):
                check(layered_layout(nodes, edges))


# A -> {b1, bx, b2, b3} -> {E1, Ex, E2, E3}. `bx`/`Ex` are never listed in `priority`, so they
# are what proves interleaving. Node/edge order is chosen so the UNCONSTRAINED layout settles on
# the exact reverse of the order asserted below - the constrained assertions cannot pass
# vacuously. See LAYOUT.md "Priority ordering".
_PRIORITY_NODES = [_node(n) for n in ("A", "b1", "bx", "b2", "b3", "E1", "Ex", "E2", "E3")]
_PRIORITY_EDGES = [
    ("A", "b1"), ("A", "bx"), ("A", "b2"), ("A", "b3"),
    ("b1", "E1"), ("bx", "Ex"), ("b2", "E2"), ("b3", "E3"),
]


def _left_to_right(positions, node_ids):
    return sorted(node_ids, key=lambda node_id: positions[node_id]["x"])


class TestLayeredLayoutPriority(unittest.TestCase):

    def test_priority_reverses_relative_order_while_non_listed_entities_keep_their_slots(self):
        baseline = layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES)
        # Guard: a no-op implementation cannot pass the constrained assertions below.
        self.assertEqual(_left_to_right(baseline, ("b1", "bx", "b2", "b3")), ["b1", "bx", "b2", "b3"])
        self.assertEqual(_left_to_right(baseline, ("E1", "Ex", "E2", "E3")), ["E1", "Ex", "E2", "E3"])

        positions = layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES, priority=["E3", "E2", "E1"])

        self.assertLess(positions["E3"]["x"], positions["E2"]["x"])
        self.assertLess(positions["E2"]["x"], positions["E1"]["x"])
        self.assertLess(positions["b3"]["x"], positions["b2"]["x"])
        self.assertLess(positions["b2"]["x"], positions["b1"]["x"])
        # `bx`/`Ex` keep their own slot, so they still sit BETWEEN listed entities.
        self.assertEqual(_left_to_right(positions, ("b1", "bx", "b2", "b3")), ["b3", "bx", "b2", "b1"])
        self.assertEqual(_left_to_right(positions, ("E1", "Ex", "E2", "E3")), ["E3", "Ex", "E2", "E1"])

    def test_priority_leaves_the_common_ancestor_rank_and_omitted_case_untouched(self):
        baseline = layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES)
        constrained = layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES, priority=["E3", "E2", "E1"])

        # The common ancestor's own rank is never reordered.
        self.assertAlmostEqual(constrained["A"]["x"], baseline["A"]["x"])
        self.assertEqual(layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES, priority=None), baseline)
        self.assertEqual(layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES, priority=[]), baseline)
        self.assertEqual(layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES, priority=["E2"]), baseline)

    def test_priority_orders_disconnected_entities_that_share_no_common_ancestor(self):
        # No common ancestor exists, so the virtual-super-root fallback applies.
        nodes = [_node(n) for n in ("r1", "r2", "P1", "P2")]
        edges = [("r1", "P1"), ("r2", "P2")]

        baseline = layered_layout(nodes, edges)
        self.assertLess(baseline["r1"]["x"], baseline["r2"]["x"])

        positions = layered_layout(nodes, edges, priority=["P2", "P1"])

        self.assertLess(positions["P2"]["x"], positions["P1"]["x"])
        self.assertLess(positions["r2"]["x"], positions["r1"]["x"])

    def test_priority_between_an_ancestor_and_its_own_descendant_is_a_harmless_no_op(self):
        # No rank below `A` holds two constrained nodes, so the layout must be unchanged.
        positions = layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES, priority=["E1", "A"])

        self.assertEqual(positions, layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES))

    def test_priority_picks_the_same_path_regardless_of_relationship_input_order(self):
        # `target` is reachable via either `hop_a` or `hop_b` - two equally short paths. With
        # an unsorted traversal, permuting the edge list moves them between x=412 and x=262;
        # asserting on the whole position dict is what makes this test discriminating.
        nodes = [_node(n) for n in ("anc", "hop_a", "hop_b", "target", "other", "sibling")]
        edges = [
            ("anc", "hop_a"), ("anc", "hop_b"),
            ("hop_a", "target"), ("hop_b", "target"),
            ("anc", "other"), ("other", "sibling"),
        ]
        orderings = [edges, list(reversed(edges)), [edges[1], edges[0]] + edges[2:]]

        layouts = [
            layered_layout(nodes, ordering, priority=["sibling", "target"])
            for ordering in orderings
        ]

        self.assertEqual(layouts[0], layouts[1])
        self.assertEqual(layouts[0], layouts[2])
        # Pin the ambiguous hops explicitly - they are what actually moves.
        for layout in layouts[1:]:
            self.assertEqual(layout["hop_a"]["x"], layouts[0]["hop_a"]["x"])
            self.assertEqual(layout["hop_b"]["x"], layouts[0]["hop_b"]["x"])

    def test_priority_ignores_ids_that_are_not_in_the_node_set(self):
        # Rejecting unknown names is the command handler's job, not the layout's.
        positions = layered_layout(_PRIORITY_NODES, _PRIORITY_EDGES, priority=["E3", "ghost", "E1"])

        self.assertLess(positions["E3"]["x"], positions["E1"]["x"])
        self.assertNotIn("ghost", positions)


if __name__ == "__main__":
    unittest.main()
