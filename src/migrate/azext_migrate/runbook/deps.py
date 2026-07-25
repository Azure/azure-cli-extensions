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
    for key in ('prerequisite', 'dependsOn'):
        for dep in step.get(key) or []:
            dep_id = _dep_id(dep)
            if dep_id and dep_id not in seen:
                seen.add(dep_id)
                ids.append(dep_id)
    return ids
