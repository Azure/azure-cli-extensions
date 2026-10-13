# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Shared dependency-resolution helpers for runbook definition/execution.

A runbook step declares its upstream steps through two sibling lists:

* ``prerequisite`` — hard ordering constraints, and
* ``dependsOn`` — soft/gate dependencies (e.g. approval gates).

Both are lists of objects shaped like ``{"step": "<stepId>", "mode": ...}``
(and, defensively, plain id strings). The dependency graph and the table
projection must consider *both* lists, so the merge logic lives here in one
place rather than being duplicated (and drifting) across modules.
"""


def _dep_id(dep):
    """Extract the referenced step id from one dependency entry."""
    if isinstance(dep, dict):
        return dep.get('step') or dep.get('stepId')
    if dep:
        return str(dep)
    return None


def merged_dep_ids(step):
    """Return the ordered, de-duplicated upstream step ids for ``step``.

    Merges the ``prerequisite`` and ``dependsOn`` lists (in that order),
    dropping blanks and duplicates while preserving first-seen order.
    """
    step = step or {}
    ids = []
    seen = set()
    for key in ('prerequisites', 'dependsOn'):
        for dep in step.get(key) or []:
            dep_id = _dep_id(dep)
            if dep_id and dep_id not in seen:
                seen.add(dep_id)
                ids.append(dep_id)
    return ids


def _step_id(step):
    return step.get('stepId') or step.get('id') or step.get('name')


def _step_name(step):
    return (step.get('displayName') or step.get('name')
            or step.get('stepName') or _step_id(step) or 'step')


def _iter_ws_steps(document):
    """Yield ``(workstream_id, workstream_name, step)`` for every step in a
    definition or execution document.

    Unwraps an execution ``properties`` envelope and covers both the grouped
    ``workstreams[].steps[]`` and flat ``steps[]`` shapes. Steps that live
    outside any workstream yield ``None`` for the workstream id and name.
    """
    root = document or {}
    if isinstance(root, dict) and isinstance(root.get('properties'), dict):
        merged = dict(root)
        merged.update(root['properties'])
        root = merged
    if not isinstance(root, dict):
        return
    workstreams = root.get('workstreams')
    if isinstance(workstreams, list) and workstreams:
        for workstream in workstreams:
            if not isinstance(workstream, dict):
                continue
            ws_id = workstream.get('id')
            name = (workstream.get('displayName') or workstream.get('name')
                    or ws_id)
            for step in workstream.get('steps') or []:
                if isinstance(step, dict):
                    yield ws_id, name, step
        return
    for step in root.get('steps') or []:
        if isinstance(step, dict):
            yield None, None, step


def build_dep_labels(document):
    """Map each step id to a ``(workstream_id, workstream_name, step_name)``.

    A dependency is stored as an opaque step id. This single lookup (built once
    per document) lets every surface -- the ``--output table`` views and the
    visualize grid -- render a dependency as ``workstream:step name`` when it
    crosses workstreams and as just ``step name`` within the same workstream
    (see :func:`label_deps`). Steps outside any workstream carry a ``None``
    workstream; ids absent here (dangling references) fall back to the raw id.
    """
    labels = {}
    for ws_id, ws_name, step in _iter_ws_steps(document):
        step_id = _step_id(step)
        if not step_id:
            continue
        labels[step_id] = (ws_id, ws_name, _step_name(step))
    return labels


def label_deps(step, labels, current_ws_id=None):
    """Return ``step``'s merged dependency ids as readable labels.

    A dependency in a *different* workstream renders as ``workstream:step
    name``; one in the *same* workstream (``current_ws_id``), or a step outside
    any workstream, renders as just the step name. Ids missing from ``labels``
    (dangling references, or a single-step projection) fall back to the raw id.
    """
    out = []
    for dep_id in merged_dep_ids(step):
        entry = labels.get(dep_id)
        if not entry:
            out.append(dep_id)
            continue
        ws_id, ws_name, step_name = entry
        if ws_name and ws_id != current_ws_id:
            out.append('%s:%s' % (ws_name, step_name))
        else:
            out.append(step_name)
    return out
