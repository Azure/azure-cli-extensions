# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Command-handler-boundary tests for `monitor health-models arrange` (`health_model_arrange`).

Unlike `test_custom.py` (which calls the pure `_select_subtree`/`_anchor_subtree` helpers
directly, no Azure SDK/mocking), these tests call the PUBLIC command handler itself and patch
the generated AAZ `Entity` `List`, `Relationship` `List`, and `Entity` `Update` classes that
`custom.py` imports as `_EntityList`/`_RelationshipList`/`_EntityUpdate`. This proves the
handler's own wiring - fetch entities/relationships, select/anchor, issue exactly the right
`Update` calls with the right `canvas_position` payload, await every returned poller - rather
than re-proving the selection/anchor algorithms themselves (already covered by `test_custom.py`
and `test_layout.py`).

Fixture entity/relationship dicts mirror the real shape recorded in
`recordings/test_healthmodel_arrange_entity_name_scopes_to_subtree.yaml` (an `id`/`name`/`type`/
`systemData`/`properties` entity, and a `parentEntityName`/`childEntityName` relationship, with
`canvasPosition` an optional key that is simply absent - not `None` - on never-arranged
entities).
"""

import unittest
from unittest import mock

from knack.util import CLIError

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_health_models._layout import DEFAULT_NODE_HEIGHT, DEFAULT_NODE_WIDTH, DEFAULT_NODESEP, DEFAULT_RANKSEP, \
    layered_layout
from azext_health_models.custom import health_model_arrange

_NO_POSITION = object()


def _entity(name, canvas_position=_NO_POSITION):
    properties = {
        "provisioningState": "Succeeded",
        "displayName": "CLI Test Entity",
        "impact": "Standard",
        "healthState": "Unknown",
    }
    if canvas_position is not _NO_POSITION:
        properties["canvasPosition"] = canvas_position
    entity_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rg1/"
        f"providers/microsoft.cloudhealth/healthmodels/model1/entities/{name}"
    )
    return {
        "id": entity_id,
        "name": name,
        "type": "Microsoft.CloudHealth/healthmodels/entities",
        "systemData": {"createdBy": "test@example.com", "createdByType": "User"},
        "properties": properties,
    }


def _relationship(name, parent, child):
    relationship_id = (
        "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rg1/"
        f"providers/microsoft.cloudhealth/healthmodels/model1/relationships/{name}"
    )
    return {
        "id": relationship_id,
        "name": name,
        "type": "Microsoft.CloudHealth/healthmodels/relationships",
        "systemData": {"createdBy": "test@example.com", "createdByType": "User"},
        "properties": {
            "provisioningState": "Succeeded",
            "parentEntityName": parent,
            "childEntityName": child,
        },
    }


def _fake_list_class(items):
    """Stand-in for a generated AAZ `List` class: `SomeList(cli_ctx=...)` returns a callable
    operation, and calling that operation with `command_args=...` returns the canned `items`
    (matching `_EntityList(cli_ctx=cmd.cli_ctx)(command_args={...})`'s real call shape)."""
    operation = mock.MagicMock(name="list_operation")
    operation.return_value = list(items)
    list_class = mock.MagicMock(name="list_class")
    list_class.return_value = operation
    return list_class, operation


def _fake_update_class():
    """Stand-in for the generated AAZ `Entity` `Update` class. Every call records the exact
    `command_args` it was invoked with and returns a fresh fake poller (a `MagicMock` whose
    `.result()` is asserted, mirroring the real `AAZLROPoller` the handler blocks on)."""
    operation = mock.MagicMock(name="update_operation")
    update_class = mock.MagicMock(name="update_class")
    update_class.return_value = operation
    pollers = []

    def _invoke(command_args):
        poller = mock.MagicMock(name=f"poller_for_{command_args['entity_name']}")
        poller.result.return_value = {
            "name": command_args["entity_name"],
            "properties": {"canvasPosition": command_args["canvas_position"]},
        }
        pollers.append(poller)
        return poller

    operation.side_effect = _invoke
    return update_class, operation, pollers


class TestHealthModelArrangeHandlerBoundary(unittest.TestCase):
    """Boundary tests: call `health_model_arrange` itself, patch only the generated AAZ
    `List`/`Update` classes it imports, and assert on the mocked `Update` operation's captured
    call arguments and poller-await behavior."""

    def setUp(self):
        self.cmd = mock.MagicMock(name="cmd")
        self.cmd.cli_ctx = mock.sentinel.cli_ctx
        self.resource_group = "rg1"
        self.health_model_name = "model1"
        # Patch the prompt away by default so the wiring tests stay non-interactive; the
        # confirmation behavior itself is asserted by the dedicated tests below.
        confirmation_patcher = mock.patch("azext_health_models.custom.user_confirmation")
        self.user_confirmation = confirmation_patcher.start()
        self.addCleanup(confirmation_patcher.stop)

    def _patch_aaz(self, entity_list_class, relationship_list_class, update_class):
        for target, replacement in (
            ("azext_health_models.custom._EntityList", entity_list_class),
            ("azext_health_models.custom._RelationshipList", relationship_list_class),
            ("azext_health_models.custom._EntityUpdate", update_class),
        ):
            patcher = mock.patch(target, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    @mock.patch("azext_health_models.custom.logger.warning")
    def test_health_model_arrange_handler_warns_that_layout_is_experimental(self, warning):
        entity_list_class, _ = _fake_list_class([])
        relationship_list_class, _ = _fake_list_class([])
        update_class, update_op, _ = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        health_model_arrange(self.cmd, self.resource_group, self.health_model_name)

        warning.assert_called_once_with(
            "The arrange command is experimental and may produce layouts that differ from the "
            "Azure portal Health Model Designer. It persists canvas positions immediately, and "
            "the CLI has no undo or revert command."
        )
        update_op.assert_not_called()

    def test_health_model_arrange_handler_updates_only_selected_subtree_with_anchored_payloads_and_awaits_pollers(
        self,
    ):
        # Complex topology in one fixture: `root` is anchored at its own existing (0, 0);
        # `mid1`/`mid2` both feed the diamond/multi-parent descendant `deep`; `deep` -> `cyc1`
        # <-> `cyc2` is a cycle reachable from root; `outside_parent` -> `deep` is a
        # cross-boundary edge from a parent OUTSIDE the selection; `sibling_root` ->
        # `sibling_child` is a wholly unrelated disconnected component; `root` -> `mid1` is
        # additionally duplicated as its own relationship object.
        entities = [
            _entity("root", canvas_position={"x": 0.0, "y": 0.0}),
            _entity("mid1"),
            _entity("mid2"),
            _entity("deep"),
            _entity("cyc1"),
            _entity("cyc2"),
            _entity("outside_parent", canvas_position={"x": 999.0, "y": 999.0}),
            _entity("sibling_root", canvas_position={"x": 500.0, "y": 500.0}),
            _entity("sibling_child"),
        ]
        relationships = [
            _relationship("rel-root-mid1", "root", "mid1"),
            _relationship("rel-root-mid2", "root", "mid2"),
            _relationship("rel-mid1-deep", "mid1", "deep"),
            _relationship("rel-mid2-deep", "mid2", "deep"),
            _relationship("rel-deep-cyc1", "deep", "cyc1"),
            _relationship("rel-cyc1-cyc2", "cyc1", "cyc2"),
            _relationship("rel-cyc2-cyc1", "cyc2", "cyc1"),
            _relationship("rel-outside-deep", "outside_parent", "deep"),
            _relationship("rel-sibling", "sibling_root", "sibling_child"),
            _relationship("rel-root-mid1-dup", "root", "mid1"),
        ]

        entity_list_class, entity_list_op = _fake_list_class(entities)
        relationship_list_class, relationship_list_op = _fake_list_class(relationships)
        update_class, update_op, pollers = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        results = health_model_arrange(self.cmd, self.resource_group, self.health_model_name, entity_name="root")

        # Deterministic oracle: the SAME `layered_layout` call the handler itself makes, over
        # the hand-verified correct subtree-only node/edge set (root + every descendant
        # reachable via child edges only; the cross-boundary `outside_parent` edge and the
        # unrelated sibling component are hand-excluded here, independently of the handler,
        # so a handler bug that failed to exclude them would produce a different, non-matching
        # payload below) - then the documented root-anchor delta formula (`existing_root -
        # native_root`, added uniformly to every position) is applied as plain arithmetic, not
        # via a call to `_anchor_subtree`.
        oracle_nodes = [
            {"id": node_id, "width": DEFAULT_NODE_WIDTH, "height": DEFAULT_NODE_HEIGHT}
            for node_id in ("root", "mid1", "mid2", "deep", "cyc1", "cyc2")
        ]
        oracle_edges = [
            ("root", "mid1"), ("root", "mid2"),
            ("mid1", "deep"), ("mid2", "deep"),
            ("deep", "cyc1"), ("cyc1", "cyc2"), ("cyc2", "cyc1"),
            ("root", "mid1"),  # duplicate relationship, mirrored verbatim
        ]
        native = layered_layout(oracle_nodes, oracle_edges, nodesep=DEFAULT_NODESEP, ranksep=DEFAULT_RANKSEP)
        delta_x = 0.0 - native["root"]["x"]
        delta_y = 0.0 - native["root"]["y"]
        expected = {
            node_id: {"x": position["x"] + delta_x, "y": position["y"] + delta_y}
            for node_id, position in native.items()
        }

        # Exact selected update-name set, each updated exactly once, no outside/external
        # updates (cross-boundary parent + wholly unrelated component are never even targeted).
        update_calls = {
            call.kwargs["command_args"]["entity_name"]: call.kwargs["command_args"]
            for call in update_op.call_args_list
        }
        self.assertEqual(update_op.call_count, 6)
        self.assertEqual(set(update_calls), {"root", "mid1", "mid2", "deep", "cyc1", "cyc2"})
        self.assertNotIn("outside_parent", update_calls)
        self.assertNotIn("sibling_root", update_calls)
        self.assertNotIn("sibling_child", update_calls)

        # Exact `canvas_position` payload per updated call: root anchored at (0.0, 0.0)
        # exactly, every descendant strictly below it, uniformly translated by the same delta.
        self.assertEqual(update_calls["root"]["canvas_position"], {"x": 0.0, "y": 0.0})
        for node_id, expected_position in expected.items():
            self.assertAlmostEqual(update_calls[node_id]["canvas_position"]["x"], expected_position["x"])
            self.assertAlmostEqual(update_calls[node_id]["canvas_position"]["y"], expected_position["y"])
        for descendant in ("mid1", "mid2", "deep", "cyc1", "cyc2"):
            self.assertGreater(update_calls[descendant]["canvas_position"]["y"], 0.0)

        # `resource_group`/`health_model_name` are threaded through unchanged on every call.
        for command_args in update_calls.values():
            self.assertEqual(command_args["resource_group"], self.resource_group)
            self.assertEqual(command_args["health_model_name"], self.health_model_name)

        # Every returned poller is awaited (`.result()` called) exactly once, and the
        # handler's own return value threads each poller's result through.
        self.assertEqual(len(pollers), 6)
        for poller in pollers:
            poller.result.assert_called_once()
        self.assertEqual(len(results), 6)

        # List operations ran exactly once each to build the selection.
        self.assertEqual(entity_list_op.call_count, 1)
        self.assertEqual(relationship_list_op.call_count, 1)

    def test_health_model_arrange_handler_falls_back_to_native_positions_when_root_has_no_canvas_position(self):
        # Selected root (`root3`) has no `canvasPosition` at all (the real shape of a
        # never-arranged entity - the key is absent, not `None`).
        entities = [
            _entity("root3"),
            _entity("mid3"),
            _entity("leaf3"),
        ]
        relationships = [
            _relationship("rel-root3-mid3", "root3", "mid3"),
            _relationship("rel-mid3-leaf3", "mid3", "leaf3"),
        ]

        entity_list_class, _ = _fake_list_class(entities)
        relationship_list_class, _ = _fake_list_class(relationships)
        update_class, update_op, pollers = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        health_model_arrange(self.cmd, self.resource_group, self.health_model_name, entity_name="root3")

        # Oracle: the layout's own native, un-translated output (no existing root position to
        # anchor against -> identity fallback, per `_anchor_subtree`'s documented formula).
        oracle_nodes = [
            {"id": node_id, "width": DEFAULT_NODE_WIDTH, "height": DEFAULT_NODE_HEIGHT}
            for node_id in ("root3", "mid3", "leaf3")
        ]
        oracle_edges = [("root3", "mid3"), ("mid3", "leaf3")]
        expected = layered_layout(oracle_nodes, oracle_edges, nodesep=DEFAULT_NODESEP, ranksep=DEFAULT_RANKSEP)

        update_calls = {
            call.kwargs["command_args"]["entity_name"]: call.kwargs["command_args"]
            for call in update_op.call_args_list
        }
        self.assertEqual(set(update_calls), {"root3", "mid3", "leaf3"})
        for node_id, expected_position in expected.items():
            self.assertEqual(update_calls[node_id]["canvas_position"], expected_position)

        self.assertEqual(len(pollers), 3)
        for poller in pollers:
            poller.result.assert_called_once()

    def test_health_model_arrange_handler_raises_before_any_update_for_unknown_entity_name(self):
        entities = [_entity("root4"), _entity("mid4")]
        relationships = [_relationship("rel-root4-mid4", "root4", "mid4")]

        entity_list_class, entity_list_op = _fake_list_class(entities)
        relationship_list_class, relationship_list_op = _fake_list_class(relationships)
        update_class, update_op, pollers = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        with self.assertRaises(InvalidArgumentValueError) as raised:
            health_model_arrange(self.cmd, self.resource_group, self.health_model_name, entity_name="does-not-exist")

        self.assertIn("does-not-exist", str(raised.exception))

        # Zero Update instantiations/calls - the error is raised before any Update is even
        # constructed, let alone invoked.
        self.assertEqual(update_class.call_count, 0)
        self.assertEqual(update_op.call_count, 0)
        self.assertEqual(pollers, [])

        # List operations still occur as expected (entities/relationships are always fetched
        # before the selection/validation step runs).
        self.assertEqual(entity_list_op.call_count, 1)
        self.assertEqual(relationship_list_op.call_count, 1)

    def _arrange_three_entity_chain(self, **kwargs):
        """Wire up a `top -> middle -> bottom` chain and run the handler against it, returning
        the mocked `Update` operation and the captured pollers."""
        entity_list_class, _ = _fake_list_class([_entity("top"), _entity("middle"), _entity("bottom")])
        relationship_list_class, _ = _fake_list_class([
            _relationship("rel-top-middle", "top", "middle"),
            _relationship("rel-middle-bottom", "middle", "bottom"),
        ])
        update_class, update_op, pollers = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        health_model_arrange(self.cmd, self.resource_group, self.health_model_name, **kwargs)
        return update_op, pollers

    @mock.patch("azext_health_models.custom.logger.warning")
    def test_health_model_arrange_handler_lists_every_affected_entity_before_issuing_any_update(self, warning):
        entity_list_class, _ = _fake_list_class([_entity("top"), _entity("middle"), _entity("bottom")])
        relationship_list_class, _ = _fake_list_class([
            _relationship("rel-top-middle", "top", "middle"),
            _relationship("rel-middle-bottom", "middle", "bottom"),
        ])
        update_class, update_op, _ = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        # One shared manager, so "announced and confirmed BEFORE anything was persisted" is
        # proven by call order rather than assumed.
        manager = mock.Mock(name="call_order")
        manager.attach_mock(warning, "warning")
        manager.attach_mock(self.user_confirmation, "confirm")
        manager.attach_mock(update_op, "update")

        health_model_arrange(self.cmd, self.resource_group, self.health_model_name)

        announced = "\n".join(
            call.args[0] % call.args[1:] if len(call.args) > 1 else call.args[0]
            for call in warning.call_args_list
        )
        for name in ("top", "middle", "bottom"):
            self.assertIn(name, announced)
        self.assertIn("3", announced)

        recorded = [name for name, _args, _kwargs in manager.mock_calls]
        self.assertEqual(update_op.call_count, 3)
        first_update = recorded.index("update")
        self.assertLess(max(index for index, name in enumerate(recorded) if name == "warning"), first_update)
        self.assertLess(recorded.index("confirm"), first_update)

    def test_health_model_arrange_handler_persists_nothing_when_the_user_declines(self):
        # Real `user_confirmation` raises exactly this on a "n" answer, and on a missing tty.
        self.user_confirmation.side_effect = CLIError("Operation cancelled.")

        with self.assertRaises(CLIError) as raised:
            self._arrange_three_entity_chain()

        self.assertIn("cancelled", str(raised.exception).lower())

    def test_health_model_arrange_handler_forwards_yes_to_the_confirmation_and_still_persists(self):
        update_op, pollers = self._arrange_three_entity_chain(yes=True)

        self.user_confirmation.assert_called_once()
        self.assertEqual(self.user_confirmation.call_args.kwargs["yes"], True)
        self.assertEqual(update_op.call_count, 3)
        self.assertEqual(len(pollers), 3)

    def test_health_model_arrange_handler_orders_priority_entities_left_to_right(self):
        # Asking for `branch-b` first must flip the persisted x order of root's two children.
        entities = [_entity("root"), _entity("branch-a"), _entity("branch-b")]
        relationships = [
            _relationship("rel-root-a", "root", "branch-a"),
            _relationship("rel-root-b", "root", "branch-b"),
        ]

        def _positions(**kwargs):
            entity_list_class, _ = _fake_list_class(entities)
            relationship_list_class, _ = _fake_list_class(relationships)
            update_class, update_op, _ = _fake_update_class()
            self._patch_aaz(entity_list_class, relationship_list_class, update_class)
            health_model_arrange(self.cmd, self.resource_group, self.health_model_name, yes=True, **kwargs)
            return {
                call.kwargs["command_args"]["entity_name"]: call.kwargs["command_args"]["canvas_position"]
                for call in update_op.call_args_list
            }

        baseline = _positions()
        self.assertLess(baseline["branch-a"]["x"], baseline["branch-b"]["x"])

        prioritized = _positions(priority=["branch-b", "branch-a"])
        self.assertLess(prioritized["branch-b"]["x"], prioritized["branch-a"]["x"])

    def test_health_model_arrange_handler_rejects_invalid_priority_before_any_update(self):
        cases = [
            ("unknown_name", {"priority": ["top", "ghost"]}, "ghost"),
            ("unknown_name_needing_quoting", {"priority": ["top", "no such entity"]}, "no such entity"),
            ("outside_selected_subtree", {"entity_name": "middle", "priority": ["middle", "top"]}, "top"),
            ("duplicate_name", {"priority": ["top", "top"]}, "top"),
        ]
        for name, kwargs, offending in cases:
            with self.subTest(name):
                entity_list_class, _ = _fake_list_class([_entity("top"), _entity("middle"), _entity("bottom")])
                relationship_list_class, _ = _fake_list_class([
                    _relationship("rel-top-middle", "top", "middle"),
                    _relationship("rel-middle-bottom", "middle", "bottom"),
                ])
                update_class, update_op, pollers = _fake_update_class()
                self._patch_aaz(entity_list_class, relationship_list_class, update_class)

                with self.assertRaises(InvalidArgumentValueError) as raised:
                    health_model_arrange(
                        self.cmd, self.resource_group, self.health_model_name, yes=True, **kwargs
                    )

                self.assertIn(offending, str(raised.exception))
                self.assertEqual(update_class.call_count, 0)
                self.assertEqual(update_op.call_count, 0)
                self.assertEqual(pollers, [])

    def test_health_model_arrange_handler_skips_entities_whose_names_the_update_api_rejects(self):
        # Discovery rules produce entities the update API's own `--entity-name` pattern refuses,
        # e.g. a private endpoint NIC's dotted name. Those must be reported and left alone
        # instead of aborting the run halfway through.
        unsupported = "pe-demo-queue.nic.1ae5fd05-41b9-446a-9f77-000000000000"
        entities = [_entity("root"), _entity(unsupported), _entity("leaf")]
        relationships = [
            _relationship("rel-root-pe", "root", unsupported),
            _relationship("rel-pe-leaf", unsupported, "leaf"),
        ]

        entity_list_class, _ = _fake_list_class(entities)
        relationship_list_class, _ = _fake_list_class(relationships)
        update_class, update_op, pollers = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        with mock.patch("azext_health_models.custom.logger.warning") as warning:
            health_model_arrange(self.cmd, self.resource_group, self.health_model_name, yes=True)

        announced = "\n".join(
            call.args[0] % call.args[1:] if len(call.args) > 1 else call.args[0]
            for call in warning.call_args_list
        )
        self.assertIn(unsupported, announced)
        self.assertIn("cannot be repositioned", announced)

        updated = {call.kwargs["command_args"]["entity_name"] for call in update_op.call_args_list}
        self.assertEqual(updated, {"root", "leaf"})
        self.assertEqual(len(pollers), 2)

        # `leaf` is still ranked through the unsupported entity, so the layout used the real
        # graph rather than a pruned one: root -> pe -> leaf puts leaf two ranks down.
        positions = {
            call.kwargs["command_args"]["entity_name"]: call.kwargs["command_args"]["canvas_position"]
            for call in update_op.call_args_list
        }
        self.assertAlmostEqual(positions["leaf"]["y"] - positions["root"]["y"], 362.0)

    def test_health_model_arrange_handler_persists_nothing_when_no_name_is_updatable(self):
        entities = [_entity("first entity"), _entity("second.entity")]

        entity_list_class, _ = _fake_list_class(entities)
        relationship_list_class, _ = _fake_list_class([])
        update_class, update_op, _ = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        results = health_model_arrange(self.cmd, self.resource_group, self.health_model_name)

        self.assertEqual(results, [])
        self.assertEqual(update_op.call_count, 0)
        # Nothing can be written, so the user is never asked to approve a no-op.
        self.user_confirmation.assert_not_called()

    def test_health_model_arrange_handler_accepts_priority_names_needing_shell_quoting(self):
        # Entity names are free-form as far as this handler is concerned; `--priority` must not
        # assume they are simple tokens.
        awkward = ["entity with spaces", "café-entity", "dotted.name", "7bac3c25-400d-57e7-85d1-9a4cd1c34400"]
        entities = [_entity("root")] + [_entity(name) for name in awkward]
        relationships = [_relationship(f"rel-{index}", "root", name) for index, name in enumerate(awkward)]

        entity_list_class, _ = _fake_list_class(entities)
        relationship_list_class, _ = _fake_list_class(relationships)
        update_class, update_op, _ = _fake_update_class()
        self._patch_aaz(entity_list_class, relationship_list_class, update_class)

        health_model_arrange(
            self.cmd, self.resource_group, self.health_model_name, yes=True,
            priority=["7bac3c25-400d-57e7-85d1-9a4cd1c34400", "entity with spaces"],
        )

        # Only the GUID passes the update API's name pattern, but the priority order was still
        # resolved over the full graph without raising.
        updated = {call.kwargs["command_args"]["entity_name"] for call in update_op.call_args_list}
        self.assertEqual(updated, {"root", "7bac3c25-400d-57e7-85d1-9a4cd1c34400"})


if __name__ == "__main__":
    unittest.main()
