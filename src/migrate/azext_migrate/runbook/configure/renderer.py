# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Render the runbook parameters editor into a self-contained HTML file.

The runbook's ``inputs.json`` (schema + per-instance step inputs + envelope
ids) and ``spec.json`` (entity list per step) are embedded, as JSON, into an
offline HTML page. The page references no external/CDN resources and makes no
outbound network calls; editing writes ``./inputs.json`` locally and the page
shows the ``parameter upload`` command to run.

Security: the embedded JSON is placed inside a ``<script>`` block, so the
``<``/``>``/``&`` characters are escaped to their ``\\uXXXX`` forms. This is the
mandatory guard that prevents a hostile ``</script>`` (or ``<!--``) sequence in
any service-supplied value from breaking out of the script context.
"""

import json
import os
import re

_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), 'templates', 'configure.html.tmpl')

_DATA_TOKEN = '__RUNBOOK_DATA__'

# Escapes that neutralise a `</script>`/`<!--` breakout without altering the
# parsed JSON value (JSON string parsing turns these back into </, > and &).
_SCRIPT_ESCAPES = (('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026'))


def _normalize_doc(inputs_root):
    """Return the ``{runbookId, waveId, migrateProjectId, schema, stepInputs}``
    shape the page expects from a raw ``inputs.json`` document."""
    root = inputs_root if isinstance(inputs_root, dict) else {}
    inputs_obj = root.get('inputs')
    if not isinstance(inputs_obj, dict):
        inputs_obj = root
    return {
        'runbookId': root.get('runbookId'),
        'waveId': root.get('waveId'),
        'migrateProjectId': root.get('migrateProjectId'),
        'schema': inputs_obj.get('schema') or {},
        'stepInputs': inputs_obj.get('stepInputs') or {},
    }


def _normalize_spec(spec_doc):
    """Return the ``{entities, workstreams}`` shape the page reads for the
    authoritative per-step entity list, from a raw ``spec.json`` document."""
    if not isinstance(spec_doc, dict):
        return {'entities': [], 'workstreams': []}
    payload = spec_doc.get('spec')
    if not isinstance(payload, dict):
        payload = spec_doc
    return {
        'entities': payload.get('entities') or [],
        'workstreams': payload.get('workstreams') or [],
    }


def build_meta(resource_group_name, project_name, runbook_name, inputs_root):
    """Build the header/upload-command metadata for the page.

    Prefers the values the caller already knows (``-g``/``-p``/``-n``) and
    falls back to parsing the ARM ``runbookId``/``waveId`` from the document
    (for offline ``--from-file`` rendering).
    """
    root = inputs_root if isinstance(inputs_root, dict) else {}
    runbook_id = root.get('runbookId') or ''
    wave_id = root.get('waveId') or ''

    def _seg(source, segment):
        match = re.search(
            '/%s/([^/]+)' % segment, source, re.IGNORECASE)
        return match.group(1) if match else ''

    return {
        'runbook': runbook_name or _seg(runbook_id, 'runbooks'),
        'resourceGroup': resource_group_name or _seg(
            runbook_id, 'resourcegroups'),
        'project': project_name or _seg(runbook_id, 'migrateprojects'),
        'wave': _seg(wave_id, 'waves'),
    }


def _embed(payload):
    """Serialise ``payload`` to a script-safe JSON literal."""
    data = json.dumps(payload)  # ensure_ascii=True escapes all non-ASCII
    for raw, safe in _SCRIPT_ESCAPES:
        data = data.replace(raw, safe)
    return data


def render(inputs_root, spec_doc, meta, schema_doc=None):
    """Return a complete, self-contained parameters-editor HTML document.

    ``schema_doc``, when the schema is shipped as its own ``schema.json``
    (rather than embedded in ``inputs.json``), supplies the validation rules.
    """
    doc = _normalize_doc(inputs_root)
    if schema_doc:
        doc['schema'] = schema_doc
    payload = {
        'doc': doc,
        'spec': _normalize_spec(spec_doc),
        'meta': meta or {},
        # Full original document so the page can export an exact inputs.json
        # (only stepInputs are edited in the browser).
        'inputsRoot': inputs_root if isinstance(inputs_root, dict) else {},
    }
    with open(_TEMPLATE_PATH, encoding='utf-8') as handle:
        template = handle.read()
    return template.replace(_DATA_TOKEN, _embed(payload))
