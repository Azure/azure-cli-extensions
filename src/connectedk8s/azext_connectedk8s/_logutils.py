# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import ast


def normalize_container_log(container_log: str | bytes) -> str:
    stripped = container_log.strip()
    if isinstance(stripped, bytes):
        return stripped.decode("utf-8", errors="replace")

    if stripped.startswith(("b'", 'b"')):
        try:
            byte_log = ast.literal_eval(stripped)
        except (SyntaxError, ValueError):
            return stripped
        if isinstance(byte_log, bytes):
            return byte_log.decode("utf-8", errors="replace").strip()

    return stripped


def split_container_log(container_log: str | bytes) -> list[str]:
    return normalize_container_log(container_log).splitlines()
