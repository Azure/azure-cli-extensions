# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Client-side (non-REST) rendering of the runbook parameters editor.

The configure package turns a runbook's ``inputs.json`` (schema + step
inputs) and ``spec.json`` (entity list) into a single, self-contained,
offline HTML page for editing parameters. It is stdlib-only and performs no
I/O beyond the caller writing the returned HTML to disk.
"""
