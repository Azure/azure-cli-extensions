# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Pure-Python re-implementation of the layered/hierarchical directed-graph layout used by the
Azure Portal Health Model Designer's "Arrange" feature.

The portal implements "Arrange" with Dagre (`@dagrejs/dagre` 3.0.0): rank assignment ->
in-rank ordering -> coordinate assignment, always top-to-bottom (``TB``) with default spacing
``nodesep=50, ranksep=100``, run over the whole canvas graph, then converts Dagre's per-node
*center* point to a top-left ``position`` by subtracting half the node's width/height.

This module implements the same class of algorithm natively in Python (no Node.js/
``@dagrejs/dagre`` runtime dependency, consistent with this repository's convention of zero
heavyweight runtime dependencies for CLI extensions) so it can run inside the ``az`` CLI
process. It intentionally reproduces the same three-stage pipeline and default parameters
rather than falling back to a naive/generic tree layout:

  1. ``_remove_cycles``: DFS-based feedback-arc-set removal (back edges - i.e. edges to a
     node already on the active DFS stack - are reversed), so relationship cycles (allowed by
     the schema, since nothing prevents two entities from each listing the other as
     parent/child) cannot cause an infinite loop or an ill-defined rank order.
  2. ``_assign_ranks``: longest-path ranking computed with an iterative Kahn topological sort
     (bounded by O(V+E), no recursion - deterministic and safe for large graphs).
  3. ``_order_ranks`` / ``_assign_coordinates``: median-heuristic in-rank ordering (a bounded
     number of alternating up/down sweeps) followed by coordinate assignment using
     ``nodesep``/``ranksep`` and a median-alignment pass, then the same center-to-top-left
     conversion the portal's adapter performs.

Reference (read prior to authoring this module - not vendored, cited for traceability):
  AHM-CloudHealth-Portal/src/Extension/Client/ReactViews/Blades/DesignerBlade/ReactFlowNodes/
    AutoLayout/DagreLayoutAlgorithm.ts (dagre graph setup + center->top-left conversion)
  .../AutoLayout/AutoLayoutUtils.ts (`AutoArrangeNodes`: empty-input no-op, whole-graph scope)
  .../AutoLayout/AutoLayoutDefaults.ts (`DefaultDirection="TB"`, `DefaultSpacing=[50,100]`)
"""

from collections import defaultdict, deque
from functools import partial

# Portal defaults (AutoLayoutDefaults.ts): direction is always "TB"; spacing is [nodesep, ranksep].
DEFAULT_NODESEP = 50.0
DEFAULT_RANKSEP = 100.0

# Human-adjudicated default (blueprint Decisions/User feedback): "Use Portal seed 200x81
# (Recommended)". Width is a stable, fixed CSS constant - `.react-flow__node { width:
# 200px; }` in `_designer-blade.scss` - constant across V2/V3 and every node state/entity
# type, independently corroborated by `ModelActionsSlice.ts`'s own `measured?.width ?? 200`
# fallback; callers can still override it via `--node-width`. Height has no analogous fixed
# CSS rule - it is the initial value `ModelActionsSlice.ts` seeds onto every V2/V3 health
# entity's `measured` state (`measured: { width: 200, height: 81 }`), not a guaranteed final
# DOM height: ReactFlow may later replace `measured.height` with a runtime-measured value
# once the card's actual content (display-name wrapping, footer/badges) is rendered, which
# the headless CLI has no DOM to reproduce. 81 is therefore the best Portal-sourced seed for
# height available without a live DOM measurement - not a fixed/CSS-final height - and
# remains overridable via `--node-height` for callers who know their model's real rendered
# size (see blueprint 2026-07-24-portal-health-card-sizes.blueprint.md).
DEFAULT_NODE_WIDTH = 200.0
DEFAULT_NODE_HEIGHT = 81.0


def layered_layout(nodes, edges, nodesep=DEFAULT_NODESEP, ranksep=DEFAULT_RANKSEP,
                   x_offset=0.0, y_offset=0.0, priority=None):
    """Compute top-left {x, y} canvas positions for a directed graph using a layered,
    rank-based (Dagre-equivalent) layout: rank assignment -> in-rank ordering -> coordinate
    assignment, top-to-bottom, matching the Azure Portal Health Model Designer's "Arrange".

    :param nodes: iterable of {"id": str, "width": float, "height": float}.
    :param edges: iterable of (source_id, target_id) tuples (parent -> child).
    :param nodesep: horizontal space between nodes in the same rank (portal default: 50).
    :param ranksep: vertical space between ranks (portal default: 100).
    :param x_offset: added to every computed x (portal adapter's optional `xOffset`).
    :param y_offset: added to every computed y (portal adapter's optional `yOffset`).
    :param priority: optional node ids in the left-to-right order they must appear in; see
        LAYOUT.md. Unknown ids are ignored.
    :return: {node_id: {"x": float, "y": float}}. Empty input -> empty result (no-op), matching
        `AutoArrangeNodes`'s early return for zero nodes.
    """
    node_list = list(nodes)
    if not node_list:
        return {}

    node_ids = [n["id"] for n in node_list]
    widths = {n["id"]: n.get("width", DEFAULT_NODE_WIDTH) or 0.0 for n in node_list}
    heights = {n["id"]: n.get("height", DEFAULT_NODE_HEIGHT) or 0.0 for n in node_list}
    known_ids = set(node_ids)

    adjacency = defaultdict(list)
    for source, target in edges:
        # Ignore edges that reference a node outside the supplied node set (defensive: keeps
        # the layout well-defined even if a caller passes a relationship whose entity was
        # filtered out) and self-loop edges, which cannot affect rank ordering.
        if source == target or source not in known_ids or target not in known_ids:
            continue
        adjacency[source].append(target)

    acyclic_edges = _remove_cycles(node_ids, adjacency)
    ranks = _assign_ranks(node_ids, acyclic_edges)
    max_rank = max(ranks.values()) if ranks else 0
    constraints = _priority_rank_constraints(node_ids, acyclic_edges, ranks, priority)
    rank_nodes = _order_ranks(node_ids, ranks, acyclic_edges, max_rank, constraints)
    x_pos, y_pos = _assign_coordinates(
        rank_nodes, widths, heights, nodesep, ranksep, max_rank, acyclic_edges
    )

    # Dagre returns each node's center point; the portal's adapter converts to a top-left
    # `position` by subtracting half the node's width/height (plus optional offsets). Mirror
    # that here so callers can write the result straight into `properties.canvasPosition`.
    positions = {}
    for node_id in node_ids:
        positions[node_id] = {
            "x": x_pos[node_id] - widths[node_id] / 2.0 + x_offset,
            "y": y_pos[node_id] - heights[node_id] / 2.0 + y_offset,
        }
    return positions


def _remove_cycles(node_ids, adjacency):
    """DFS-based feedback-arc-set removal. Edges to a node currently on the active DFS stack
    ("back edges") are reversed rather than dropped, so the relationship still informs
    ranking/ordering while guaranteeing the resulting edge set is acyclic. Implemented
    iteratively (explicit stack, no recursion) so it cannot hang or overflow the recursion
    limit on large or cyclic graphs.
    """
    white, gray, black = 0, 1, 2
    color = {node_id: white for node_id in node_ids}
    acyclic_edges = []

    for start in node_ids:
        if color[start] != white:
            continue
        color[start] = gray
        stack = [(start, iter(adjacency.get(start, [])))]
        while stack:
            node, neighbors = stack[-1]
            advanced = False
            for target in neighbors:
                if color[target] == white:
                    color[target] = gray
                    acyclic_edges.append((node, target))
                    stack.append((target, iter(adjacency.get(target, []))))
                    advanced = True
                    break
                if color[target] == gray:
                    # Back edge - reverse it to break the cycle instead of dropping it.
                    acyclic_edges.append((target, node))
                else:
                    acyclic_edges.append((node, target))
            if not advanced:
                stack.pop()
                color[node] = black
    return acyclic_edges


def _assign_ranks(node_ids, acyclic_edges):
    """Longest-path rank assignment via an iterative Kahn topological sort: rank(root) = 0;
    rank(child) = max(rank(parent) + 1) over all of its incoming edges. Guarantees every
    child's rank is strictly greater than every one of its parents' ranks (strict top-to-bottom
    hierarchy), including nodes with multiple parents.
    """
    children = defaultdict(list)
    indegree = {node_id: 0 for node_id in node_ids}
    for source, target in acyclic_edges:
        children[source].append(target)
        indegree[target] += 1

    remaining = dict(indegree)
    rank = {node_id: 0 for node_id in node_ids}
    queue = deque(node_id for node_id in node_ids if indegree[node_id] == 0)
    processed = 0

    while queue:
        node = queue.popleft()
        processed += 1
        for child in children[node]:
            if rank[child] < rank[node] + 1:
                rank[child] = rank[node] + 1
            remaining[child] -= 1
            if remaining[child] == 0:
                queue.append(child)

    if processed < len(node_ids):
        # Defensive only: _remove_cycles guarantees an acyclic edge set, so this should be
        # unreachable. Assign any leftover node its already-computed (default 0) rank rather
        # than raising, keeping the function total and hang-proof.
        for node_id in node_ids:
            if node_id not in rank:
                rank[node_id] = 0
    return rank


def _median(values):
    if not values:
        return None
    values = sorted(values)
    count = len(values)
    mid = count // 2
    if count % 2 == 1:
        return float(values[mid])
    if count == 2:
        return (values[0] + values[1]) / 2.0
    left = values[mid - 1] - values[0]
    right = values[-1] - values[mid]
    if left + right == 0:
        return (values[mid - 1] + values[mid]) / 2.0
    return (values[mid - 1] * right + values[mid] * left) / (left + right)


def _ordering_sort_key(medians, position, node_id):
    """Sort key for `_order_ranks`: nodes with a computed median neighbor position sort by
    that median; nodes without one (no neighbor yet ordered) keep their prior relative
    position. Passed to `list.sort` via `functools.partial` so `medians`/`position` (which
    change every sweep) aren't captured as loop-variable closures.
    """
    median = medians[node_id]
    return median if median is not None else position[node_id]


_ORDER_ITERATIONS = 4


def _ancestors_including_self(node_id, parents):
    """Every node with a path to `node_id` over the acyclic edge set, plus `node_id` itself."""
    seen = {node_id}
    queue = deque([node_id])
    while queue:
        current = queue.popleft()
        for parent in parents.get(current, ()):
            if parent not in seen:
                seen.add(parent)
                queue.append(parent)
    return seen


def _shortest_paths_from(sources, targets, children):
    """Breadth-first shortest path from any node in `sources` to each node in `targets`.

    Sources and children are visited in sorted id order: relationships arrive from the service
    unordered, and without this the same model could arrange differently between runs.

    :return: {target_id: [source_id, ..., target_id]}; unreachable targets are absent.
    """
    predecessor = {source: None for source in sorted(sources)}
    queue = deque(predecessor)
    remaining = set(targets)
    remaining.difference_update(predecessor)
    while queue and remaining:
        current = queue.popleft()
        for child in sorted(children.get(current, ())):
            if child in predecessor:
                continue
            predecessor[child] = current
            remaining.discard(child)
            queue.append(child)

    paths = {}
    for target in targets:
        if target not in predecessor:
            continue
        path = []
        cursor = target
        while cursor is not None:
            path.append(cursor)
            cursor = predecessor[cursor]
        paths[target] = list(reversed(path))
    return paths


def _priority_rank_constraints(node_ids, acyclic_edges, ranks, priority):
    """Turn a left-to-right `priority` node list into a per-rank relative-ordering constraint.

    See LAYOUT.md "Priority ordering" for the model and worked examples.

    :return: {rank: [node_id, ...]} in required left-to-right order; empty when fewer than two
        distinct known priority ids were supplied.
    """
    known_ids = set(node_ids)
    ordered_priority = []
    for node_id in priority or ():
        if node_id in known_ids and node_id not in ordered_priority:
            ordered_priority.append(node_id)
    if len(ordered_priority) < 2:
        return {}

    children = defaultdict(list)
    parents = defaultdict(list)
    for source, target in acyclic_edges:
        children[source].append(target)
        parents[target].append(source)

    common = set.intersection(
        *(_ancestors_including_self(node_id, parents) for node_id in ordered_priority)
    )
    if common:
        ancestor = sorted(common, key=lambda node_id: (ranks[node_id], node_id))[-1]
        sources = [ancestor]
        boundary_rank = ranks[ancestor]
    else:
        # No common ancestor: a virtual super-root stands in, so every rank is eligible.
        sources = [node_id for node_id in node_ids if ranks[node_id] == 0]
        boundary_rank = -1

    paths = _shortest_paths_from(sources, ordered_priority, children)

    best_index = {}
    for index, node_id in enumerate(ordered_priority):
        for path_node in paths.get(node_id, ()):
            if ranks[path_node] <= boundary_rank:
                continue
            if path_node not in best_index or index < best_index[path_node]:
                best_index[path_node] = index

    by_rank = defaultdict(list)
    for path_node in sorted(best_index, key=lambda n: (best_index[n], n)):
        by_rank[ranks[path_node]].append(path_node)
    return {rank: members for rank, members in by_rank.items() if len(members) > 1}


def _apply_rank_constraint(nodes_in_rank, ordered_ids):
    """Rewrite the slots already occupied by `ordered_ids` so those nodes appear in that
    left-to-right order, in place. Every other node keeps its own slot, which is what lets
    unlisted nodes stay interleaved between listed ones.
    """
    present = [node_id for node_id in ordered_ids if node_id in nodes_in_rank]
    if len(present) < 2:
        return
    slots = sorted(nodes_in_rank.index(node_id) for node_id in present)
    for slot, node_id in zip(slots, present):
        nodes_in_rank[slot] = node_id


def _order_ranks(node_ids, ranks, acyclic_edges, max_rank, constraints=None):
    """Median-heuristic in-rank ordering: a bounded number of alternating downward/upward
    sweeps, each re-sorting a rank by the median position of its neighbors in the
    already-ordered adjacent rank (nodes without such a neighbor keep their prior relative
    position). This is the same class of crossing-reduction heuristic Dagre's ordering phase
    uses, simplified to a fixed iteration count for deterministic, bounded-time execution.

    `constraints` (from `_priority_rank_constraints`) is re-applied after every sort so the
    requested order survives all sweeps and is what the following ranks' medians see.
    """
    constraints = constraints or {}
    parents = defaultdict(list)
    children = defaultdict(list)
    for source, target in acyclic_edges:
        children[source].append(target)
        parents[target].append(source)

    rank_nodes = defaultdict(list)
    for node_id in node_ids:
        rank_nodes[ranks[node_id]].append(node_id)

    for current_rank, ordered_ids in constraints.items():
        _apply_rank_constraint(rank_nodes[current_rank], ordered_ids)

    position = {}
    for nodes_in_rank in rank_nodes.values():
        for index, node_id in enumerate(nodes_in_rank):
            position[node_id] = index

    for iteration in range(_ORDER_ITERATIONS):
        downward = iteration % 2 == 0
        rank_range = range(1, max_rank + 1) if downward else range(max_rank - 1, -1, -1)
        neighbor_map = parents if downward else children
        for current_rank in rank_range:
            nodes_in_rank = rank_nodes[current_rank]
            if not nodes_in_rank:
                continue
            medians = {}
            for node_id in nodes_in_rank:
                neighbors = neighbor_map.get(node_id, ())
                neighbor_positions = [position[n] for n in neighbors if n in position]
                medians[node_id] = _median(neighbor_positions)

            nodes_in_rank.sort(key=partial(_ordering_sort_key, medians, position))
            if current_rank in constraints:
                _apply_rank_constraint(nodes_in_rank, constraints[current_rank])
            for index, node_id in enumerate(nodes_in_rank):
                position[node_id] = index
    return rank_nodes


_COORDINATE_ITERATIONS = 4


def _assign_coordinates(rank_nodes, widths, heights, nodesep, ranksep, max_rank, acyclic_edges):
    """Coordinate assignment: y is the cumulative rank offset (using each rank's tallest node,
    separated by ``ranksep``); x starts as a left-to-right packing within each rank (separated
    by ``nodesep``) and is then nudged towards the median x of each node's REAL parents/children
    in the immediately adjacent rank for a bounded number of iterations (a simplified stand-in
    for Dagre's Brandes-Kopf-style alignment), while a forward sweep re-enforces the ``nodesep``
    minimum gap so nodes never overlap or reorder. Finally, a rank/graph extent-normalization
    pass (`_normalize_rank_extents`) aligns every *connected component*'s own ranks to one shared
    centerline - the human-confirmed "middle center" whole-graph outcome - without letting a
    disconnected component sharing a rank skew or borrow another component's centerline.
    """
    y_pos = {}
    cursor_y = 0.0
    for current_rank in range(max_rank + 1):
        nodes_in_rank = rank_nodes.get(current_rank, [])
        rank_height = max((heights[node_id] for node_id in nodes_in_rank), default=0.0)
        y_center = cursor_y + rank_height / 2.0
        for node_id in nodes_in_rank:
            y_pos[node_id] = y_center
        cursor_y += rank_height + ranksep

    x_pos = {}
    for nodes_in_rank in rank_nodes.values():
        cursor_x = 0.0
        for node_id in nodes_in_rank:
            width = widths[node_id]
            x_pos[node_id] = cursor_x + width / 2.0
            cursor_x += width + nodesep

    node_rank = {
        node_id: current_rank
        for current_rank, nodes_in_rank in rank_nodes.items()
        for node_id in nodes_in_rank
    }
    parents = defaultdict(list)
    children = defaultdict(list)
    for source, target in acyclic_edges:
        children[source].append(target)
        parents[target].append(source)
    component_of, _components = _connected_components(widths.keys(), acyclic_edges)

    # Alignment below pulls each node toward the median x of its REAL parents/children in the
    # immediately adjacent rank (see `_neighbor_medians`) - real edge adjacency, not a
    # positional-index proxy across ranks of potentially different sizes.
    for _ in range(_COORDINATE_ITERATIONS):
        for current_rank in range(max_rank + 1):
            nodes_in_rank = rank_nodes.get(current_rank, [])
            if not nodes_in_rank:
                continue
            desired = list(
                _neighbor_medians(nodes_in_rank, parents, children, x_pos, current_rank, node_rank)
            )

            # Group this rank's nodes by connected component, in the same
            # left-to-right order `_order_ranks` already settled on. Each
            # group is laid out independently - its own nodesep-respecting
            # internal spacing, re-centered on the median of *its own* real
            # neighbors' x - then groups are placed side by side, only ever
            # nudged rightward far enough to keep `nodesep` from the previous
            # group. This is "Dagre-equivalent component packing": no group
            # is forced to share, or allowed to pollute, another group's own
            # alignment target, but nodesep is still enforced everywhere.
            component_groups = {}
            for index, node_id in enumerate(nodes_in_rank):
                component_groups.setdefault(component_of[node_id], []).append(index)

            group_positions = {}
            for indices in component_groups.values():
                raw = {}
                for position_in_group, index in enumerate(indices):
                    node_id = nodes_in_rank[index]
                    if position_in_group == 0:
                        raw[index] = desired[index]
                    else:
                        previous_index = indices[position_in_group - 1]
                        previous_id = nodes_in_rank[previous_index]
                        min_x = (
                            raw[previous_index] + widths[previous_id] / 2.0
                            + nodesep + widths[node_id] / 2.0
                        )
                        raw[index] = max(desired[index], min_x)
                # The clamp above always anchors the group exactly on its
                # first node's own desired target, then only ever pushes
                # later siblings rightward - it never centers the resulting
                # group on its *aggregate* target. Left as-is, that bias
                # compounds every iteration for a shared-parent fan-out (the
                # parent's own desired is the median of that already
                # right-shifted group, so the parent keeps chasing an
                # ever-drifting target instead of converging) - reproduced
                # live this session (root drifting to x=750 instead of
                # settling at 150 for a 3-child fan-out; see Decisions
                # table). Re-centering removes that bias and converges in
                # one iteration for the shapes this session's tests
                # exercise, without changing the group's already-established
                # relative order/spacing.
                target = _median([desired[i] for i in indices])
                raw_values = [raw[i] for i in indices]
                shift = (
                    target - (min(raw_values) + max(raw_values)) / 2.0
                    if target is not None else 0.0
                )
                for index in indices:
                    group_positions[index] = raw[index] + shift

            previous_last_index = None
            for indices in component_groups.values():
                first_index = indices[0]
                if previous_last_index is not None:
                    previous_id = nodes_in_rank[previous_last_index]
                    first_id = nodes_in_rank[first_index]
                    min_x = (
                        group_positions[previous_last_index] + widths[previous_id] / 2.0
                        + nodesep + widths[first_id] / 2.0
                    )
                    shortfall = min_x - group_positions[first_index]
                    if shortfall > 0:
                        for index in indices:
                            group_positions[index] += shortfall
                previous_last_index = indices[-1]

            for index, node_id in enumerate(nodes_in_rank):
                x_pos[node_id] = group_positions[index]

    _normalize_rank_extents(rank_nodes, x_pos, widths, nodesep, max_rank, component_of)
    return x_pos, y_pos


def _neighbor_medians(nodes_in_rank, parents, children, x_pos, current_rank, node_rank):
    """Median x of each node's REAL parents (previous rank) and children (next rank), falling
    back to the node's own current x when it has no real edge into an immediately adjacent rank
    (e.g. an isolated node, or a rank without a previous/next neighbor). Unlike the prior
    positional-index proxy (same index in the adjacent rank), this only ever looks at genuine
    graph edges, so a node aligns with its actual relationships rather than an unrelated node
    that merely shares its column.
    """
    for node_id in nodes_in_rank:
        candidates = [
            x_pos[neighbor] for neighbor in parents.get(node_id, ())
            if node_rank.get(neighbor) == current_rank - 1
        ]
        candidates += [
            x_pos[neighbor] for neighbor in children.get(node_id, ())
            if node_rank.get(neighbor) == current_rank + 1
        ]
        yield _median(candidates) if candidates else x_pos[node_id]


def _connected_components(node_ids, acyclic_edges):
    """Weakly-connected components (direction ignored) over the node set, derived from the
    pipeline's own already-acyclic edge set. Used only to scope the rank/graph
    extent-normalization pass below: a component with zero real edges to the rest of the graph
    must never be pooled into the same "occupied extent" as an unrelated component just because
    they happen to share a rank number - mirroring Dagre's own convention of laying out each
    disconnected component independently rather than centering them against each other.

    :return: (component_of: {node_id: int}, components: [[node_id, ...], ...]); component ids
        and member order are deterministic given a deterministic ``node_ids`` iteration order
        (the caller passes ``widths.keys()``, which preserves the original node insertion order).
    """
    undirected = defaultdict(list)
    for source, target in acyclic_edges:
        undirected[source].append(target)
        undirected[target].append(source)

    component_of = {}
    components = []
    for start in node_ids:
        if start in component_of:
            continue
        component_index = len(components)
        members = []
        stack = [start]
        component_of[start] = component_index
        while stack:
            node = stack.pop()
            members.append(node)
            for neighbor in undirected.get(node, ()):
                if neighbor not in component_of:
                    component_of[neighbor] = component_index
                    stack.append(neighbor)
        components.append(members)
    return component_of, components


def _normalize_rank_extents(rank_nodes, x_pos, widths, nodesep, max_rank, component_of):
    """Shift every rank's nodes - scoped to their own connected component - so that component's
    ranks all share one common centerline: the human-confirmed "middle center" whole-graph
    outcome (a root centered over its full connected child span; every rank's real-connected
    extent midpoint aligned to the same centerline), on top of (not instead of) the real-edge
    local alignment above, which alone cannot manufacture this cross-rank invariant (proven by
    the blueprint's counter-example on uneven fan-out).

    Scoped per connected component (`_connected_components`) rather than globally across the
    whole node set: an unrelated disconnected component sharing a rank can neither skew nor be
    forced to share another component's centerline - each component picks its own anchor rank
    (its own widest occupied extent; ties broken by the smallest rank number, for determinism)
    and every one of that component's other ranks is shifted, as a whole, to match it. A
    component occupying only one rank (a fully isolated node, or several disconnected nodes that
    all happen to land in the same rank) has nothing to normalize against and is left exactly
    where its local packing/alignment already placed it - this is the deterministic policy for
    the isolated-node's-own-position boundary case the blueprint left open.

    A uniform per-rank, per-component shift preserves that component's already-established
    in-rank order and relative spacing; `_enforce_nodesep` afterwards re-guarantees the
    nodesep minimum gap graph-wide, since two independently-shifted components sharing a rank
    could otherwise end up interleaved differently than before the shift.
    """
    component_rank_members = defaultdict(lambda: defaultdict(list))
    for current_rank in range(max_rank + 1):
        for node_id in rank_nodes.get(current_rank, []):
            component_rank_members[component_of[node_id]][current_rank].append(node_id)

    def extent_mid(members):
        xs = [x_pos[node_id] for node_id in members]
        return (min(xs) + max(xs)) / 2.0

    def extent_width(members):
        xs = [x_pos[node_id] for node_id in members]
        return max(xs) - min(xs)

    for rank_members in component_rank_members.values():
        if len(rank_members) < 2:
            continue  # Single-rank component: nothing to share a centerline with.

        anchor_rank = min(rank_members, key=lambda r, m=rank_members: (-extent_width(m[r]), r))
        anchor_mid = extent_mid(rank_members[anchor_rank])
        for current_rank, members in rank_members.items():
            if current_rank == anchor_rank:
                continue
            delta = anchor_mid - extent_mid(members)
            if delta:
                for node_id in members:
                    x_pos[node_id] += delta

    _enforce_nodesep(rank_nodes, x_pos, widths, nodesep, max_rank)


def _enforce_nodesep(rank_nodes, x_pos, widths, nodesep, max_rank):
    """Re-enforce the ``nodesep`` minimum gap after `_normalize_rank_extents`'s shifts, since
    independently shifting each connected component can change how two different components'
    nodes interleave along the x-axis within a rank they happen to share. Re-sorts each rank by
    its *current* x (not the crossing-reduction order from `_order_ranks`, which the shifts may
    have invalidated) and walks left-to-right enforcing the minimum gap; a no-op wherever the
    shifts introduced no violation.
    """
    for current_rank in range(max_rank + 1):
        nodes_in_rank = rank_nodes.get(current_rank, [])
        if len(nodes_in_rank) < 2:
            continue
        ordered_indexes = sorted(
            range(len(nodes_in_rank)), key=lambda i, n=nodes_in_rank: (x_pos[n[i]], i)
        )
        previous_id = nodes_in_rank[ordered_indexes[0]]
        for list_index in ordered_indexes[1:]:
            node_id = nodes_in_rank[list_index]
            min_x = (
                x_pos[previous_id] + widths[previous_id] / 2.0
                + nodesep + widths[node_id] / 2.0
            )
            if x_pos[node_id] < min_x:
                x_pos[node_id] = min_x
            previous_id = node_id
