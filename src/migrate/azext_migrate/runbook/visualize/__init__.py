# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Client-side (non-REST) rendering of runbook definitions/executions.

The visualize package turns a runbook definition or execution JSON
document into a single, self-contained, offline HTML dependency graph.
It is stdlib-only and performs no I/O beyond the caller writing the
returned HTML to disk.
"""
