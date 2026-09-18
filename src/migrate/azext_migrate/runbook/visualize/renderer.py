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
import os
import re
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


def _workstream_order(graph):
    """Group nodes into workstream swimlanes in source-document order.

    Bands follow the runbook's workstream order (the same order the grid
    uses) so the diagram is not reversed relative to the grid. Within a
    band, nodes keep their layer-sorted order for column layout.
    """
    by_ws = {}
    for node in graph.nodes:
        by_ws.setdefault(node.group or 'Ungrouped', []).append(node)
    ordered = []
    for name, ws_id in graph.group_order:
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
    if kind == viewmodel.KIND_EXECUTION:
        status = step.status or 'NotStarted'
        count = step.workload_progress or '-'
    else:
        status = step.status or 'Unknown'
        count = step.workloads
    return (
        '<div class="row" role="button" tabindex="0" data-step="%d">'
        '<div class="col-step cell-step">'
        '<span class="row__ico">&#9656;</span>'
        '<span class="row__name">%s</span>%s</div>'
        '<div class="col-status"><span class="pill%s">%s</span></div>'
        '<div class="col-dep">%s</div>'
        '<div class="col-count">%s</div>'
        '</div>'
        % (index, _esc(step.name), ref,
           _status_class(status), _esc(status), _esc(dep), _esc(count)))


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
        '<div class="col-count">%s</div></div>' % (status_head, count_head)]
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


def _detail_html(workstream_name, step, kind):
    """Build the step detail-pane markup (shown in the side drawer)."""
    if kind == viewmodel.KIND_EXECUTION:
        entities = ['%s (%s)' % (entity.name, entity.status)
                    if entity.status else entity.name
                    for entity in step.entities]
        body = (
            _field('Step ID', step.id)
            + _status_field('Step status', step.status, 'NotStarted')
            + _field('Workload progress', step.workload_progress)
            + _chip_field('Entities (%d)' % len(entities), entities)
            + _chip_field('Depends on', step.deps))
    else:
        entities = step.entity_names
        body = (
            _field('Step type', step.step_ref)
            + _field('Step ID', step.id)
            + _status_field('Configuration status', step.status, 'Unknown')
            + _chip_field('Entities (%d)' % len(entities), entities)
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
_HELP_CHIPS = (
    ('&#9654;', 'Start execution',
     'Runs the wave and streams live progress in the execution view.',
     'az migrate runbook execution start --resource-group <rg> '
     '--project-name <project> --runbook-name <name>'),
    ('&#65291;', 'Add a step',
     'Adds a step to a workstream in the runbook definition.',
     'az migrate runbook definition step add --resource-group <rg> '
     '--project-name <project> --runbook-name <name> '
     '--step-type <type> --step-name <stepName> --workstream-id <workstream>'),
    ('&#8649;', 'Merge workstreams',
     'Combines two workstreams into a single track.',
     'az migrate runbook definition workstream merge --resource-group <rg> '
     '--project-name <project> --runbook-name <name> '
     '--source-workstream-ids <id1> <id2> --new-workstream-name <name>'),
    ('&#9649;', 'Split a workstream',
     'Splits a workstream into parallel tracks.',
     'az migrate runbook definition workstream split --resource-group <rg> '
     '--project-name <project> --runbook-name <name> '
     '--source-workstream-id <id> --new-workstream-name <name> '
     '--entities-to-move <entity1> <entity2>'),
    ('&#8635;', 'Refresh this view',
     'Regenerates the HTML from the latest runbook definition.',
     'az migrate runbook definition visualize --resource-group <rg> '
     '--project-name <project> --runbook-name <name>'),
)


# CLI cmdlet help chips shown above the execution grid.
_EXEC_HELP_CHIPS = (
    ('&#10073;&#10073;', 'Pause execution',
     'Pauses the in-progress execution so it can be resumed later.',
     'az migrate runbook execution pause --resource-group <rg> '
     '--project-name <project> --runbook-name <name> '
     '--execution-id <id>'),
    ('&#9654;', 'Resume execution',
     'Resumes a paused execution from where it left off.',
     'az migrate runbook execution resume --resource-group <rg> '
     '--project-name <project> --runbook-name <name> '
     '--execution-id <id>'),
    ('&#10005;', 'Cancel execution',
     'Cancels an in-progress or paused execution.',
     'az migrate runbook execution cancel --resource-group <rg> '
     '--project-name <project> --runbook-name <name> '
     '--execution-id <id>'),
    ('&#8635;', 'Refresh this view',
     'Regenerates the HTML from the latest execution status.',
     'az migrate runbook execution visualize --resource-group <rg> '
     '--project-name <project> --runbook-name <name> '
     '--execution-id <id>'),
)


def _help_bar(view):
    """Render the static CLI cmdlet help chips (kind-aware)."""
    if view is None:
        return ''
    chips_src = (_HELP_CHIPS if view.kind == viewmodel.KIND_DEFINITION
                 else _EXEC_HELP_CHIPS)
    chips = ''.join(
        '<button type="button" class="how-chip" data-title="%s" '
        'data-desc="%s" data-cmd="%s">'
        '<span class="how-chip__ico">%s</span>%s</button>'
        % (_esc(title), _esc(desc), _esc(cmd), ico, _esc(title))
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

def render(graph, view=None, refresh_interval=None):
    """Return a complete, self-contained HTML document for the runbook.

    ``graph`` drives the SVG dependency diagram; the optional ``view``
    (:class:`~.viewmodel.RunbookView`) drives the default portal-style grid
    and enables the in-page grid/diagram toggle. When ``refresh_interval`` is
    a positive number of seconds, an offline ``<meta http-equiv="refresh">``
    tag is embedded so a browser viewing the file auto-reloads it from disk on
    that cadence (used by ``--watch`` so the user never has to refresh
    manually). Reloading a local file makes no network call, preserving the
    offline/air-gapped guarantee.
    """
    with open(_TEMPLATE_PATH, encoding='utf-8') as handle:
        template = string.Template(handle.read())
    title = graph.title if view is None else view.title
    step_count = len(graph.nodes) if view is None else view.step_count
    summary = '%d step%s' % (step_count, '' if step_count == 1 else 's')
    generated = _format_generated(
        None if view is None else view.generated)
    grid_html = _grid(view)
    return template.substitute(
        title=_esc(title),
        summary=_esc(summary),
        generated=_esc(generated),
        meta=_meta_block(view),
        help=_help_bar(view),
        details=_grid_details(view),
        legend=_legend(graph, view),
        refresh=_refresh_meta(refresh_interval),
        summary_cards=_summary_cards(view),
        toggle=_toggle(grid_html),
        grid=grid_html,
        grid_hidden='' if grid_html else ' hidden',
        diagram_hidden=' hidden' if grid_html else '',
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
