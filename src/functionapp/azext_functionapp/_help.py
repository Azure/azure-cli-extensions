# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['functionapp devops-pipeline'] = """
type: group
short-summary: Azure Function specific integration with Azure DevOps. Please visit https://aka.ms/functions-azure-devops for more information.
"""

helps['functionapp devops-pipeline create'] = """
type: command
short-summary: Create an Azure DevOps pipeline for a function app.
examples:
  - name: create an Azure Pipeline to a function app.
    text: >
        az functionapp devops-pipeline create --functionapp-name FunctionApp
  - name: create an Azure Pipeline from a Github function app repository.
    text: >
        az functionapp devops-pipeline create --github-repository GithubOrganization/GithubRepository --github-pat GithubPersonalAccessToken
  - name: create an Azure Pipeline with specific Azure DevOps organization and project
    text: >
        az functionapp devops-pipeline create --organization-name AzureDevOpsOrganization --project-name AzureDevOpsProject
"""

helps['functionapp scale config always-ready'] = """
type: group
short-summary: Manage always-ready instance settings for a Flex Consumption function app.
"""

helps['functionapp scale config always-ready delete'] = """
type: command
short-summary: Delete always-ready settings for a Flex Consumption function app.
examples:
  - name: Delete always-ready settings by name.
    text: >
        az functionapp scale config always-ready delete --resource-group MyResourceGroup --name MyFunctionApp --setting-names http function:Function1
"""
