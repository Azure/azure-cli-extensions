# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Unit tests for `_decode_ws_message`.

Covers the fix for rendering binary WebSocket frames from the Azure Serial
Console stream: bytes must be decoded as UTF-8 so ANSI escape sequences and
multi-byte characters render correctly instead of being emitted via `repr()`.
"""

import pytest

from azext_serialconsole.custom import _decode_ws_message


@pytest.mark.parametrize(
    "message, expected",
    [
        # str passthrough (text-opcode frames).
        pytest.param("hello", "hello", id="str-passthrough"),
        pytest.param("", "", id="str-empty"),
        # bytes / bytearray (binary-opcode frames) decoded as UTF-8.
        pytest.param(b"", "", id="bytes-empty"),
        pytest.param("héllo ✓".encode("utf-8"), "héllo ✓", id="bytes-utf8"),
        pytest.param(
            bytearray("héllo ✓".encode("utf-8")),
            "héllo ✓",
            id="bytearray-utf8",
        ),
        # Colored systemd boot output: escape sequence must survive intact.
        pytest.param(
            b"\x1b[0;32m  OK  \x1b[0m Finished something.\r\n",
            "\x1b[0;32m  OK  \x1b[0m Finished something.\r\n",
            id="ansi-escape-preserved",
        ),
        # cloud-init tables use UTF-8 box-drawing characters.
        pytest.param(
            "┌──────┐".encode("utf-8"), "┌──────┐", id="box-drawing"
        ),
        # errors="replace" keeps the session alive on stray bytes.
        pytest.param(
            b"ok \xff bad", "ok \ufffd bad", id="invalid-utf8-replaced"
        ),
    ],
)
def test_decode_ws_message(message, expected):
    assert _decode_ws_message(message) == expected
