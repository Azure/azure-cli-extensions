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
