# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module
"""Client-side paging shared by the site-runtime and managed-catalog command paths.

Both catalogs hand back whole collections with no server-side continuation, so the CLI
pages them itself. The token is an opaque base64url envelope carrying the offset, and the
two paths deliberately share this one implementation: they used to carry byte-identical
copies that raised different exception types, so the same malformed token produced a clean
error on one command and an unhandled traceback on another.
"""

import base64
import json

from azure.cli.core.azclierror import InvalidArgumentValueError

from ._json import strict_json_loads

TOKEN_FLAG = "--next-token"


def encode_token(offset):
    raw = json.dumps({"offset": offset}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_token(token):
    if token in (None, ""):
        return 0
    try:
        raw = base64.b64decode(str(token).encode("ascii"), altchars=b"-_", validate=True)
        payload = strict_json_loads(raw.decode("utf-8"))
        offset = payload["offset"]
        if type(offset) is not int:  # pylint: disable=unidiomatic-typecheck
            raise ValueError("offset")
    except (ValueError, KeyError, TypeError, OverflowError, RecursionError) as ex:
        # Anything malformed arrives here as binascii.Error/ValueError/KeyError. It has to be
        # translated: a bare ValueError escaping a command handler is reported by the CLI as
        # an unexpected error, complete with traceback and a link to file an azure-cli bug.
        raise InvalidArgumentValueError(
            "{} is not a valid Logic Apps CLI continuation token. Pass back the "
            "nextContinuationToken value from a previous response.".format(TOKEN_FLAG)) from ex
    if offset < 0:
        raise InvalidArgumentValueError("{} offset must be non-negative.".format(TOKEN_FLAG))
    return offset


def slice_items(items, next_token=None, max_items=None):
    start = decode_token(next_token)
    if max_items is None:
        return items[start:], None
    try:
        count = int(max_items)
    except (TypeError, ValueError, OverflowError) as ex:
        raise InvalidArgumentValueError(
            "--max-items expects a positive integer. Received: {}".format(max_items)) from ex
    if count <= 0:
        raise InvalidArgumentValueError(
            "--max-items expects a positive integer. Received: {}".format(max_items))
    end = start + count
    return items[start:end], encode_token(end) if end < len(items) else None


def operation_kind(kind):
    value = str(kind or "all").strip().lower()
    if value not in ("action", "trigger", "all"):
        raise InvalidArgumentValueError("--kind must be one of: action, trigger, all")
    return value
