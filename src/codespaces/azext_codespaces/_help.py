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

helps['codespace plan'] = """
    type: group
    short-summary: Manage Codespace plans.
"""

helps['codespace secret'] = """
    type: group
    short-summary: Manage plan secrets.
"""

helps['codespace location list'] = """
    type: command
    short-summary: List available regions.
"""

helps['codespace location show'] = """
    type: command
    short-summary: Show details of a region.
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
          text: az codespace plan create -g my-rg -n my-plan --tags tagname=tagvalue
        - name: Create a plan with a default instance type
          text: az codespace plan create -g my-rg -n my-plan --default-instance-type premiumLinux
        - name: Create a plan with a default suspend after
          text: az codespace plan create -g my-rg -n my-plan --default-suspend-after 120
        - name: Create a plan associated with a subnet
          text: az codespace plan create -g my-rg -n my-plan --subnet /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.Network/virtualNetworks/my-vnet/subnets/default
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
        - name: Create a Codespace with default plan settings
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
        - name: List Codespaces given plan id
          text: az codespace list --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.Codespaces/plans/my-plan
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
          text: az codespace delete --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.Codespaces/plans/my-plan --name my-codespace
"""

helps['codespace update'] = """
    type: command
    short-summary: Update a Codespace.
    examples:
        - name: Update a Codespace with a different instance type
          text: az codespace update -g my-rg --plan my-plan --name my-codespace --instance-type premiumLinux
        - name: Update a Codespace with a different suspend after
          text: az codespace update -g my-rg --plan my-plan --name my-codespace --suspend-after 30
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
          text: az codespace show --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.Codespaces/plans/my-plan --name my-codespace
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
          text: az codespace resume --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.Codespaces/plans/my-plan --name my-codespace
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
          text: az codespace suspend --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.Codespaces/plans/my-plan --name my-codespace
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
          text: az codespace open --plan /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.Codespaces/plans/my-plan --name my-codespace
"""

helps['codespace secret create'] = """
    type: command
    short-summary: Create a plan secret.
    examples:
        - name: Create a plan secret.
          text: az codespace secret create -g my-rg --plan my-plan --name API_KEY --value "secretkey" --note "service api key"
        - name: Create a plan secret with filters.
          text: az codespace secret create -g my-rg --plan my-plan --name API_KEY --value "secretkey" --filters GitRepo=https://github.com/repo/name CodespaceName=mycodespace
"""

helps['codespace secret update'] = """
    type: command
    short-summary: Update a plan secret.
    examples:
        - name: Update a plan secret with new values.
          text: az codespace secret update -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000 --name API_KEY --value "newsecretkey" --note "service api key"
        - name: Update a plan secret with new filters.
          text: az codespace secret update -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000 --filters GitRepo=https://github.com/repo/name CodespaceName=mycodespace
        - name: Update a plan secret and clear existing filters.
          text: az codespace secret update -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000 --filters ''
"""

helps['codespace secret delete'] = """
    type: command
    short-summary: Delete a plan secret.
    examples:
        - name: Delete a plan secret.
          text: az codespace secret delete -g my-rg --plan my-plan --id 00000000-0000-0000-0000-000000000000
"""

helps['codespace secret list'] = """
    type: command
    short-summary: List plan secrets.
    examples:
        - name: List plan secrets.
          text: az codespace secret list -g my-rg --plan my-plan
"""

helps['codespace set-config'] = """
    type: command
    short-summary: Set configuration for codespace commands.
"""

helps['codespace show-config'] = """
    type: command
    short-summary: Show current configuration for codespace commands.
"""
