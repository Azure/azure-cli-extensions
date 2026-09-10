# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Download and safely extract SAS-protected ZIP artifacts.

Several runbook endpoints (``GenerateDownloadUrl``) return a pre-signed
blob SAS URL that points at a ZIP. The SAS is self-authorizing, so the
blob is fetched with a plain HTTPS GET (no ARM token) and then extracted
with guards against path traversal (zip-slip) and decompression bombs.
"""

import io
import json
import os
import tempfile
import zipfile
from urllib.request import Request, urlopen

from knack.log import get_logger

from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
)

logger = get_logger(__name__)

# Guard rails for the untrusted archive we extract.
_MAX_TOTAL_UNCOMPRESSED = 256 * 1024 * 1024
_MAX_MEMBERS = 1000

# Keys a GenerateDownloadUrl / GenerateInputUploadUrl response may use for
# the SAS URL, checked both at the top level and under ``properties``.
_SAS_URL_KEYS = (
    'uploadUrl', 'uploadUri', 'downloadUrl', 'downloadUri',
    'sasUrl', 'sasUri', 'url', 'uri')

# Derived/computed inputs the CLI must never surface or download. This
# document shares the 'runbookInputs' shape with the user parameters, so it
# can only be distinguished by name (content classification is not enough).
# Both the legacy and post-rename (inputs -> parameters) names are excluded.
_DERIVED_INPUTS_NAMES = (
    'system-derived-inputs.json', 'system-derived-parameters.json')

# Suffix identifying the execution status document (``executionStatus.json``)
# fetched via a per-execution SAS download (GenerateDownloadUrl on the
# execution resource). The blob may be the raw status bytes or a ZIP that
# contains it; read_status_json handles both (``status.json`` suffix also
# matches the renamed ``executionStatus.json``).
_STATUS_SUFFIX = 'status.json'

# Local ZIP file magic; a SAS download may be a ZIP archive or a raw blob.
_ZIP_MAGIC = b'PK\x03\x04'


def _is_zip(data):
    """True when ``data`` starts with the local ZIP file signature."""
    return isinstance(data, (bytes, bytearray)) and data[:4] == _ZIP_MAGIC


def extract_sas_url(response_body):
    """Return the download URL from a GenerateDownloadUrl response body."""
    if not isinstance(response_body, dict):
        return None
    for source in (response_body, response_body.get('properties')):
        if not isinstance(source, dict):
            continue
        for key in _SAS_URL_KEYS:
            value = source.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def download_bytes(url):
    """HTTP GET a self-authorizing https URL and return the raw bytes."""
    if not isinstance(url, str) or not url.lower().startswith('https://'):
        raise InvalidArgumentValueError(
            'The download URL must be an absolute https URL.')
    request = Request(url, method='GET')
    # The URL is a pre-signed blob SAS returned by ARM and validated above
    # to be https; no ARM token is attached.
    with urlopen(request) as response:  # nosec B310
        return response.read()


def upload_bytes(url, data):
    """HTTP PUT raw bytes to a self-authorizing https blob SAS URL."""
    if not isinstance(url, str) or not url.lower().startswith('https://'):
        raise InvalidArgumentValueError(
            'The upload URL must be an absolute https URL.')
    request = Request(
        url, data=data, method='PUT',
        headers={'x-ms-blob-type': 'BlockBlob'})
    # The URL is a pre-signed blob SAS returned by ARM and validated above
    # to be https; no ARM token is attached. The SAS query string carries
    # the signature, so only the blob path (before '?') is logged.
    logger.debug(
        'Uploading %d bytes to blob %s', len(data), url.split('?', 1)[0])
    with urlopen(request) as response:  # nosec B310
        logger.debug('Blob upload completed (HTTP %s).', response.status)
        return None


def _looks_like_spec(parsed):
    """True when a parsed JSON document is a runbook definition/spec."""
    return isinstance(parsed, dict) and (
        'spec' in parsed or 'workstreams' in parsed)


def _looks_like_parameters(parsed):
    """True when a parsed JSON document is a runbook parameters file."""
    return isinstance(parsed, dict) and (
        'inputs' in parsed
        or 'stepInputs' in parsed
        or 'schema' in parsed)


def _looks_like_status(parsed):
    """True when a parsed JSON document is an execution status document.

    The per-execution download archive can also carry the definition
    (wrapped in ``spec``) and the input parameters (``inputs`` / ``schema``
    / ``stepInputs``); neither is a status document. A status document is
    wrapped in ``executionStatus`` (or is a bare ``workstreams`` shape), so
    it is anything that is a dict and is not the definition or parameters.
    """
    return (isinstance(parsed, dict)
            and 'spec' not in parsed
            and not _looks_like_parameters(parsed))


def _classify_archive(zip_bytes):
    """Sort the GenerateDownloadUrl archive members by role.

    Returns ``{'definition': (name, bytes) | None,
    'parameters': (name, bytes) | None, 'docs': [(name, bytes), ...]}``.

    The archive ships the definition (``runbookSpec``), the user parameters
    (``runbookInputs``), the ``system-derived-inputs.json`` computed inputs,
    and a documentation markdown. ``system-derived-inputs.json`` shares the
    parameters shape and is distinguished only by name, so it is skipped
    here; every other member is classified by content. This is the single
    source of truth for the archive layout.
    """
    definition = parameters = None
    docs = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        _guard_archive(archive.infolist())
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = os.path.basename(info.filename.replace('\\', '/'))
            lower = name.lower()
            if lower in _DERIVED_INPUTS_NAMES:
                continue
            data = archive.read(info)
            if lower.endswith('.md'):
                docs.append((name, data))
                continue
            if not lower.endswith('.json'):
                continue
            try:
                parsed = json.loads(data.decode('utf-8'))
            except ValueError:
                continue
            if definition is None and _looks_like_spec(parsed):
                definition = (name, data)
            elif parameters is None and _looks_like_parameters(parsed):
                parameters = (name, data)
    return {
        'definition': definition, 'parameters': parameters, 'docs': docs}


def read_spec_json(zip_bytes):
    """Return the parsed runbook definition (``runbookSpec``) or None.

    Accepts either a ZIP archive (definition classified out of it) or a raw
    ``spec.json`` blob (file-mode download), returning the parsed JSON.
    """
    if not _is_zip(zip_bytes):
        try:
            return json.loads(zip_bytes.decode('utf-8'))
        except ValueError:
            return None
    found = _classify_archive(zip_bytes)['definition']
    return json.loads(found[1].decode('utf-8')) if found else None


def describe_archive(zip_bytes):
    """Summarize a download for diagnostics: each member and its detected role.

    Returns a short string such as ``spec.json (definition), inputs.json
    (parameters), runbook.md (docs)`` so a "definition not found" failure can
    tell whether the archive genuinely lacks a definition or the member was
    rejected by the content classifier (e.g. an unexpected contract shape).
    """
    if not _is_zip(zip_bytes):
        return 'raw non-archive blob'
    roles = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = os.path.basename(info.filename.replace('\\', '/'))
            lower = name.lower()
            if lower in _DERIVED_INPUTS_NAMES:
                roles.append('%s (derived-inputs, skipped)' % name)
            elif lower.endswith('.md'):
                roles.append('%s (docs)' % name)
            elif not lower.endswith('.json'):
                roles.append('%s (ignored)' % name)
            else:
                try:
                    parsed = json.loads(archive.read(info).decode('utf-8'))
                except ValueError:
                    roles.append('%s (invalid JSON)' % name)
                    continue
                if _looks_like_spec(parsed):
                    roles.append('%s (definition)' % name)
                elif _looks_like_parameters(parsed):
                    roles.append('%s (parameters)' % name)
                else:
                    roles.append('%s (unrecognized)' % name)
    return ', '.join(roles) if roles else 'empty archive'


def read_schema_json(zip_bytes):
    """Return the parsed standalone ``schema.json`` from the archive, or None.

    When the input schema is shipped as its own file (rather than embedded in
    ``inputs.json``), configure/validation read it here. A standalone schema
    document is keyed by step type and matches neither the definition nor the
    parameters content classifiers, so it is located by name.
    """
    if not _is_zip(zip_bytes):
        return None
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        _guard_archive(archive.infolist())
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = os.path.basename(info.filename.replace('\\', '/')).lower()
            if name == 'schema.json':
                try:
                    return json.loads(archive.read(info).decode('utf-8'))
                except ValueError:
                    return None
    return None


def extract_parameters_file(zip_bytes):
    """Return ``(filename, raw_bytes)`` for the user parameters, or None.

    ``system-derived-inputs.json`` (which shares the parameters shape) is
    never returned; see :func:`_classify_archive`. A raw (non-ZIP) blob
    carries no separate parameters file, so None is returned.
    """
    if not _is_zip(zip_bytes):
        return None
    return _classify_archive(zip_bytes)['parameters']


def read_parameters_json(zip_bytes):
    """Return the parsed ``inputs`` object from the ZIP, or None."""
    found = extract_parameters_file(zip_bytes)
    if not found:
        return None
    parsed = json.loads(found[1].decode('utf-8'))
    if isinstance(parsed, dict) and isinstance(
            parsed.get('inputs'), dict):
        return parsed['inputs']
    return parsed


def read_status_json(raw_bytes):
    """Return the parsed execution status document from a SAS download.

    The per-execution SAS blob may be either the raw ``executionStatus.json``
    bytes or a ZIP archive that contains it. A not-yet-run execution's download
    archive ships only the input parameters (``runbookInputs``) and/or the
    definition (``runbookSpec``); those are NOT a status document and are
    rejected here so callers can fall back to the execution resource. Raises
    :class:`CLIInternalError` when no status document is present.
    """
    if raw_bytes[:4] == b'PK\x03\x04':
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as archive:
            _guard_archive(archive.infolist())
            named = typed = None
            for info in archive.infolist():
                if info.is_dir():
                    continue
                base = os.path.basename(info.filename.replace('\\', '/'))
                lower = base.lower()
                if lower in _DERIVED_INPUTS_NAMES \
                        or not lower.endswith('.json'):
                    continue
                try:
                    parsed = json.loads(archive.read(info).decode('utf-8'))
                except ValueError:
                    continue
                if not _looks_like_status(parsed):
                    continue
                if lower.endswith(_STATUS_SUFFIX):
                    named = parsed
                    break
                if typed is None:
                    typed = parsed
            status = named if named is not None else typed
            if status is None:
                raise CLIInternalError(
                    'The downloaded archive did not contain an execution '
                    'status file.')
            return status
    parsed = json.loads(raw_bytes.decode('utf-8'))
    if not _looks_like_status(parsed):
        raise CLIInternalError(
            'The download did not contain an execution status document.')
    return parsed


def read_json_file(path):
    """Read and parse a local JSON file, returning the parsed object.

    Enables offline rendering/testing of the visualize commands from
    definition/parameters/status JSON files without contacting the service.
    The file is read as bytes so ``json.loads`` can auto-detect the encoding
    (UTF-8/16/32, with or without a BOM); this tolerates files saved by
    Windows PowerShell redirection, which default to UTF-16.
    """
    with open(path, 'rb') as handle:
        return json.loads(handle.read())


def resolve_output_path(file, default_name):
    """Resolve a user ``--file`` value to an absolute output file path.

    ``file`` may be ``None`` (write ``default_name`` into the current
    directory), a directory (write ``default_name`` inside it), or a full
    file path. A value that names a not-yet-created directory -- one that
    ends with a path separator or has no file extension -- is treated as a
    directory so ``default_name`` is written inside it (rather than becoming
    an extensionless output file). The result is always an absolute,
    normalized path.
    """
    if not file:
        return os.path.join(os.getcwd(), default_name)
    looks_like_dir = (
        file.endswith(('/', '\\')) or os.path.splitext(file)[1] == '')
    target = os.path.abspath(file)
    if os.path.isdir(target):
        return os.path.join(target, default_name)
    if looks_like_dir and not os.path.isfile(target):
        return os.path.join(target, default_name)
    return target


def write_text(path, text):
    """Write ``text`` (UTF-8) to ``path`` atomically, creating parent dirs.

    The content is written to a temporary file in the same directory and then
    atomically moved into place with :func:`os.replace`. This guarantees a
    reader (e.g. a browser auto-reloading the file during ``--watch``) never
    observes a partially written file.
    """
    absolute = os.path.abspath(path)
    parent = os.path.dirname(absolute)
    if parent:
        os.makedirs(parent, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix='.runbook-', suffix='.tmp', dir=parent or None)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(text)
        os.replace(tmp, absolute)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    return absolute


def open_in_browser(path, required=False):
    """Open a local file in the default browser; return True on success.

    ``visualize`` passes ``required=True`` so it fails loudly when no browser
    can be launched (the HTML is already written, so the message points to it
    and to ``--no-open``). Other callers open best-effort.
    """
    import webbrowser
    url = 'file://' + os.path.abspath(path)
    try:
        opened = bool(webbrowser.open(url))
    except (OSError, webbrowser.Error) as ex:  # pragma: no cover
        logger.debug('Could not open a browser: %s', ex)
        opened = False
    if not opened and required:
        raise CLIInternalError(
            'Rendered the HTML file but could not open a browser to display '
            "it: {}. Open the file manually, or re-run with '--no-open'."
            .format(path))
    return opened


def extract_definition_files(zip_bytes, destination):
    """Write the runbook definition, its parameters and docs to disk.

    Writes the definition (``runbookSpec``), the user parameters
    (``runbookInputs``) and any ``.md`` docs; the redundant
    ``derived-input.json`` is skipped (see :func:`_classify_archive`). The
    parameters file is downloaded because the definition's per-step
    ``configurationStatus`` is computed from it, but callers still render only
    the definition in table/CLI output. Member names are flattened to their
    base name, so a hostile archive path cannot escape ``destination``
    (zip-slip is designed out rather than checked at write time). Returns the
    absolute paths written.
    """
    destination = os.path.abspath(destination)
    os.makedirs(destination, exist_ok=True)
    if not _is_zip(zip_bytes):
        target = os.path.join(destination, 'runbook.json')
        with open(target, 'wb') as handle:
            handle.write(zip_bytes)
        return [target]
    classified = _classify_archive(zip_bytes)
    selected = list(classified['docs'])
    if classified['definition']:
        selected.insert(0, classified['definition'])
    if classified['parameters']:
        selected.append(classified['parameters'])
    written = []
    for name, data in selected:
        target = os.path.join(destination, os.path.basename(name))
        with open(target, 'wb') as handle:
            handle.write(data)
        written.append(target)
    return written


# Parameter-side files shipped alongside ``inputs.json`` (schema is moving to
# its own file; captured by name for forward-compatibility).
_PARAM_EXTRA_NAMES = ('schema.json',)


def extract_parameter_files(zip_bytes, destination):
    """Write the runbook parameters file(s) to ``destination``.

    Writes the user parameters (``inputs.json``) and, when the schema is
    shipped as its own file, ``schema.json`` (needed for validation). The
    definition, docs and the redundant ``system-derived-inputs.json`` are
    skipped. A raw (non-ZIP) blob is written as ``inputs.json``. Member names
    are flattened to their base name (zip-slip is designed out). Returns the
    absolute paths written.
    """
    destination = os.path.abspath(destination)
    os.makedirs(destination, exist_ok=True)
    if not _is_zip(zip_bytes):
        target = os.path.join(destination, 'inputs.json')
        with open(target, 'wb') as handle:
            handle.write(zip_bytes)
        return [target]
    selected = []
    parameters = _classify_archive(zip_bytes)['parameters']
    if parameters:
        selected.append(parameters)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        _guard_archive(archive.infolist())
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = os.path.basename(info.filename.replace('\\', '/'))
            if name.lower() in _PARAM_EXTRA_NAMES:
                selected.append((name, archive.read(info)))
    written = []
    seen = set()
    for name, data in selected:
        base = os.path.basename(name)
        if base in seen:
            continue
        seen.add(base)
        target = os.path.join(destination, base)
        with open(target, 'wb') as handle:
            handle.write(data)
        written.append(target)
    return written


def _guard_archive(infos):
    """Reject archives with too many members or an implausible size."""
    if len(infos) > _MAX_MEMBERS:
        raise CLIInternalError(
            'Downloaded archive has too many entries.')
    if sum(i.file_size for i in infos) > _MAX_TOTAL_UNCOMPRESSED:
        raise CLIInternalError(
            'Downloaded archive is unexpectedly large.')
