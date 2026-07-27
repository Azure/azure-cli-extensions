# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Tests for the pure subtree-selection/anchor-translation helpers backing `monitor
health-models arrange --entity-name`. Both helpers are plain-Python (no Azure SDK/mocking),
matching `test_layout.py`'s black-box convention of asserting only on public return values.

Graph fixture (`_SUBTREE_ENTITIES`/`_SUBTREE_RELATIONSHIPS`) is intentionally non-trivial:
a root with two children that both feed into a single diamond descendant (multi-parent),
a cycle two levels further down, a descendant with a second parent OUTSIDE the subtree
(cross-boundary edge), and an entirely unrelated sibling component - so traversal actually
exercises visited-set dedupe/cycle-safety/edge-filtering rather than only ever seeing a
straight acyclic chain.
"""

import unittest

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_health_models.custom import _anchor_subtree, _select_subtree


def _entity(name):
    return {"name": name}


def _relationship(parent, child):
    return {"properties": {"parentEntityName": parent, "childEntityName": child}}


# root -> mid1, root -> mid2, {mid1, mid2} -> deep (diamond/multi-parent), deep -> cyc1 <-> cyc2
# (cycle), outside_parent -> deep (cross-boundary: deep's second parent lives outside the
# subtree), and a wholly disconnected sibling_root -> sibling_child component.
_SUBTREE_ENTITIES = [
    _entity(name) for name in (
        "root", "mid1", "mid2", "deep", "cyc1", "cyc2",
        "outside_parent", "sibling_root", "sibling_child",
    )
]
_SUBTREE_RELATIONSHIPS = [
    _relationship("root", "mid1"),
    _relationship("root", "mid2"),
    _relationship("mid1", "deep"),
    _relationship("mid2", "deep"),
    _relationship("deep", "cyc1"),
    _relationship("cyc1", "cyc2"),
    _relationship("cyc2", "cyc1"),
    _relationship("outside_parent", "deep"),
    _relationship("sibling_root", "sibling_child"),
]


class TestSelectSubtree(unittest.TestCase):

    def test_select_subtree_includes_root_descendants_diamond_and_cycle_members(self):
        selected_ids, selected_edges = _select_subtree(_SUBTREE_ENTITIES, _SUBTREE_RELATIONSHIPS, "root")

        self.assertEqual(selected_ids, {"root", "mid1", "mid2", "deep", "cyc1", "cyc2"})
        self.assertEqual(
            set(selected_edges),
            {
                ("root", "mid1"), ("root", "mid2"),
                ("mid1", "deep"), ("mid2", "deep"),
                ("deep", "cyc1"), ("cyc1", "cyc2"), ("cyc2", "cyc1"),
            },
        )

    def test_select_subtree_excludes_external_parent_edge_but_keeps_the_shared_descendant(self):
        selected_ids, selected_edges = _select_subtree(_SUBTREE_ENTITIES, _SUBTREE_RELATIONSHIPS, "root")

        # "deep" is still selected (reached via mid1/mid2), but the one-sided cross-boundary
        # edge from its external parent must never appear in the selected edge set, and that
        # external parent itself must never be selected.
        self.assertIn("deep", selected_ids)
        self.assertNotIn("outside_parent", selected_ids)
        self.assertNotIn(("outside_parent", "deep"), selected_edges)

    def test_select_subtree_excludes_the_unrelated_sibling_component_entirely(self):
        selected_ids, selected_edges = _select_subtree(_SUBTREE_ENTITIES, _SUBTREE_RELATIONSHIPS, "root")

        self.assertNotIn("sibling_root", selected_ids)
        self.assertNotIn("sibling_child", selected_ids)
        self.assertNotIn(("sibling_root", "sibling_child"), selected_edges)

    def test_select_subtree_rooted_at_true_leaf_is_single_node_no_edges(self):
        entities = [_entity("solo_root"), _entity("solo_child")]
        relationships = [_relationship("solo_root", "solo_child")]

        selected_ids, selected_edges = _select_subtree(entities, relationships, "solo_child")

        self.assertEqual(selected_ids, {"solo_child"})
        self.assertEqual(selected_edges, [])

    def test_select_subtree_raises_invalid_argument_value_error_for_unknown_root(self):
        with self.assertRaises(InvalidArgumentValueError) as raised:
            _select_subtree(_SUBTREE_ENTITIES, _SUBTREE_RELATIONSHIPS, "does-not-exist")

        self.assertIn("does-not-exist", str(raised.exception))

    def test_select_subtree_on_zero_entity_model_raises_invalid_argument_value_error(self):
        with self.assertRaises(InvalidArgumentValueError):
            _select_subtree([], [], "does-not-exist")


class TestAnchorSubtree(unittest.TestCase):

    def test_anchor_subtree_translates_every_position_so_root_lands_exactly_on_existing_position(self):
        positions = {
            "root": {"x": 0.0, "y": 0.0},
            "mid1": {"x": -50.0, "y": 181.0},
            "mid2": {"x": 50.0, "y": 181.0},
        }
        existing_root_position = {"x": 400.0, "y": 900.0}

        anchored = _anchor_subtree(positions, "root", existing_root_position)

        # Root's final position equals its pre-existing canvasPosition EXACTLY (not merely
        # approximately) - delta is derived from it, so this must be exact float equality.
        self.assertEqual(anchored["root"], {"x": 400.0, "y": 900.0})
        # Same uniform delta (400.0, 900.0) applied to every other selected node too.
        self.assertEqual(anchored["mid1"], {"x": 350.0, "y": 1081.0})
        self.assertEqual(anchored["mid2"], {"x": 450.0, "y": 1081.0})

    def test_anchor_subtree_falls_back_to_native_positions_when_root_has_no_existing_position(self):
        positions = {
            "root": {"x": 0.0, "y": 0.0},
            "mid1": {"x": -50.0, "y": 181.0},
        }

        anchored = _anchor_subtree(positions, "root", None)

        # Identity translation: output equals layered_layout's own raw, un-translated result.
        self.assertEqual(anchored, positions)


if __name__ == "__main__":
    unittest.main()
