# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Extension help for azext_fzf.
"""

from knack.help_files import helps  # pylint: disable=unused-import


helps['fzf'] = """
    type: group
    short-summary: Commands to select active or default objects via fzf.
    long-summary: |-
        Select your active subscription or set defaults with an easy selection interface (fzf).

        Search syntax:

        Token    Match type                  Description
        -------  --------------------------  ----------------------------------
        sbtrkt   fuzzy-match                 Items that match sbtrkt
        'wild    exact-match (quoted)        Items that include wild
        ^music   prefix-exact-match          Items that start with music
        .mp3$    suffix-exact-match          Items that end with .mp3
        !fire    inverse-exact-match         Items that do not include fire
        !^music  inverse-prefix-exact-match  Items that do not start with music
        !.mp3$   inverse-suffix-exact-match  Items that do not end with .mp3

        More information about search syntax or fzf in general can be found on the fzf project page: https://github.com/junegunn/fzf#search-syntax
"""

helps['fzf install'] = """
    type: command
    short-summary: download and install the fzf command.
"""

helps['fzf group'] = """
    type: command
    short-summary: select default resource group.
"""

helps['fzf location'] = """
    type: command
    short-summary: select default location.
"""

helps['fzf subscription'] = """
    type: command
    short-summary: select default subscription.
"""
