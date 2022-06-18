# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['acr import-pipeline'] = """
    type: group
    short-summary: Manage ACR import pipelines.
"""

helps['acr export-pipeline'] = """
    type: group
    short-summary: Manage ACR export pipelines.
"""

helps['acr pipeline-run'] = """
    type: group
    short-summary: Manage ACR import and export pipeline-runs.
"""

helps['acr import-pipeline create'] = """
    type: command
    short-summary: Create an import pipeline.
    examples:
        - name: Create an import pipeline.
          text: az acr import-pipeline create --resource-group $MyRG --registry $MyReg --name $MyPipeline --secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer
        - name: Create an import pipeline with a user-assigned identity, all available options, and source trigger disabled.
          text: az acr import-pipeline create --resource-group $MyRG --registry $MyReg --name $MyPipeline --secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer --options DeleteSourceBlobOnSuccess OverwriteTags ContinueOnErrors --assign-identity /subscriptions/$MySubID/resourceGroups/$MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$MyIdentity --source-trigger-enabled False
"""

helps['acr import-pipeline list'] = """
    type: command
    short-summary: List import pipelines on a Container Registry.
    examples:
        - name: List import pipelines on a container registry
          text: az acr import-pipeline list --resource-group $MyRG --registry $MyReg
"""

helps['acr import-pipeline show'] = """
    type: command
    short-summary: Show an import pipeline in detail.
    examples:
        - name: Show a specific import pipeline in detail.
          text: az acr import-pipeline show --resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acr import-pipeline delete'] = """
    type: command
    short-summary: Delete an import pipeline.
    examples:
        - name: Delete an import pipeline.
          text: az acr import-pipeline delete --resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acr export-pipeline create'] = """
    type: command
    short-summary: Create an export pipeline.
    examples:
        - name: Create an export pipeline.
          text: az acr export-pipeline create --resource-group $MyRG --registry $MyReg --name $MyPipeline --secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer
        - name: Create an export pipeline with a user-assigned identity and all available options.
          text: az acr export-pipeline create --resource-group $MyRG --registry $MyReg --name $MyPipeline --secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer --options OverwriteBlobs ContinueOnErrors --assign-identity /subscriptions/$MySubID/resourceGroups/$MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$MyIdentity
"""

helps['acr export-pipeline list'] = """
    type: command
    short-summary: List export pipelines on a Container Registry.
    examples:
        - name: List export pipelines on a container registry
          text: az acr export-pipeline list --resource-group $MyRG --registry $MyReg
"""

helps['acr export-pipeline show'] = """
    type: command
    short-summary: Show an export pipeline in detail.
    examples:
        - name: Show a specific export pipeline in detail.
          text: az acr export-pipeline show --resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acr export-pipeline delete'] = """
    type: command
    short-summary: Delete an export pipeline.
    examples:
        - name: Delete an export pipeline.
          text: az acr export-pipeline delete --resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acr pipeline-run create'] = """
    type: command
    short-summary: Create a pipeline-run.
    examples:
        - name: Create an import pipeline-run.
          text: az acr pipeline-run create --resource-group $MyRG --registry $MyReg --pipeline $MyPipeline --name $MyPipelineRunName --pipeline-type import --storage-blob $MyBlob
        - name: Create an export pipeline-run and force redeploy.
          text: az acr pipeline-run create --resource-group $MyRG --registry $MyReg --pipeline $MyPipeline --name $MyPipelineRunName --pipeline-type export --storage-blob $MyBlob --artifacts hello-world:latest hello-world@sha256:90659bf80b44ce6be8234e6ff90a1ac34acbeb826903b02cfa0da11c82cbc042 --force-redeploy
"""

helps['acr pipeline-run list'] = """
    type: command
    short-summary: List pipeline-runs of all pipelines on a container registry.
    examples:
        - name: List all pipeline-runs on a container registry
          text: az acr pipeline-run list --resource-group $MyRG --registry $MyReg
"""

helps['acr pipeline-run show'] = """
    type: command
    short-summary: Show a pipeline-run in detail.
    examples:
        - name: Show a specific pipeline-run in detail.
          text: az acr pipeline-run show --resource-group $MyRG --registry $MyReg --name $MyPipelineRun
"""

helps['acr pipeline-run delete'] = """
    type: command
    short-summary: Delete a pipeline-run.
    examples:
        - name: Delete a pipeline-run.
          text: az acr pipeline-run delete --resource-group $MyRG --registry $MyReg --name $MyPipelineRun
"""

helps['acr pipeline-run clean'] = """
    type: command
    short-summary: Delete all failed pipeline-runs on the registry.
    examples:
        - name: Delete all failed pipeline-runs on the registry.
          text: az acr pipeline-run clean --resource-group $MyRG --registry $MyReg
        - name: List the failed pipeline-runs that would have been deleted, but do not delete any.
          text: az acr pipeline-run clean --resource-group $MyRG --registry $MyReg --dry-run -o table
"""
