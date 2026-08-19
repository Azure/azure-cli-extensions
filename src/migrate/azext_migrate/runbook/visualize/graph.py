# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Transform a runbook definition/execution JSON document into a DAG model.

This module is **data only** — it contains no HTML and performs no I/O. It
parses the runbook JSON into an in-memory directed acyclic graph (nodes +
edges), validates it (cycle detection, dangling ``dependsOn`` handling) and
computes a stable topological layering so the renderer can lay the graph out
deterministically. Keeping the graph shape free of HTML makes it trivial to
unit-test.
"""

from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_migrate.runbook import deps as dep_utils

logger = get_logger(__name__)

NODE_TYPE_STEP = 'step'


class Node:
    """A single step in the runbook dependency graph."""

    # pylint: disable=too-few-public-methods,too-many-arguments,too-many-instance-attributes
    def __init__(self, node_id, name, node_type=NODE_TYPE_STEP,
                 group=None, status=None, layer=0, ref=None,
                 group_id=None):
        self.id = node_id
        self.name = name
        self.type = node_type
        self.group = group
        self.group_id = group_id
        self.status = status
        self.layer = layer
        self.ref = ref

    def __repr__(self):
        return (
            "Node(id=%r, name=%r, group=%r, status=%r, layer=%r)"
            % (self.id, self.name, self.group, self.status, self.layer))


class Edge:
    """A ``dependsOn`` dependency: ``source`` must finish before ``target``."""

    # pylint: disable=too-few-public-methods
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __repr__(self):
        return "Edge(source=%r, target=%r)" % (self.source, self.target)


class Graph:
    """A layered DAG of runbook steps."""

    # pylint: disable=too-few-public-methods
    def __init__(self, title, nodes, edges, group_order=None):
        self.title = title
        self.nodes = nodes
        self.edges = edges
        # Workstream groups in source-document order (a list of
        # ``(name, group_id)`` pairs). The renderer orders swimlanes by this
        # so the diagram matches the grid; ``nodes`` is separately sorted by
        # dependency layer for column layout.
        self.group_order = group_order or []

    @property
    def layer_count(self):
        return (max((n.layer for n in self.nodes), default=-1) + 1)


def _step_id(step):
    return step.get('id') or step.get('stepId') or step.get('name')


def _step_name(step):
    return (step.get('displayName') or step.get('name')
            or step.get('stepName') or _step_id(step) or 'step')


def _step_status(step):
    status = step.get('status') or step.get('state')
    if isinstance(status, dict):
        status = status.get('state') or status.get('status')
    # Definition steps carry no execution state; fall back to the computed
    # configuration status so the definition DAG colours by readiness.
    return status or step.get('configurationStatus')


def _iter_steps(document):
    """Yield ``(step, workstream_name, workstream_id)`` triples.

    Handles both the ``workstreams[].steps[]`` shape and a flat
    ``steps[]`` shape, and unwraps an execution ``properties`` envelope.
    """
    root = document
    if isinstance(root, dict) and isinstance(root.get('properties'), dict):
        merged = dict(root)
        merged.update(root['properties'])
        root = merged
    if not isinstance(root, dict):
        return
    workstreams = root.get('workstreams') or []
    for workstream in workstreams:
        if not isinstance(workstream, dict):
            continue
        ws_id = workstream.get('id')
        ws_name = (workstream.get('displayName')
                   or workstream.get('name') or ws_id)
        for step in workstream.get('steps', []) or []:
            if isinstance(step, dict):
                yield step, ws_name, ws_id
    for step in root.get('steps', []) or []:
        if isinstance(step, dict):
            yield step, None, None


def _build_graph(document, title):
    nodes = []
    node_by_id = {}
    group_order = []
    seen_groups = set()
    for step, ws_name, ws_id in _iter_steps(document):
        node_id = _step_id(step)
        if not node_id or node_id in node_by_id:
            continue
        node = Node(
            node_id, _step_name(step), group=ws_name, group_id=ws_id,
            status=_step_status(step), ref=step.get('stepRef'))
        nodes.append(node)
        node_by_id[node_id] = node
        group_key = ws_name or 'Ungrouped'
        if group_key not in seen_groups:
            seen_groups.add(group_key)
            group_order.append((group_key, ws_id))

    edges = []
    dependencies = {node.id: [] for node in nodes}
    for step, _, _ in _iter_steps(document):
        node_id = _step_id(step)
        if node_id not in node_by_id:
            continue
        for dep_id in dep_utils.merged_dep_ids(step):
            if dep_id not in node_by_id:
                logger.warning(
                    "Step '%s' depends on unknown step '%s'; ignoring the "
                    "dangling dependency.", node_id, dep_id)
                continue
            edges.append(Edge(dep_id, node_id))
            dependencies[node_id].append(dep_id)

    _assign_layers(nodes, node_by_id, dependencies)
    return Graph(title, nodes, edges, group_order=group_order)


def _assign_layers(nodes, node_by_id, dependencies):
    """Compute a topological layering (Kahn's algorithm), raising on cycles."""
    remaining = dict(dependencies)
    resolved = set()
    order = list(node_by_id)
    progressed = True
    while remaining and progressed:
        progressed = False
        ready = [
            node_id for node_id in order
            if node_id in remaining
            and all(dep in resolved for dep in remaining[node_id])]
        for node_id in ready:
            deps = dependencies[node_id]
            layer = 0
            for dep in deps:
                layer = max(layer, node_by_id[dep].layer + 1)
            node_by_id[node_id].layer = layer
            resolved.add(node_id)
            del remaining[node_id]
            progressed = True
    if remaining:
        raise InvalidArgumentValueError(
            'The runbook dependency graph contains a cycle involving steps: '
            + ', '.join(sorted(remaining)))
    nodes.sort(key=lambda n: (n.layer, n.id))


def build_definition_graph(definition, title='Runbook definition'):
    """Build the DAG for a runbook definition document."""
    return _build_graph(definition or {}, title)


def build_execution_graph(execution, title='Runbook execution'):
    """Build the DAG for a runbook execution document (status-annotated)."""
    return _build_graph(execution or {}, title)
