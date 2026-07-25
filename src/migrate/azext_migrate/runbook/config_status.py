# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Compute the configuration status of a runbook definition step.

A runbook is *shipped* as two documents inside the same download archive:

* the **definition** (``runbookSpec``) — the immutable step graph, and
* the **parameters** (``runbookInputs``) — the per-step input *schema* plus
  the customer-supplied *values*.

A step is only runnable once every *required* input has a value. Required
inputs come in two scopes:

* ``Appliance`` — one shared value stored at ``stepInputs[stepId][field]``.
* ``Entity`` — one value **per migration entity**, stored at
  ``stepInputs[stepId].workloadOverrides[entityId][field]``. An entity-scope
  field is only "set" when *every* entity on the step has a value for it.

The status is one of:

* ``Configured``     — all required inputs have values (or none are required),
* ``Partial (n/m)``  — some but not all required inputs have values,
* ``NotConfigured``  — no required input has a value, and
* ``Unknown``        — no parameters/schema available for the step (defensive).
"""

CONFIGURED = 'Configured'
NOT_CONFIGURED = 'NotConfigured'
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
        overrides = step_inputs.get('workloadOverrides') or {}
        entities = step.get('entities') or []
        if not entities:
            return False
        for entity_id in entities:
            entity_values = overrides.get(entity_id) or {}
            if _is_empty(entity_values.get(field)):
                return False
        return True
    return not _is_empty(step_inputs.get(field))


def compute(step, runbook_inputs):
    """Return the configuration status string for a definition ``step``.

    ``runbook_inputs`` is the ``runbookInputs`` object from the parameters
    document (with ``schema`` and ``stepInputs``). Returns :data:`UNKNOWN`
    when the schema or inputs for the step are unavailable.
    """
    step = step or {}
    if not isinstance(runbook_inputs, dict):
        return UNKNOWN
    step_ref = step.get('stepRef')
    step_id = step.get('stepId') or step.get('id')
    schema = (runbook_inputs.get('schema') or {}).get(step_ref)
    step_inputs = (runbook_inputs.get('stepInputs') or {}).get(step_id)
    if not isinstance(schema, dict) or not isinstance(step_inputs, dict):
        return UNKNOWN

    required = [
        (field, meta) for field, meta in schema.items()
        if isinstance(meta, dict) and meta.get('required')]
    if not required:
        return CONFIGURED

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
