# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Render a runbook view into a self-contained, offline HTML file.

This is the security-critical stage: **every** user-controlled value (step
names, workstream names, statuses, dependency labels) is passed through
:func:`html.escape` before it is substituted into the markup, which is the
mandatory XSS guard. The emitted HTML embeds all styles/scripts inline and
references no external/CDN resources, so it is fully offline and makes no
outbound network calls.

The document shows two views of the same runbook:

* a **grid** (portal-style, grouped by workstream) — the default view, and
* a **diagram** (SVG dependency DAG) — an optional view toggled in-page.

The tiny inline toggle script runs entirely locally (no network), preserving
the offline/air-gapped guarantee.
"""

import datetime
import html
import json
import os
import re
import secrets
import string

from azext_migrate.runbook.visualize import viewmodel

_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), 'templates', 'runbook.html.tmpl')

# SVG layout constants (deterministic, so output is stable for tests).
_MARGIN = 24
_NODE_W = 220
_NODE_H = 56
_COL_GAP = 80
_ROW_GAP = 24
# Workstream swimlane band metrics.
_BAND_LABEL_H = 26
_BAND_GAP = 18

# Execution ``state`` vocabulary, in legend display order.
_EXECUTION_LEGEND = (
    ('Completed', '#6bb700'),
    ('InProgress', '#2899f5'),
    ('Blocked', '#ffaa44'),
    ('Failed', '#d13438'),
    ('NotStarted', '#8a8886'),
)

# Definition configuration-status vocabulary, in legend display order.
_DEFINITION_LEGEND = (
    ('Configured', '#6bb700'),
    ('Partial', '#ffaa44'),
    ('NotConfigured', '#d13438'),
    ('Unknown', '#8a8886'),
)


def _esc(value):
    """HTML-escape a possibly-``None`` user value (the XSS guard)."""
    if value is None:
        return ''
    return html.escape(str(value), quote=True)


def _id_badge(value, title='id'):
    """Render an id as a small, greyish, monospace inline badge (HTML).

    Ids are surfaced so users can copy them into the CLI commands that
    address workstreams/steps by id (e.g. ``workstream split``/``merge``).
    Returns escaped markup, so callers must NOT re-escape it.
    """
    if not value:
        return ''
    return '<span class="id-badge" title="%s">%s</span>' % (
        _esc(title), _esc(value))


def _id_tspan(value):
    """Render an id as a small, muted ``<tspan>`` inside an SVG text run."""
    if not value:
        return ''
    return '<tspan class="svg-id"> %s</tspan>' % _esc(value)


def _status_class(status):
    """Map a status to a CSS-safe class suffix (first word, alnum only)."""
    if not status:
        return ''
    token = str(status).strip().split(' ', 1)[0]
    token = re.sub(r'[^A-Za-z0-9_-]', '', token)
    return ' status-%s' % token if token else ''


def _sorted_group_pairs(graph):
    """Return ``group_order`` topologically sorted by workstream deps.

    Prerequisite lanes are placed before dependent lanes; ties keep document
    order. A dependency cycle (defensive) degrades to document order.
    """
    pairs = list(graph.group_order)
    if not graph.group_deps:
        return pairs
    order_index = {ws_id: i for i, (_, ws_id) in enumerate(pairs)}
    name_by_id = {ws_id: name for name, ws_id in pairs}
    prereqs = {}
    for pre_ws, dep_ws in graph.group_deps:
        if pre_ws in order_index and dep_ws in order_index:
            prereqs.setdefault(dep_ws, set()).add(pre_ws)
    placed = set()
    result = []
    remaining = [ws_id for _, ws_id in pairs]
    progressed = True
    while remaining and progressed:
        progressed = False
        ready = [w for w in remaining if prereqs.get(w, set()) <= placed]
        if not ready:
            break
        ready.sort(key=lambda w: order_index.get(w, 0))
        for ws_id in ready:
            result.append(ws_id)
            placed.add(ws_id)
            remaining.remove(ws_id)
            progressed = True
    result.extend(remaining)  # cycle fallback: keep document order
    return [(name_by_id.get(ws_id), ws_id) for ws_id in result]


def _workstream_order(graph):
    """Group nodes into workstream swimlanes, ordered by workstream deps.

    Bands follow a dependency-topological order (prerequisite lanes first),
    tie-broken by the runbook's document order. Within a band, nodes keep
    their layer-sorted order for column layout.
    """
    by_ws = {}
    for node in graph.nodes:
        by_ws.setdefault(node.group or 'Ungrouped', []).append(node)
    ordered = []
    for name, ws_id in _sorted_group_pairs(graph):
        nodes = by_ws.pop(name, None)
        if nodes:
            ordered.append((name, ws_id, nodes))
    # Any group not present in the recorded order (defensive) keeps a stable
    # first-appearance fallback.
    for name, nodes in by_ws.items():
        ordered.append((name, nodes[0].group_id, nodes))
    return ordered


def _layout(graph):
    """Lay steps out in workstream swimlanes with dependency columns.

    The horizontal axis is the (global) dependency layer so ``dependsOn``
    edges always flow left-to-right; the vertical axis groups steps into
    per-workstream bands. Returns ``(positions, bands, width, height)`` where
    ``bands`` is a list of ``(name, top, height, count)`` tuples.
    """
    positions = {}
    bands = []
    width = _MARGIN * 2 + graph.layer_count * _NODE_W \
        + max(graph.layer_count - 1, 0) * _COL_GAP
    y = _MARGIN
    for name, ws_id, nodes in _workstream_order(graph):
        band_top = y
        content_top = band_top + _BAND_LABEL_H
        rows_per_layer = {}
        max_rows = 0
        for node in nodes:
            row = rows_per_layer.get(node.layer, 0)
            rows_per_layer[node.layer] = row + 1
            node_x = _MARGIN + node.layer * (_NODE_W + _COL_GAP)
            node_y = content_top + row * (_NODE_H + _ROW_GAP)
            positions[node.id] = (node_x, node_y)
            max_rows = max(max_rows, row + 1)
        band_height = _BAND_LABEL_H + max_rows * (_NODE_H + _ROW_GAP)
        bands.append((name, ws_id, band_top, band_height, len(nodes)))
        y = band_top + band_height + _BAND_GAP
    height = y + _MARGIN - _BAND_GAP
    return positions, bands, width, height


def _svg(graph):
    if not graph.nodes:
        return '<p class="empty">This runbook has no steps to display.</p>'

    positions, bands, width, height = _layout(graph)
    parts = [
        '<svg width="%d" height="%d" viewBox="0 0 %d %d" role="img">'
        % (width, height, width, height)]

    for name, ws_id, top, band_height, count in bands:
        parts.append(
            '<g class="lane">'
            '<rect x="%d" y="%d" width="%d" height="%d" rx="8"/>'
            '<text x="%d" y="%d">Workstream: %s%s (%d)</text></g>'
            % (_MARGIN / 2, top, width - _MARGIN, band_height,
               _MARGIN / 2 + 12, top + 16,
               _esc(name or 'Ungrouped'), _id_tspan(ws_id), count))

    # Workstream-level dependency connectors: a rail down the left edge from a
    # prerequisite lane's bottom to the dependent lane's top.
    band_pos = {ws_id: (top, band_height)
                for _, ws_id, top, band_height, _ in bands}
    for pre_ws, dep_ws in graph.group_deps:
        if pre_ws in band_pos and dep_ws in band_pos:
            pre_top, pre_h = band_pos[pre_ws]
            dep_top = band_pos[dep_ws][0]
            rail = _MARGIN / 2
            parts.append(
                '<path class="lane-edge" d="M%.1f %.1f L%.1f %.1f"/>'
                % (rail, pre_top + pre_h, rail, dep_top))

    for edge in graph.edges:
        if edge.source not in positions or edge.target not in positions:
            continue
        sx, sy = positions[edge.source]
        tx, ty = positions[edge.target]
        x1, y1 = sx + _NODE_W, sy + _NODE_H / 2
        x2, y2 = tx, ty + _NODE_H / 2
        midx = (x1 + x2) / 2
        parts.append(
            '<path class="edge" d="M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"/>'
            % (x1, y1, midx, y1, midx, y2, x2, y2))

    for node in graph.nodes:
        x, y = positions[node.id]
        status_class = _status_class(node.status)
        sub = node.ref or node.status
        parts.append('<g class="node%s">' % status_class)
        parts.append(
            '<rect x="%d" y="%d" width="%d" height="%d" rx="6"/>'
            % (x, y, _NODE_W, _NODE_H))
        parts.append(
            '<text x="%d" y="%d">%s</text>'
            % (x + 12, y + 24, _esc(node.name)))
        if sub:
            parts.append(
                '<text class="sub" x="%d" y="%d">%s</text>'
                % (x + 12, y + 42, _esc(sub)))
        parts.append('</g>')

    parts.append('</svg>')
    return '\n'.join(parts)


def _legend(graph, view):
    """Render the status legend appropriate to the view kind."""
    if view is not None and view.kind == viewmodel.KIND_DEFINITION:
        statuses = _DEFINITION_LEGEND
    else:
        statuses = _EXECUTION_LEGEND
        if not any(node.status for node in graph.nodes):
            return ''
    items = ''.join(
        '<span><i style="background:%s"></i>%s</span>' % (color, _esc(label))
        for label, color in statuses)
    return '<div class="legend">%s</div>' % items


# ---------------------------------------------------------------------------
# Portal-style grid
# ---------------------------------------------------------------------------

def _summary_cards(view):
    if view is None or not view.summary:
        return ''
    stats = ''.join(
        '<div class="stat"><span class="stat__n">%s</span>'
        '<span class="stat__l">%s</span></div>' % (_esc(value), _esc(label))
        for label, value in view.summary)
    return '<div class="summary">%s</div>' % stats


def _grid_row(kind, index, step):
    """Render one step as a clickable grid row (portal-style).

    The status/last-column semantics differ by view kind: a definition row
    shows its configuration status and entity count, while an execution row
    shows its live step status and workload progress.
    """
    ref = ('<span class="row__ref">%s</span>' % _esc(step.step_ref)
           if step.step_ref else '')
    dep = ', '.join(step.deps) if step.deps else '-'
    apps = len(step.entity_groups)
    if kind == viewmodel.KIND_EXECUTION:
        status = step.status or 'NotStarted'
        count = step.workload_progress or '-'
        retry = getattr(step, 'retry_count', 0) or 0
        retry_badge = (
            ' <span class="retry" title="%s failed attempt(s), retried">'
            '&#8635; %s</span>' % (_esc(retry), _esc(retry))) if retry else ''
    else:
        status = step.status or 'Unknown'
        count = step.workloads
        retry_badge = ''
    return (
        '<div class="row" role="button" tabindex="0" data-step="%d">'
        '<div class="col-step cell-step">'
        '<span class="row__ico">&#9656;</span>'
        '<span class="row__name">%s</span>%s</div>'
        '<div class="col-status"><span class="pill%s">%s</span>%s</div>'
        '<div class="col-dep">%s</div>'
        '<div class="col-count">%s</div>'
        '<div class="col-apps">%s</div>'
        '</div>'
        % (index, _esc(step.name), ref,
           _status_class(status), _esc(status), retry_badge, _esc(dep),
           _esc(count), _esc(apps)))


def _iter_indexed_steps(view):
    """Yield ``(index, workstream_name, step)`` in stable grid order."""
    index = 0
    for workstream in view.workstreams:
        for step in workstream.steps:
            yield index, workstream.name, step
            index += 1


def _portal_grid(view):
    """Render the runbook as a portal-style grid: header + grouped rows."""
    if view.kind == viewmodel.KIND_EXECUTION:
        status_head, count_head = 'Step status', 'Workload progress'
    else:
        status_head, count_head = 'Configuration status', 'Entities'
    parts = [
        '<div class="grid__head">'
        '<div class="col-step">Steps</div>'
        '<div class="col-status">%s</div>'
        '<div class="col-dep">Step dependency</div>'
        '<div class="col-count">%s</div>'
        '<div class="col-apps">Applications</div></div>' % (
            status_head, count_head)]
    index = 0
    for workstream in view.workstreams:
        head = 'Workstream: %s%s (%d)' % (
            _esc(workstream.name or 'Ungrouped'),
            _id_badge(workstream.id, 'Workstream id'),
            len(workstream.steps))
        parts.append('<details class="ws-group" open>')
        parts.append('<summary class="group__head">%s</summary>' % head)
        if not workstream.steps:
            parts.append('<div class="row row--empty">'
                         'No steps in this workstream.</div>')
        for step in workstream.steps:
            parts.append(_grid_row(view.kind, index, step))
            index += 1
        parts.append('</details>')
    return '<div class="grid">%s</div>' % ''.join(parts)


def _field(label, value):
    text = value if value not in (None, '') else '-'
    return ('<div class="field"><div class="field__label">%s</div>'
            '<div class="field__value">%s</div></div>'
            % (_esc(label), _esc(text)))


def _chip_field(label, values):
    if not values:
        body = '<div class="field__value">-</div>'
    else:
        body = '<div class="chips">%s</div>' % ''.join(
            '<span class="chip">%s</span>' % _esc(value) for value in values)
    return ('<div class="field"><div class="field__label">%s</div>%s</div>'
            % (_esc(label), body))


def _status_field(label, status, default):
    """Render a labelled status pill field for the detail pane."""
    return ('<div class="field"><div class="field__label">%s</div>'
            '<div class="field__value"><span class="pill%s">%s</span></div>'
            '</div>'
            % (_esc(label), _status_class(status), _esc(status or default)))


def _output_scalar(value):
    """Format a single outputs value for display (JSON for nested shapes)."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _output_rows(outputs):
    """Render an outputs dict as key/value rows.

    A list value stacks one item per line (generic — no key is special-cased),
    so multi-valued outputs like ``roleAssignmentIds`` read cleanly.
    """
    rows = []
    for key in sorted(outputs or {}):
        value = outputs[key]
        if isinstance(value, list):
            value_html = ''.join(
                '<div>%s</div>' % _esc(_output_scalar(item))
                for item in value) or '-'
        else:
            value_html = _esc(_output_scalar(value))
        rows.append(
            '<div class="orow"><span class="ok">%s</span>'
            '<span class="ov">%s</span></div>' % (_esc(key), value_html))
    return ''.join(rows)


def _output_block(variant, heading, tag, rows_html, note=None):
    """Render an output sub-block (``partial`` / ``final`` / ``step``)."""
    tag_html = '<span class="tag">%s</span>' % _esc(tag) if tag else ''
    note_html = ('<div class="muted-note">%s</div>' % _esc(note)
                 if note else '')
    return (
        '<div class="out out--%s"><div class="out__h">%s%s</div>%s%s</div>'
        % (variant, _esc(heading), tag_html, rows_html, note_html))


def _attempt_dot(status):
    """Map an attempt status to a timeline dot class (ok / fail / run)."""
    token = str(status or '').lower()
    if token == 'failed':
        return 'fail'
    if token in ('completed', 'succeeded'):
        return 'ok'
    return 'run'


def _time_range(started, ended):
    """Format a start/end pair as "start \u2192 end" (or whichever is present)."""
    if started and ended:
        return '%s \u2192 %s' % (started, ended)
    return started or ended or ''


def _parse_iso(value):
    """Parse an ISO-8601 timestamp (tolerating a trailing ``Z``), else None."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        return datetime.datetime.fromisoformat(text)
    except ValueError:
        return None


def _duration(started, ended):
    """Human-readable duration between two ISO timestamps (e.g. ``2h 52m``)."""
    start, end = _parse_iso(started), _parse_iso(ended)
    if start is None or end is None:
        return ''
    total = int((end - start).total_seconds())
    if total < 0:
        return ''
    if total < 60:
        return '%ds' % total
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if hours:
        parts.append('%dh' % hours)
    if minutes:
        parts.append('%dm' % minutes)
    if seconds and not hours:
        parts.append('%ds' % seconds)
    return ' '.join(parts) or '0s'


def _attempt_timeline(attempts):
    """Render an attempts timeline: dots, status pill, times, error box."""
    rows = []
    for attempt in attempts:
        when = _time_range(attempt.get('started'), attempt.get('ended'))
        when_html = ('<span class="att__t">%s</span>' % _esc(when)
                     if when else '')
        err_html = ('<div class="att__err">%s</div>' % _esc(attempt['error'])
                    if attempt.get('error') else '')
        rows.append(
            '<div class="att"><span class="att__dot %s"></span><div>'
            '<div class="att__row"><span class="att__n">Attempt %s</span>'
            '<span class="pill%s">%s</span>%s</div>%s</div></div>'
            % (_attempt_dot(attempt.get('status')), _esc(attempt.get('number')),
               _status_class(attempt.get('status')),
               _esc(attempt.get('status') or ''), when_html, err_html))
    return '<div class="timeline">%s</div>' % ''.join(rows)


def _entity_output_blocks(entity):
    """Render a workload's output as partial (running) or final (completed)."""
    if entity.outputs:
        rows = _output_rows(entity.outputs)
        if entity.completed:
            return _output_block('final', 'Final output', None, rows)
        return _output_block(
            'partial', 'Partial output', 'live \u00b7 may change', rows,
            'Progress snapshot from the tool; superseded when the step '
            'completes.')
    if not entity.completed:
        return _output_block(
            'final', 'Final output', 'pending', '',
            'Available once this workload reaches a completed state.')
    return ''


def _entity_card(entity):
    """Render one workload (entity) card: header, attempts, output block."""
    meta = '<span class="pill%s">%s</span>' % (
        _status_class(entity.status), _esc(entity.status or 'NotStarted'))
    if entity.tool_status:
        meta += ' <span class="chip">tool: %s</span>' % _esc(
            entity.tool_status)
    body = ''
    if entity.attempts:
        failed = sum(1 for a in entity.attempts
                     if str(a.get('status') or '').lower() == 'failed')
        badge = ' <span class="retry">%d failed</span>' % failed if failed \
            else ''
        body += ('<div><div class="field__label">Attempts%s</div>%s</div>'
                 % (badge, _attempt_timeline(entity.attempts)))
    if entity.error:
        body += '<div class="att__err">%s</div>' % _esc(entity.error)
    elif entity.status_reason:
        body += '<div class="muted-note">%s</div>' % _esc(entity.status_reason)
    body += _entity_output_blocks(entity)
    return (
        '<div class="ent"><div class="ent__h">'
        '<span class="ent__nm">%s</span>'
        '<span class="ent__meta">%s</span></div>'
        '<div class="ent__body">%s</div></div>'
        % (_esc(entity.name), meta, body))


def _detail_section(heading, body_html, first=False):
    """Wrap a group of detail-pane fields in a titled section."""
    cls = 'dsec dsec--first' if first else 'dsec'
    return ('<div class="%s"><div class="dsec__h">%s</div>%s</div>'
            % (cls, _esc(heading), body_html))


def _application_card(name):
    """Render one application (entity group) with the workload-card style.

    Applications and workloads share the ``.ent`` card typography so the two
    lists read identically in the step detail pane.
    """
    return ('<div class="ent"><div class="ent__h">'
            '<span class="ent__nm">%s</span></div></div>' % _esc(name))


def _detail_html(workstream_name, step, kind):
    """Build the step detail-pane markup (shown in the side drawer)."""
    if kind == viewmodel.KIND_EXECUTION:
        overview = (
            _field('Step ID', step.id)
            + _status_field('Step status', step.status, 'NotStarted')
            + (_field('Status reason', step.status_reason)
               if step.status_reason else '')
            + (_field('Error', step.error) if step.error else '')
            + (_field('Retries (failed attempts)', step.retry_count)
               if step.retry_count else '')
            + _field('Workload progress', step.workload_progress)
            + (_field('Start time', step.started) if step.started else '')
            + (_field('End time', step.ended) if step.ended else '')
            + (_field('Duration', _duration(step.started, step.ended))
               if _duration(step.started, step.ended) else '')
            + (_field('User comment', step.user_comment)
               if step.user_comment else '')
            + _chip_field('Depends on', step.deps))
        body = _detail_section('Overview', overview, first=True)
        if step.entities:
            cards = ''.join(_entity_card(e) for e in step.entities)
            body += _detail_section(
                'Workloads (%d)' % len(step.entities), cards)
        apps = step.entity_groups
        body += _detail_section(
            'Applications (%d)' % len(apps),
            ''.join(_application_card(a) for a in apps)
            or '<div class="muted-note">No applications for this step.</div>')
        step_out = _attempt_timeline(step.attempts) if step.attempts else ''
        if step.outputs:
            step_out += _output_block(
                'step', 'Shared output', None, _output_rows(step.outputs),
                'Step-scoped: produced once for the whole step '
                '(no per-workload split).')
        if step_out:
            body += _detail_section('Step output', step_out)
    else:
        entities = step.entity_names
        body = (
            _field('Step type', step.step_ref)
            + _field('Step ID', step.id)
            + _status_field('Configuration status', step.status, 'Unknown')
            + _chip_field('Entities (%d)' % len(entities), entities)
            + _chip_field('Applications', step.entity_groups)
            + _chip_field('Pre-requisites', step.prereqs)
            + _chip_field('Depends on', step.dep_details))
    return (
        '<section class="detail">'
        '<header class="detail__head">'
        '<div><h2 class="detail__title">%s</h2>'
        '<div class="detail__sub">Workstream: %s</div></div>'
        '<button type="button" class="detail__close" data-close '
        'aria-label="Close">&#10005;</button></header>'
        '<div class="detail__body">%s</div></section>'
        % (_esc(step.name), _esc(workstream_name or 'Ungrouped'), body))


def _grid_details(view):
    """Emit hidden per-step detail blocks that the drawer clones on click."""
    if view is None:
        return ''
    blocks = ''.join(
        '<div class="detail-src" id="detail-%d" hidden>%s</div>'
        % (index, _detail_html(ws_name, step, view.kind))
        for index, ws_name, step in _iter_indexed_steps(view))
    return '<div id="detailData" hidden>%s</div>' % blocks


# CLI cmdlet help chips (static; shown above the definition grid).
# ``<rg>``/``<project>``/``<runbook>``/``<execution>`` are auto-filled from the
# invoking command; only the genuinely variable tokens (step/workstream/entity
# names) stay as ``<...>`` placeholders for the user to fill.
_HELP_CHIPS = (
    ('&#9654;', 'Start execution',
     'Runs the wave and streams live progress in the execution view.',
     'az migrate runbook execution start --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook>'),
    ('&#65291;', 'Add a step',
     'Adds a step to a workstream in the runbook definition.',
     'az migrate runbook definition step add --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook> '
     '--step-type <type> --step-name <stepName> --workstream-id <workstream>'),
    ('&#8649;', 'Merge workstreams',
     'Combines two workstreams into a single track.',
     'az migrate runbook definition workstream merge --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook> '
     '--source-workstream-ids <id1> <id2> --new-workstream-name <name>'),
    ('&#9649;', 'Split a workstream',
     'Splits a workstream into parallel tracks.',
     'az migrate runbook definition workstream split --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook> '
     '--source-workstream-id <id> --new-workstream-name <name> '
     '--entities-to-move <entity1> <entity2>'),
    ('&#8635;', 'Refresh this view',
     'Regenerates the HTML from the latest runbook definition.',
     'az migrate runbook definition visualize --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook>'),
)


# CLI cmdlet help chips shown above the execution grid.
_EXEC_HELP_CHIPS = (
    ('&#10073;&#10073;', 'Pause execution',
     'Pauses the in-progress execution so it can be resumed later.',
     'az migrate runbook execution pause --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook> '
     '--execution-id <execution>'),
    ('&#9654;', 'Resume execution',
     'Resumes a paused execution from where it left off.',
     'az migrate runbook execution resume --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook> '
     '--execution-id <execution>'),
    ('&#10005;', 'Cancel execution',
     'Cancels an in-progress or paused execution.',
     'az migrate runbook execution cancel --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook> '
     '--execution-id <execution>'),
    ('&#8635;', 'Refresh this view',
     'Regenerates the HTML from the latest execution status.',
     'az migrate runbook execution visualize --resource-group <rg> '
     '--project-name <project> --runbook-name <runbook> '
     '--execution-id <execution>'),
)


_CMD_CONTEXT_TOKENS = (
    ('<rg>', 'resource_group'),
    ('<project>', 'project'),
    ('<runbook>', 'runbook'),
    ('<execution>', 'execution'),
)


def _fill_cmd(cmd, context):
    """Substitute known context values (g/p/runbook/execution) into a chip.

    Variable tokens (step/workstream/entity names) are left as ``<...>``
    placeholders; unfilled context tokens keep their placeholder too.
    """
    if not context:
        return cmd
    for token, key in _CMD_CONTEXT_TOKENS:
        value = context.get(key)
        if value:
            cmd = cmd.replace(token, str(value))
    return cmd


def _help_bar(view, context=None):
    """Render the CLI cmdlet help chips (kind-aware), context-filled."""
    if view is None:
        return ''
    chips_src = (_HELP_CHIPS if view.kind == viewmodel.KIND_DEFINITION
                 else _EXEC_HELP_CHIPS)
    chips = ''.join(
        '<button type="button" class="how-chip" data-title="%s" '
        'data-desc="%s" data-cmd="%s">'
        '<span class="how-chip__ico">%s</span>%s</button>'
        % (_esc(title), _esc(desc), _esc(_fill_cmd(cmd, context)),
           ico, _esc(title))
        for ico, title, desc, cmd in chips_src)
    return (
        '<div class="how-bar"><span class="how-bar__label">This is a '
        'read-only view &mdash; actions run from the Azure CLI. Pick one to '
        'see the command:</span><div class="how-chips">%s</div></div>'
        % chips)


def _meta_block(view):
    """Render the header metadata strip (any view that carries meta)."""
    if view is None or not view.meta:
        return ''
    fields = ''
    for label, value in view.meta:
        display = _format_generated(value) if label == 'Generated' else value
        fields += (
            '<div class="meta"><span class="meta__label">%s</span>'
            '<span class="meta__value" title="%s">%s</span></div>'
            % (_esc(label), _esc(display), _esc(display)))
    return '<div class="tab-meta">%s</div>' % fields


def _grid(view):
    if view is None:
        return ''
    if not view.workstreams or view.step_count == 0:
        return '<p class="empty">This runbook has no steps to display.</p>'
    return _portal_grid(view)


# ---------------------------------------------------------------------------
# Document assembly
# ---------------------------------------------------------------------------

def render(graph, view=None, refresh_interval=None, context=None):
    """Return a complete, self-contained HTML document for the runbook.

    ``graph`` drives the SVG dependency diagram; the optional ``view``
    (:class:`~.viewmodel.RunbookView`) drives the default portal-style grid
    and enables the in-page grid/diagram toggle. When ``refresh_interval`` is
    a positive number of seconds, an offline ``<meta http-equiv="refresh">``
    tag is embedded so a browser viewing the file auto-reloads it from disk on
    that cadence (used by ``--watch`` so the user never has to refresh
    manually). Reloading a local file makes no network call, preserving the
    offline/air-gapped guarantee. ``context`` (resource_group/project/runbook/
    execution) fills the help-chip commands so users copy ready-to-run text.
    """
    with open(_TEMPLATE_PATH, encoding='utf-8') as handle:
        template = string.Template(handle.read())
    title = graph.title if view is None else view.title
    step_count = len(graph.nodes) if view is None else view.step_count
    summary = '%d step%s' % (step_count, '' if step_count == 1 else 's')
    generated = _format_generated(
        None if view is None else view.generated)
    grid_html = _grid(view)
    # Per-file random nonce: the Content-Security-Policy admits only the inline
    # <script> stamped with this nonce, so no injected markup can execute.
    nonce = secrets.token_urlsafe(16)
    return template.substitute(
        title=_esc(title),
        summary=_esc(summary),
        generated=_esc(generated),
        meta=_meta_block(view),
        help=_help_bar(view, context),
        details=_grid_details(view),
        legend=_legend(graph, view),
        refresh=_refresh_meta(refresh_interval),
        summary_cards=_summary_cards(view),
        toggle=_toggle(grid_html),
        grid=grid_html,
        grid_hidden='' if grid_html else ' hidden',
        diagram_hidden=' hidden' if grid_html else '',
        nonce=nonce,
        svg=_svg(graph))


def _format_generated(declared):
    """Format the generation timestamp for the header.

    Prefer the document's own ``generatedAt`` (ISO 8601) when present,
    normalising it to ``YYYY-MM-DD HH:MM UTC``; otherwise fall back to the
    current render time.
    """
    if declared:
        text = str(declared).replace('T', ' ')
        text = text.split('.', 1)[0].rstrip('Z').strip()
        return '%s UTC' % text if text else text
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        '%Y-%m-%d %H:%M UTC')


def _toggle(grid_html):
    """Render the grid/diagram tab buttons (only when a grid exists)."""
    if not grid_html:
        return ''
    return (
        '<div class="tabs" role="tablist">'
        '<button type="button" class="tab is-active" data-view="grid">'
        'Grid</button>'
        '<button type="button" class="tab" data-view="diagram">'
        'Diagram</button></div>')


def _refresh_meta(refresh_interval):
    """Build an offline auto-reload ``<meta>`` tag, or '' when disabled."""
    try:
        seconds = int(refresh_interval)
    except (TypeError, ValueError):
        return ''
    if seconds <= 0:
        return ''
    return '<meta http-equiv="refresh" content="%d" />\n' % seconds
