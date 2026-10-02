# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Command-handler-boundary tests for `monitor health-models arrange` (`health_model_arrange`).

These call the PUBLIC command handler and patch the generated AAZ `Entity` `List`,
`Relationship` `List` and `Entity` `Update` classes that `custom.py` imports as
`_EntityList`/`_RelationshipList`/`_EntityUpdate`. They prove the handler's own wiring - fetch,
select, anchor, partition names, confirm, then issue exactly the right `Update` calls and await
every poller - rather than re-proving the layout itself, which `test_layout.py` covers.

Fixture entity/relationship dicts mirror the shape recorded in
`recordings/test_healthmodel_arrange_entity_name_scopes_to_subtree.yaml`, where `canvasPosition`
is an optional key that is simply absent - not `None` - on a never-arranged entity.
"""

import unittest
from unittest import mock

from knack.util import CLIError

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_health_models._layout import DEFAULT_NODE_HEIGHT, DEFAULT_NODE_WIDTH, DEFAULT_NODESEP, DEFAULT_RANKSEP, \
    layered_layout
from azext_health_models.custom import health_model_arrange

_NO_POSITION = object()

# `root` -> `mid1`/`mid2` both feed the multi-parent descendant `deep`; `deep` -> `cyc1` <->
# `cyc2` is a cycle reachable from root; `outside_parent` -> `deep` is a cross-boundary edge
# from a parent OUTSIDE the selection; `sibling_root` -> `sibling_child` is a wholly unrelated
# disconnected component; `root` -> `mid1` is additionally duplicated as its own relationship.
_SUBTREE_IDS = ("root", "mid1", "mid2", "deep", "cyc1", "cyc2")
_SUBTREE_EDGES = [
    ("root", "mid1"), ("root", "mid2"),
    ("mid1", "deep"), ("mid2", "deep"),
    ("deep", "cyc1"), ("cyc1", "cyc2"), ("cyc2", "cyc1"),
    ("root", "mid1"),
]
_OUTSIDE_EDGES = [("outside_parent", "deep"), ("sibling_root", "sibling_child")]

_UNSUPPORTED_NIC = "pe-demo-queue.nic.1ae5fd05-41b9-446a-9f77-000000000000"
_UNSUPPORTED_SPACES = "entity with spaces"

_CHAIN_ENTITY_NAMES = ("top", "middle", "bottom")
_CHAIN_EDGES = [("top", "middle"), ("middle", "bottom")]


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


def _relationships(edges):
    return [
        {
            "id": (
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rg1/"
                f"providers/microsoft.cloudhealth/healthmodels/model1/relationships/rel-{index}"
            ),
            "name": f"rel-{index}",
            "type": "Microsoft.CloudHealth/healthmodels/relationships",
            "systemData": {"createdBy": "test@example.com", "createdByType": "User"},
            "properties": {
                "provisioningState": "Succeeded",
                "parentEntityName": parent,
                "childEntityName": child,
            },
        }
        for index, (parent, child) in enumerate(edges)
    ]


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


def _native_layout(node_ids, edges):
    """The layout the handler itself computes for a given node/edge set, used as this module's
    oracle so the assertions below test the handler's selection and anchoring rather than
    re-deriving coordinates `test_layout.py` already covers."""
    nodes = [
        {"id": node_id, "width": DEFAULT_NODE_WIDTH, "height": DEFAULT_NODE_HEIGHT}
        for node_id in node_ids
    ]
    return layered_layout(nodes, edges, nodesep=DEFAULT_NODESEP, ranksep=DEFAULT_RANKSEP)


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
        # confirmation behavior itself is asserted by the dedicated test below.
        confirmation_patcher = mock.patch("azext_health_models.custom.user_confirmation")
        self.user_confirmation = confirmation_patcher.start()
        self.addCleanup(confirmation_patcher.stop)

    def _patch_aaz(self, entities, relationships):
        """Patch the three generated AAZ classes with canned data, returning the mocked
        `Update` operation and the pollers it hands back."""
        entity_list_class, _ = _fake_list_class(entities)
        relationship_list_class, _ = _fake_list_class(relationships)
        update_class, update_op, pollers = _fake_update_class()
        for target, replacement in (
            ("azext_health_models.custom._EntityList", entity_list_class),
            ("azext_health_models.custom._RelationshipList", relationship_list_class),
            ("azext_health_models.custom._EntityUpdate", update_class),
        ):
            patcher = mock.patch(target, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)
        return update_class, update_op, pollers

    @staticmethod
    def _captured_args(update_op):
        return {
            call.kwargs["command_args"]["entity_name"]: call.kwargs["command_args"]
            for call in update_op.call_args_list
        }

    @staticmethod
    def _announced(warning):
        return "\n".join(
            call.args[0] % call.args[1:] if len(call.args) > 1 else call.args[0]
            for call in warning.call_args_list
        )

    def test_arrange_scopes_to_the_subtree_and_anchors_it_on_the_root(self):
        # The anchor delta is the only thing that differs between a root that already has a
        # `canvasPosition` and one that has never been arranged, so both run the same topology.
        for name, root_position in (
            ("root already positioned", {"x": 0.0, "y": 0.0}),
            ("root never arranged", _NO_POSITION),
        ):
            with self.subTest(name):
                entities = [_entity("root", root_position)]
                entities += [_entity(node_id) for node_id in _SUBTREE_IDS[1:]]
                entities += [
                    _entity("outside_parent", {"x": 999.0, "y": 999.0}),
                    _entity("sibling_root", {"x": 500.0, "y": 500.0}),
                    _entity("sibling_child"),
                ]
                _update_class, update_op, pollers = self._patch_aaz(
                    entities, _relationships(_SUBTREE_EDGES + _OUTSIDE_EDGES)
                )

                results = health_model_arrange(
                    self.cmd, self.resource_group, self.health_model_name, entity_name="root"
                )

                # Oracle: the layout over the hand-verified subtree-only node/edge set (the
                # cross-boundary and unrelated-component edges are excluded here independently
                # of the handler), then the documented anchor delta as plain arithmetic.
                native = _native_layout(_SUBTREE_IDS, _SUBTREE_EDGES)
                anchored = root_position is not _NO_POSITION
                delta_x = -native["root"]["x"] if anchored else 0.0
                delta_y = -native["root"]["y"] if anchored else 0.0

                update_calls = self._captured_args(update_op)
                self.assertEqual(set(update_calls), set(_SUBTREE_IDS))
                for node_id, position in native.items():
                    canvas_position = update_calls[node_id]["canvas_position"]
                    self.assertAlmostEqual(canvas_position["x"], position["x"] + delta_x)
                    self.assertAlmostEqual(canvas_position["y"], position["y"] + delta_y)
                if anchored:
                    self.assertEqual(update_calls["root"]["canvas_position"], {"x": 0.0, "y": 0.0})

                # `resource_group`/`health_model_name` are threaded through unchanged, and
                # every returned poller is awaited exactly once.
                for command_args in update_calls.values():
                    self.assertEqual(command_args["resource_group"], self.resource_group)
                    self.assertEqual(command_args["health_model_name"], self.health_model_name)
                self.assertEqual(len(results), len(_SUBTREE_IDS))
                for poller in pollers:
                    poller.result.assert_called_once()

    def test_arrange_skips_names_the_update_api_rejects_but_still_lays_out_the_real_graph(self):
        # Discovery rules produce entities the update API's own `--entity-name` pattern refuses,
        # e.g. a private endpoint NIC's dotted name. Those must be reported and left alone
        # instead of aborting the run halfway through - while still ranking their descendants.
        entities = [_entity(name) for name in (
            "root", _UNSUPPORTED_NIC, _UNSUPPORTED_SPACES, "alpha", "beta", "leaf",
        )]
        edges = [
            ("root", _UNSUPPORTED_NIC), (_UNSUPPORTED_NIC, "leaf"),
            ("root", _UNSUPPORTED_SPACES), ("root", "alpha"), ("root", "beta"),
        ]
        _update_class, update_op, pollers = self._patch_aaz(entities, _relationships(edges))

        with mock.patch("azext_health_models.custom.logger.warning") as warning:
            health_model_arrange(
                self.cmd, self.resource_group, self.health_model_name, yes=True,
                priority=[_UNSUPPORTED_SPACES, "beta", "alpha"],
            )

        announced = self._announced(warning)
        self.assertIn("cannot be repositioned", announced)
        self.assertIn(_UNSUPPORTED_NIC, announced)
        self.assertIn(_UNSUPPORTED_SPACES, announced)

        update_calls = self._captured_args(update_op)
        self.assertEqual(set(update_calls), {"root", "alpha", "beta", "leaf"})
        self.assertEqual(len(pollers), 4)

        positions = {name: args["canvas_position"] for name, args in update_calls.items()}
        # `leaf` is still ranked through the skipped NIC, so the layout ran over the real graph
        # rather than a pruned one: root -> nic -> leaf puts leaf two ranks down.
        self.assertAlmostEqual(positions["leaf"]["y"] - positions["root"]["y"], 362.0)
        # The handler forwarded `--priority` to the layout, and a name the update API rejects
        # is still usable as a priority entry rather than raising.
        self.assertLess(positions["beta"]["x"], positions["alpha"]["x"])

    def test_arrange_announces_and_confirms_before_persisting_anything(self):
        cases = [
            ("confirmed", _CHAIN_ENTITY_NAMES, _CHAIN_EDGES, {"yes": True}, None, 3, True),
            ("declined", _CHAIN_ENTITY_NAMES, _CHAIN_EDGES, {}, CLIError("Operation cancelled."), 0, True),
            ("no updatable name", ("first entity", "second.entity"), [], {}, None, 0, False),
            ("empty model", (), [], {}, None, 0, False),
        ]
        for name, entity_names, edges, kwargs, decline, expected_updates, expects_prompt in cases:
            with self.subTest(name):
                self.user_confirmation.reset_mock()
                self.user_confirmation.side_effect = decline
                _update_class, update_op, _pollers = self._patch_aaz(
                    [_entity(entity_name) for entity_name in entity_names], _relationships(edges)
                )

                with mock.patch("azext_health_models.custom.logger.warning") as warning:
                    # One shared manager, so "announced and confirmed BEFORE anything was
                    # persisted" is proven by call order rather than assumed.
                    manager = mock.Mock(name="call_order")
                    manager.attach_mock(warning, "warning")
                    manager.attach_mock(self.user_confirmation, "confirm")
                    manager.attach_mock(update_op, "update")

                    if decline is not None:
                        with self.assertRaises(CLIError) as raised:
                            health_model_arrange(
                                self.cmd, self.resource_group, self.health_model_name, **kwargs
                            )
                        self.assertIn("cancelled", str(raised.exception).lower())
                    else:
                        results = health_model_arrange(
                            self.cmd, self.resource_group, self.health_model_name, **kwargs
                        )
                        self.assertEqual(len(results), expected_updates)

                self.assertEqual(update_op.call_count, expected_updates)
                self.assertEqual(self.user_confirmation.called, expects_prompt)
                if expected_updates:
                    self.assertEqual(self.user_confirmation.call_args.kwargs["yes"], True)
                    announced = self._announced(warning)
                    for entity_name in entity_names:
                        self.assertIn(entity_name, announced)
                    recorded = [call_name for call_name, _args, _kwargs in manager.mock_calls]
                    first_update = recorded.index("update")
                    self.assertLess(recorded.index("confirm"), first_update)
                    self.assertLess(
                        max(index for index, call_name in enumerate(recorded) if call_name == "warning"),
                        first_update,
                    )

    def test_arrange_rejects_bad_arguments_before_issuing_any_update(self):
        cases = [
            ("unknown entity_name", {"entity_name": "does-not-exist"}, "does-not-exist"),
            ("unknown priority name", {"priority": ["top", "ghost"]}, "ghost"),
            ("unknown priority name needing quoting", {"priority": ["top", "no such entity"]}, "no such entity"),
            ("priority outside selected subtree", {"entity_name": "middle", "priority": ["middle", "top"]}, "top"),
            ("duplicate priority name", {"priority": ["top", "top"]}, "top"),
        ]
        for name, kwargs, offending in cases:
            with self.subTest(name):
                update_class, update_op, pollers = self._patch_aaz(
                    [_entity(entity_name) for entity_name in _CHAIN_ENTITY_NAMES],
                    _relationships(_CHAIN_EDGES),
                )

                with self.assertRaises(InvalidArgumentValueError) as raised:
                    health_model_arrange(
                        self.cmd, self.resource_group, self.health_model_name, yes=True, **kwargs
                    )

                self.assertIn(offending, str(raised.exception))
                # No Update is even constructed, let alone invoked.
                self.assertEqual(update_class.call_count, 0)
                self.assertEqual(update_op.call_count, 0)
                self.assertEqual(pollers, [])


if __name__ == "__main__":
    unittest.main()
