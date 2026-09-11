# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Manual (non-generated) command layer for `az monitor health-models`.

Adds `monitor health-models arrange`, which recomputes entity canvas positions with an
experimental layered/hierarchical layout based on the Azure Portal Health Model Designer's
"Arrange" behavior (see `_layout.py`), then persists each position through the extension's
existing entity-update path (`--canvas-position`), the same field the portal writes.
"""

from collections import defaultdict

from knack.log import get_logger

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import user_confirmation

from ._layout import DEFAULT_NODE_HEIGHT, DEFAULT_NODE_WIDTH, DEFAULT_NODESEP, DEFAULT_RANKSEP, layered_layout
from .aaz.latest.monitor.health_models.entity import List as _EntityList
from .aaz.latest.monitor.health_models.entity import Update as _EntityUpdate
from .aaz.latest.monitor.health_models.relationship import List as _RelationshipList

logger = get_logger(__name__)


def _select_subtree(entities, relationships, entity_name):
    """Select `entity_name` plus every descendant reachable along `parentEntityName` ->
    `childEntityName` edges, using an iterative visited-set traversal (same safe-on-cycles/
    safe-on-multiple-parents style as `_layout.py`'s `_remove_cycles`/`_assign_ranks`: no
    recursion, a node is only ever added to the selected set once, and the visited check
    alone prevents re-traversal/infinite loops without ever excluding an already-reached
    cycle member).

    A descendant that also has a parent OUTSIDE the selection is still included (reachability
    is purely outgoing-edge traversal from the root; an extra incoming edge from outside never
    blocks or removes a node already reached via an in-selection path); the returned edge list
    is filtered to only edges whose parent AND child are both selected, so that one-sided
    cross-boundary relationship is dropped from the layout's connectivity graph while its
    external endpoint is never selected (and therefore never persisted).

    :param entities: iterable of entity dicts with a `"name"` key.
    :param relationships: iterable of relationship dicts with
        `properties.parentEntityName`/`properties.childEntityName`.
    :param entity_name: name of the subtree's root entity.
    :return: (selected_ids: set[str], selected_edges: list[(parent, child)]).
    :raises InvalidArgumentValueError: if `entity_name` does not match any entity in `entities`.
    """
    if not any(entity["name"] == entity_name for entity in entities):
        raise InvalidArgumentValueError(
            f"Entity '{entity_name}' was not found in this health model. Use "
            "'az monitor health-models entity list' to see the available entity names."
        )

    children = defaultdict(list)
    for relationship in relationships:
        parent = relationship["properties"]["parentEntityName"]
        child = relationship["properties"]["childEntityName"]
        children[parent].append(child)

    selected_ids = set()
    stack = [entity_name]
    while stack:
        node_id = stack.pop()
        if node_id in selected_ids:
            continue
        selected_ids.add(node_id)
        for child_id in children.get(node_id, ()):
            if child_id not in selected_ids:
                stack.append(child_id)

    selected_edges = [
        (relationship["properties"]["parentEntityName"], relationship["properties"]["childEntityName"])
        for relationship in relationships
        if relationship["properties"]["parentEntityName"] in selected_ids
        and relationship["properties"]["childEntityName"] in selected_ids
    ]
    return selected_ids, selected_edges


def _anchor_subtree(positions, root_id, existing_root_position):
    """Translate every position in `positions` by the uniform delta that makes `root_id`'s
    final position exactly equal `existing_root_position` (human-adjudicated Option A:
    anchor the arranged subtree at the selected root's own existing `canvasPosition`).

    If `existing_root_position` is absent (the root has never been positioned), no delta can
    be anchored against; fall back to identity translation, returning `positions` unchanged -
    the layout's own native result, the same no-offset behavior full-model `arrange` already
    produces today.

    :param positions: {node_id: {"x": float, "y": float}}, e.g. `layered_layout`'s own output.
    :param root_id: the selected subtree's root node id (must be a key in `positions`).
    :param existing_root_position: the root's pre-existing {"x", "y"} `canvasPosition`, or
        `None`/falsy if it has none.
    :return: {node_id: {"x": float, "y": float}} - a new dict, uniformly translated.
    """
    if not existing_root_position:
        return positions

    delta_x = existing_root_position["x"] - positions[root_id]["x"]
    delta_y = existing_root_position["y"] - positions[root_id]["y"]
    return {
        node_id: {"x": position["x"] + delta_x, "y": position["y"] + delta_y}
        for node_id, position in positions.items()
    }


def _updatable_name_pattern():
    """The regex `entity update` enforces on `--entity-name`, read from the generated AAZ schema
    so it cannot drift from the command this handler actually calls. Returns `None` if the
    schema shape changes, in which case the caller treats every name as updatable and lets the
    update call raise on its own.
    """
    try:
        # pylint: disable=protected-access
        return _EntityUpdate._build_arguments_schema().entity_name._fmt._compiled_pattern
    except AttributeError:
        return None


_UPDATABLE_NAME_PATTERN = _updatable_name_pattern()


def _partition_by_updatable_name(entity_names):
    """Split entity names into those `entity update` will accept and those it will reject.

    Discovery rules can create entities whose names contain characters the update API's own
    argument pattern refuses (a private endpoint NIC's dotted name, for example). Without this
    split, arrange would persist part of the model and then abort on the first such entity.

    :return: (updatable, skipped), preserving input order.
    """
    if _UPDATABLE_NAME_PATTERN is None:
        return list(entity_names), []

    updatable, skipped = [], []
    for name in entity_names:
        (updatable if _UPDATABLE_NAME_PATTERN.match(name) else skipped).append(name)
    return updatable, skipped


def _validate_priority(priority, arranged_names, entity_name):
    """Reject `--priority` values this arrange could never order: a repeated name, or a name
    that is not among the entities being arranged.

    :raises InvalidArgumentValueError: naming the offending value.
    """
    seen = set()
    for name in priority:
        if name in seen:
            raise InvalidArgumentValueError(f"Entity '{name}' is listed more than once in '--priority'.")
        seen.add(name)
        if name not in arranged_names:
            scope = (
                f"the subtree scoped by '--entity-name {entity_name}'" if entity_name is not None
                else "this health model"
            )
            raise InvalidArgumentValueError(
                f"Priority entity '{name}' was not found in {scope}. Use "
                "'az monitor health-models entity list' to see the available entity names."
            )


def health_model_arrange(cmd, resource_group, health_model_name, entity_name=None, priority=None, yes=False,
                         node_width=DEFAULT_NODE_WIDTH, node_height=DEFAULT_NODE_HEIGHT,
                         node_sep=DEFAULT_NODESEP, rank_sep=DEFAULT_RANKSEP):
    """Recompute and persist canvas positions for every entity in a health model, using an
    experimental layered/hierarchical layout based on the Azure Portal Health Model Designer's
    "Arrange" behavior (whole-graph scope, top-to-bottom, default spacing nodesep=50/ranksep=100).

    If `entity_name` is given, scope the arrange to that entity's subtree (itself plus every
    descendant reachable via `parentEntityName` -> `childEntityName` edges) instead of the
    whole model: only the selected entities are laid out/persisted, cross-boundary edges to
    entities outside the selection are excluded from the layout, and the result is translated
    so the selected root's new position exactly matches its own pre-existing `canvasPosition`
    (or is left at the layout's native, un-translated result if it had none). Every entity
    outside the selection is left completely untouched - no computation, no update call.

    If `priority` is given, those entities' branches are forced into that left-to-right order;
    see LAYOUT.md.

    Every entity that will be repositioned is listed before anything is persisted, and the
    caller must confirm unless `yes` is set.
    """
    logger.warning(
        "The arrange command is experimental and may produce layouts that differ from the "
        "Azure portal Health Model Designer. It persists canvas positions immediately, and "
        "the CLI has no undo or revert command."
    )

    entities = list(_EntityList(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group,
        "health_model_name": health_model_name,
    }))
    relationships = list(_RelationshipList(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group,
        "health_model_name": health_model_name,
    }))

    if entity_name is not None:
        selected_ids, edges = _select_subtree(entities, relationships, entity_name)
        entities_to_arrange = [entity for entity in entities if entity["name"] in selected_ids]
    else:
        entities_to_arrange = entities
        edges = [
            (relationship["properties"]["parentEntityName"], relationship["properties"]["childEntityName"])
            for relationship in relationships
        ]

    arranged_names = [entity["name"] for entity in entities_to_arrange]
    if priority:
        _validate_priority(priority, set(arranged_names), entity_name)

    updatable_names, skipped_names = _partition_by_updatable_name(arranged_names)

    if skipped_names:
        logger.warning(
            "%d %s cannot be repositioned because the entity update API rejects their names, "
            "and will be left where they are:\n  %s",
            len(skipped_names),
            "entity" if len(skipped_names) == 1 else "entities",
            "\n  ".join(skipped_names),
        )

    if not updatable_names:
        return []

    logger.warning(
        "This arrange will update the canvas position of %d %s:\n  %s",
        len(updatable_names),
        "entity" if len(updatable_names) == 1 else "entities",
        "\n  ".join(updatable_names),
    )
    user_confirmation("Do you want to continue?", yes=yes)

    # Layout still runs over the whole selection, including skipped entities, so the entities
    # that do get written are placed relative to the real graph rather than a pruned one.
    nodes = [{"id": entity["name"], "width": node_width, "height": node_height} for entity in entities_to_arrange]
    positions = layered_layout(nodes, edges, nodesep=node_sep, ranksep=rank_sep, priority=priority)

    if entity_name is not None:
        existing_root_position = next(
            (entity["properties"].get("canvasPosition") for entity in entities if entity["name"] == entity_name),
            None,
        )
        positions = _anchor_subtree(positions, entity_name, existing_root_position)

    skipped = set(skipped_names)
    results = []
    for entity in entities_to_arrange:
        current_entity_name = entity["name"]
        if current_entity_name in skipped:
            continue
        position = positions.get(current_entity_name)
        if position is None:
            # Defensive only: every entity was passed into `nodes` above, so `_layout` always
            # returns a position for it unless the model has zero entities (in which case this
            # loop does not execute at all).
            logger.warning("No computed position for entity '%s'; skipping.", current_entity_name)
            continue
        poller = _EntityUpdate(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": resource_group,
            "health_model_name": health_model_name,
            "entity_name": current_entity_name,
            "canvas_position": {"x": position["x"], "y": position["y"]},
        })
        # Entity update is a long-running operation (`AAZLROPoller`, backed by a daemon
        # thread); without waiting for `.result()` the process could return - and, in a
        # short-lived CLI invocation, exit - before the PUT actually completes, silently
        # dropping the write. Block here so every entity's new position is durably persisted
        # before `arrange` reports success.
        results.append(poller.result())
    return results
