# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['storage blob filter'] = """
type: command
short-summary: List blobs across all containers whose tags match a given search expression.
parameters:
  - name: --tag-filter
    short-summary: >
            The expression to find blobs whose tags matches the specified condition.
            eg. ""yourtagname"='firsttag' and "yourtagname2"='secondtag'"
"""

helps['storage blob tag'] = """
type: group
short-summary: Manage blob tags.
"""

helps['storage blob tag list'] = """
type: command
short-summary: Get tags on a blob or specific blob version, or snapshot.
"""

helps['storage blob tag set'] = """
type: command
short-summary: Set tags on a blob or specific blob version, but not snapshot.
long-summary: >
    Each call to this operation replaces all existing tags attached to the blob. To remove all
    tags from the blob, call this operation with no tags set.
"""
