# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['codespace'] = """
    type: group
    short-summary: Manage Visual Studio Codespaces.
"""

helps['codespace location'] = """
    type: group
    short-summary: Information on available regions.
"""

helps['codespace location list'] = """
    type: command
    short-summary: List available regions.
"""

helps['codespace location show'] = """
    type: command
    short-summary: Show details on a region.
"""

helps['codespace plan'] = """
    type: group
    short-summary: Manage Codespace plans.
"""

helps['codespace plan create'] = """
    type: command
    short-summary: Create a Codespace plan.
    examples:
        - name: Create a plan in same region as resource group
          text: az codespace plan create -g my-rg -n my-plan
        - name: Create a plan in a specific region
          text: az codespace plan create -g my-rg -n my-plan -l westus2
        - name: Create a plan with tags
          text: az codespace plan create -g my-rg -n my-plan -l westus2 --tags tagname=tagvalue
"""

helps['codespace plan list'] = """
    type: command
    short-summary: List Codespace plans.
    examples:
        - name: List plans
          text: az codespace plan list
        - name: List plans in a given resource group
          text: az codespace plan list -g my-rg
"""

helps['codespace plan delete'] = """
    type: command
    short-summary: Delete a Codespace plan.
    examples:
        - name: Delete a plan
          text: az codespace plan delete -g my-rg -n my-plan
"""

helps['codespace plan show'] = """
    type: command
    short-summary: Show details of a Codespace plan.
    examples:
        - name: Show details of a plan
          text: az codespace plan show -g my-rg -n my-plan
"""

helps['codespace create'] = """
    type: command
    short-summary: Create a Codespace.
    parameters:
        - name: --instance-type
          short-summary: Instance Type
          populator-commands:
              - az codespace location show
    examples:
        - name: Create a Codespace with default settings
          text: az codespace create -g my-rg --plan my-plan --name my-codespace
        - name: Create a Codespace with a different instance type with custom suspend time
          text: az codespace create -g my-rg --plan my-plan --name my-codespace --instance-type premiumLinux --suspend-after 5
        - name: Create a Codespace with a git repo
          text: az codespace create -g my-rg --plan my-plan --name my-codespace --git-repo https://github.com/github/repo --git-user-name "User Name" --git-user-email user@example.com
        - name: Create a Codespace with a dotfiles repo
          text: az codespace create -g my-rg --plan my-plan --name my-codespace --dotfiles-repo https://github.com/github/dotfiles --dotfiles-path ~/dotfiles --dotfiles-command bootstrap.sh
"""

helps['codespace list'] = """
    type: command
    short-summary: List Codespaces.
    examples:
        - name: List Codespaces
          text: az codespace list -g my-rg --plan my-plan
        - name: List Codespaces given plan id and Codespace name
          text: az codespace list --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.VSOnline/plans/my-plan
"""

helps['codespace delete'] = """
    type: command
    short-summary: Delete a Codespace.
    examples:
        - name: Delete a Codespace given name
          text: az codespace delete -g my-rg --plan my-plan --name my-codespace
        - name: Delete a Codespace given id
          text: az codespace delete -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000
        - name: Delete a Codespace given plan id and Codespace name
          text: az codespace delete --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.VSOnline/plans/my-plan --name my-codespace

"""

helps['codespace show'] = """
    type: command
    short-summary: Show details of a Codespace.
    examples:
        - name: Show details of a Codespace given name
          text: az codespace show -g my-rg --plan my-plan --name my-codespace
        - name: Show details of a Codespace given id
          text: az codespace show -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000
        - name: Show details of a Codespace given plan id and Codespace name
          text: az codespace show --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.VSOnline/plans/my-plan --name my-codespace
"""

helps['codespace resume'] = """
    type: command
    short-summary: Resume a Codespace.
    examples:
        - name: Resume a Codespace given name
          text: az codespace resume -g my-rg --plan my-plan --name my-codespace
        - name: Resume a Codespace given id
          text: az codespace resume -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000
        - name: Resume a Codespace given plan id and Codespace name
          text: az codespace resume --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.VSOnline/plans/my-plan --name my-codespace
"""

helps['codespace suspend'] = """
    type: command
    short-summary: Suspend a Codespace.
    examples:
        - name: Suspend a Codespace given name
          text: az codespace suspend -g my-rg --plan my-plan --name my-codespace
        - name: Suspend a Codespace given id
          text: az codespace suspend -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000
        - name: Suspend a Codespace given plan id and Codespace name
          text: az codespace suspend --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.VSOnline/plans/my-plan --name my-codespace
"""

helps['codespace open'] = """
    type: command
    short-summary: Open a Codespace in the web browser.
    long-summary: |
        Confirmation is required if the Codespace is not in the 'Available' state as opening a Codespace will automatically resume it.
    examples:
        - name: Open a Codespace given name
          text: az codespace open -g my-rg --plan my-plan --name my-codespace
        - name: Open a Codespace given id
          text: az codespace open -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000
        - name: Open a Codespace given plan id and Codespace name
          text: az codespace open --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.VSOnline/plans/my-plan --name my-codespace

"""
