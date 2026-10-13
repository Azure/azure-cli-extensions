# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Compute the configuration status of a runbook definition step.

A runbook is *shipped* as two documents inside the same download archive:

* the **definition** (``spec``) — the immutable step graph, and
* the **parameters** (``inputs``) — the per-step input *schema* plus
  the customer-supplied *values*.

A step is only runnable once every *required* input has a value. Required
inputs come in two scopes:

* ``Appliance`` — one shared value stored at ``stepInputs[stepId][field]``.
* ``Entity`` — one value **per migration entity**, stored at
  ``stepInputs[stepId].workloadOverrides[entityId][field]``. A non-empty
  step-level value is inherited by every workload (the per-entity override is
  optional), so an entity-scope field is "set" when each entity's *effective*
  value -- its override if non-empty, else the step-level value -- is set.
  This mirrors the configure editor's ``effective()``.

The status is one of:

* ``Configured``     — the step has required inputs and all have values,
* ``Partial (n/m)``  — some but not all required inputs have values,
* ``NotConfigured``  — the step has required inputs but none have values,
* ``NA``             — the step takes no inputs (nothing to configure), and
* ``Unknown``        — no parameters document is available, so the status of a
  step that *might* take inputs cannot be determined.

A step's required inputs are defined solely by its ``schema[stepRef]`` entry.
Manual/Approval gates (``stepRef`` in :data:`INPUTLESS_STEP_REFS`) never take
inputs, so they are :data:`NA` even when no parameters document is present. Any
other step whose schema declares no required inputs is likewise :data:`NA`.
"""

from azext_migrate.runbook.constants import INPUTLESS_STEP_REFS

CONFIGURED = 'Configured'
NOT_CONFIGURED = 'NotConfigured'
NOT_APPLICABLE = 'NA'
UNKNOWN = 'Unknown'


def _is_empty(value):
    """Return True when ``value`` counts as "not provided"."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ''
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def _field_is_set(field, meta, step, step_inputs):
    """Return True when a required input ``field`` has a value on the step."""
    scope = (meta.get('scope') if isinstance(meta, dict) else None) or \
        'Appliance'
    if scope == 'Entity':
        entities = step.get('entities') or []
        if not entities:
            return False
        overrides = step_inputs.get('workloadOverrides') or {}
        # A non-empty step-level value is inherited by every workload; only a
        # non-empty per-entity override takes precedence (configure's
        # ``effective()``: override if set, else the step-level value).
        step_level = step_inputs.get(field)
        for entity_id in entities:
            effective = (overrides.get(entity_id) or {}).get(field)
            if _is_empty(effective):
                effective = step_level
            if _is_empty(effective):
                return False
        return True
    return not _is_empty(step_inputs.get(field))


def compute(step, runbook_inputs):
    """Return the configuration status string for a definition ``step``.

    ``runbook_inputs`` is the ``inputs`` object from the parameters
    document (with ``schema`` and ``stepInputs``). A step that takes no inputs
    is :data:`NOT_APPLICABLE`; a step that might take inputs but has no
    parameters document is :data:`UNKNOWN`. Otherwise the step's required
    inputs come from ``schema[stepRef]``.
    """
    step = step or {}
    step_ref = step.get('stepRef')
    # Manual/Approval gates never take inputs -> NA (independent of params).
    if step_ref in INPUTLESS_STEP_REFS:
        return NOT_APPLICABLE
    if not isinstance(runbook_inputs, dict):
        return UNKNOWN
    step_id = step.get('stepId') or step.get('id')
    # A missing ``stepInputs`` entry just means "no values supplied yet"; the
    # schema below decides whether any are required.
    step_inputs = (runbook_inputs.get('stepInputs') or {}).get(step_id)
    if not isinstance(step_inputs, dict):
        step_inputs = {}
    # The schema entry may be absent for steps that need no inputs; treat a
    # missing/invalid schema as "no required inputs".
    schema = (runbook_inputs.get('schema') or {}).get(step_ref)
    if not isinstance(schema, dict):
        schema = {}

    required = [
        (field, meta) for field, meta in schema.items()
        if isinstance(meta, dict) and meta.get('required')]
    if not required:
        return NOT_APPLICABLE

    set_count = sum(
        1 for field, meta in required
        if _field_is_set(field, meta, step, step_inputs))
    total = len(required)
    if set_count == 0:
        return NOT_CONFIGURED
    if set_count == total:
        return CONFIGURED
    return 'Partial (%d/%d)' % (set_count, total)


def annotate(definition, runbook_inputs):
    """Stamp ``configurationStatus`` onto every step of ``definition``.

    Mutates and returns ``definition`` in place so the table transformer and
    the graph/grid can read ``step['configurationStatus']`` without needing
    the parameters document threaded through them.
    """
    if not isinstance(definition, dict):
        return definition
    workstreams = definition.get('workstreams')
    if isinstance(workstreams, list):
        for workstream in workstreams:
            if isinstance(workstream, dict):
                _annotate_steps(workstream.get('steps'), runbook_inputs)
    _annotate_steps(definition.get('steps'), runbook_inputs)
    return definition


def _annotate_steps(steps, runbook_inputs):
    if not isinstance(steps, list):
        return
    for step in steps:
        if isinstance(step, dict):
            step['configurationStatus'] = compute(step, runbook_inputs)
