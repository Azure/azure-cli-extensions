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
    text: |-
        Select your active subscription or set defaults with an easy selection
        interface (fzf).

        Filter syntax:

        Token    Match type                  Description
        -------  --------------------------  ----------------------------------
        sbtrkt   fuzzy-match                 Items that match sbtrkt
        'wild    exact-match (quoted)        Items that include wild
        ^music   prefix-exact-match          Items that start with music
        .mp3$    suffix-exact-match          Items that end with .mp3
        !fire    inverse-exact-match         Items that do not include fire
        !^music  inverse-prefix-exact-match  Items that do not start with music
        !.mp3$   inverse-suffix-exact-match  Items that do not end with .mp3

        More information about search syntax or fzf in general can be found on
        the fzf project page: https://github.com/junegunn/fzf#search-syntax
"""

helps['fzf install'] = """
    type: command
    short-summary: download and install the fzf command.
    text: |-
        This command downloads and installs the current fzf binary from GitHub
        into your $AZURE_CONFIG_DIR (usually ~/.azure) for use of this extension.
"""

helps['fzf group'] = """
    type: command
    short-summary: select default resource group.
    parameters:
        - name: -d
          type: bool
          short-summary: Don't change default; just search and return the object.
        - name: -f
          type: string
          short-summary: Filter string for fzf
          long-summary: |-
              Sets a default resource group for your Azure CLI session.

              Filter syntax:

              Token    Match type                  Description
              -------  --------------------------  ----------------------------------
              sbtrkt   fuzzy-match                 Items that match sbtrkt
              'wild    exact-match (quoted)        Items that include wild
              ^music   prefix-exact-match          Items that start with music
              .mp3$    suffix-exact-match          Items that end with .mp3
              !fire    inverse-exact-match         Items that do not include fire
              !^music  inverse-prefix-exact-match  Items that do not start with music
              !.mp3$   inverse-suffix-exact-match  Items that do not end with .mp3

              More information about search syntax or fzf in general can be found on
              the fzf project page: https://github.com/junegunn/fzf#search-syntax
    examples:
        - name: Search for a group with test in the name.
          text: az fzf group -f test
        - name: Search for a group that contains aks
          text: az fzf group -f aks
"""

helps['fzf location'] = """
    type: command
    short-summary: select default location.
    parameters:
        - name: -d
          type: bool
          short-summary: Don't change default; just search and return the object.
        - name: -f
          type: string
          short-summary: Filter string for fzf
          text: |-
              Sets a default resource location for your Azure CLI session. Search will
              be performed across the name, display name, and regional display name. As
              an example, you could search for "australiaeast", "Australia East", or
              "(Asia Pacific) Australia East" and find the same region.

              Filter syntax:

              Token    Match type                  Description
              -------  --------------------------  ----------------------------------
              sbtrkt   fuzzy-match                 Items that match sbtrkt
              'wild    exact-match (quoted)        Items that include wild
              ^music   prefix-exact-match          Items that start with music
              .mp3$    suffix-exact-match          Items that end with .mp3
              !fire    inverse-exact-match         Items that do not include fire
              !^music  inverse-prefix-exact-match  Items that do not start with music
              !.mp3$   inverse-suffix-exact-match  Items that do not end with .mp3

              More information about search syntax or fzf in general can be found on
              the fzf project page: https://github.com/junegunn/fzf#search-syntax
    examples:
        - name: Interactive location search.
          text: az fzf location
        - name: Select the westus2 location.
          text: az fzf location -f westus2
"""

helps['fzf subscription'] = """
    type: command
    short-summary: select default subscription.
    parameters:
        - name: -d
          type: bool
          short-summary: Don't change default; just search and return the object.
        - name: -f
          type: string
          short-summary: Filter string for fzf
          text: |-
              Sets a default subscription for your Azure CLI session. Search will be
              performed across the display name, state, and subscription ID.

              Filter syntax:

              Token    Match type                  Description
              -------  --------------------------  ----------------------------------
              sbtrkt   fuzzy-match                 Items that match sbtrkt
              'wild    exact-match (quoted)        Items that include wild
              ^music   prefix-exact-match          Items that start with music
              .mp3$    suffix-exact-match          Items that end with .mp3
              !fire    inverse-exact-match         Items that do not include fire
              !^music  inverse-prefix-exact-match  Items that do not start with music
              !.mp3$   inverse-suffix-exact-match  Items that do not end with .mp3

              More information about search syntax or fzf in general can be found on the
              fzf project page: https://github.com/junegunn/fzf#search-syntax
    examples:
        - name: Interactive subscription selection
          text: az fzf subscription
        - name: Select subscription best matching "demosub"
          text: az fzf subscription -f demosub
"""
