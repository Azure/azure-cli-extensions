# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Shared shorthand-syntax parser aligned with Azure CLI conventions.

Wraps the native ``AAZShortHandSyntaxParser`` so our hand-written commands can
accept the same input forms as AAZ-generated commands:

* Full value:    ``"{key:value,key2:value2}"``
* Partial value: ``"key=value"``
* Null/help:     ``"null"`` / ``"??"``
* File input:    ``"@path/to/file.json"`` or ``"@path/to/file.yaml"``

The parser returns a plain ``dict`` for object-shaped inputs. Consumers apply
their own semantic validation on the result.
"""

import json
import os

from azure.cli.core.azclierror import InvalidArgumentValueError

try:
    from azure.cli.core.aaz._utils import AAZShortHandSyntaxParser
    _AAZ_PARSER = AAZShortHandSyntaxParser()
except ImportError:  # pragma: no cover - defensive guard for older core
    _AAZ_PARSER = None


def _load_file(path, allow_yaml):
    """Load a JSON (or YAML when allowed) file into a dict."""
    if not os.path.exists(path):
        raise InvalidArgumentValueError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    suffix = os.path.splitext(path)[1].lower()
    if allow_yaml and suffix in (".yaml", ".yml"):
        try:
            import yaml  # pylint: disable=import-outside-toplevel
        except ImportError as ex:
            raise InvalidArgumentValueError(
                "PyYAML is required to read YAML files. Install it with 'pip install pyyaml'."
            ) from ex
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as ex:
        if allow_yaml:
            try:
                import yaml  # pylint: disable=import-outside-toplevel
                return yaml.safe_load(text)
            except Exception as yex:  # pylint: disable=broad-exception-caught
                raise InvalidArgumentValueError(
                    f"Failed to parse '{path}' as JSON or YAML: {yex}"
                ) from yex
        raise InvalidArgumentValueError(
            f"Failed to parse '{path}' as JSON: {ex}"
        ) from ex


def parse_shorthand(
    raw,
    arg_name="argument",
    allow_yaml_files=False,
    require_object=True,
):
    """Parse a shorthand/JSON/file input into a Python value.

    Parameters
    ----------
    raw : str
        The raw CLI argument value.
    arg_name : str
        Display name used in error messages (e.g. ``hierarchy-spec``).
    allow_yaml_files : bool
        If True, ``@file.yaml`` / ``@file.yml`` are loaded via PyYAML, and
        pre-expanded YAML content strings are accepted.
    require_object : bool
        If True, the final parsed value must be a ``dict``.

    Returns
    -------
    dict | list | str | int | float | bool | None
    """
    if raw is None:
        raise InvalidArgumentValueError(f"--{arg_name}: value is required")
    if not isinstance(raw, str):
        value = raw
    else:
        stripped = raw.strip()
        if not stripped:
            raise InvalidArgumentValueError(f"--{arg_name}: empty value")
        value = _parse_string(stripped, allow_yaml_files, arg_name)

    if require_object and not isinstance(value, dict):
        raise InvalidArgumentValueError(
            f"--{arg_name}: expected an object, got {type(value).__name__}"
        )
    return value


def _parse_string(stripped, allow_yaml, arg_name):
    """Dispatch a stripped, non-empty argument string to the right parser."""
    # 1. Explicit @file (not yet pre-expanded by CLI framework)
    if stripped.startswith("@"):
        return _load_file(stripped[1:], allow_yaml=allow_yaml)

    # 2. Partial-value shorthand: "key=value" (top-level only)
    if _AAZ_PARSER is not None and _AAZ_PARSER.partial_value_key_pattern.match(stripped):
        key, _, val_str = stripped.partition("=")
        try:
            val = _AAZ_PARSER(val_str, is_simple=True) if val_str else ""
        except Exception as ex:  # pylint: disable=broad-exception-caught
            raise InvalidArgumentValueError(
                f"--{arg_name}: failed to parse value for '{key}': {ex}"
            ) from ex
        return {key: val}

    # 3. Strict JSON (catches @file contents that the CLI pre-expanded, and
    #    explicitly quoted JSON inputs).
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # 4. AAZ shorthand syntax: {k:v}, [a,b], 'quoted'.
    #    Tried BEFORE YAML because YAML flow-style greedily parses
    #    "{name:X}" as "{'name:X': None}" (YAML requires ': ' with space).
    if _AAZ_PARSER is not None and (stripped[0] in "{[" or stripped.startswith("'")):
        try:
            return _AAZ_PARSER(stripped)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            raise InvalidArgumentValueError(
                f"--{arg_name}: failed to parse '{stripped}'. {ex}"
            ) from ex

    # 5. YAML content (only when YAML is permitted - i.e. hierarchy-spec).
    #    This is for pre-expanded @file.yaml contents (multi-line YAML).
    if allow_yaml:
        try:
            import yaml  # pylint: disable=import-outside-toplevel
            parsed = yaml.safe_load(stripped)
            if isinstance(parsed, (dict, list)):
                return parsed
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    # 6. Final fallback: AAZ for simple strings / help markers.
    if _AAZ_PARSER is not None:
        try:
            return _AAZ_PARSER(stripped)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            raise InvalidArgumentValueError(
                f"--{arg_name}: failed to parse '{stripped}'. {ex}"
            ) from ex

    raise InvalidArgumentValueError(  # pragma: no cover
        f"--{arg_name}: unable to parse '{stripped}'."
    )


def validate_allowed_keys(data, allowed_keys, arg_name):
    """Raise if ``data`` contains keys outside ``allowed_keys``.

    Case-insensitive; returns a new dict with keys lowered to match registry.
    """
    allowed_lower = {k.lower() for k in allowed_keys}
    normalized = {}
    for key, value in data.items():
        lkey = key.lower() if isinstance(key, str) else key
        if lkey not in allowed_lower:
            raise InvalidArgumentValueError(
                f"--{arg_name}: unknown key '{key}'. "
                f"Allowed keys: {sorted(allowed_keys)}."
            )
        if lkey in normalized:
            raise InvalidArgumentValueError(
                f"--{arg_name}: duplicate key '{lkey}'."
            )
        if value is None or (isinstance(value, str) and not value.strip()):
            raise InvalidArgumentValueError(
                f"--{arg_name}: empty value for key '{lkey}'."
            )
        normalized[lkey] = value if not isinstance(value, str) else value.strip()
    return normalized
