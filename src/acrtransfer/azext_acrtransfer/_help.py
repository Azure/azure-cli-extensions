# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['acrtransfer'] = """
    type: group
    short-summary: Commands to manage the ACR Transfer feature.
"""

helps['acrtransfer importpipeline'] = """
    type: group
    short-summary: Commands to manage ACR import pipelines.
"""

helps['acrtransfer exportpipeline'] = """
    type: group
    short-summary: Commands to manage ACR export pipelines.
"""

helps['acrtransfer pipelinerun'] = """
    type: group
    short-summary: Commands to manage ACR pipelineruns on both import and export pipelines.
"""

helps['acrtransfer importpipeline create'] = """
    type: command
    short-summary: Create an import pipeline.
    examples: 
        - name: Create an import pipeline.
          text: az acrtransfer importpipeline create -resource-group $MyRG --registry $MyReg --name $MyPipeline --keyvault-secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-account-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer
        - name: Create an import pipeline with a user assigned identity, all available options, and source trigger disabled. 
          text: az acrtransfer importpipeline create -resource-group $MyRG --registry $MyReg --name $MyPipeline --keyvault-secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-account-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer --options DeleteSourceBlobOnSuccess,OverwriteTags,ContinueOnErrors --assign-identity /subscriptions/$MySubID/resourceGroups/$MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$MyIdentity --source-trigger-enabled False
"""

helps['acrtransfer importpipeline list'] = """
    type: command
    short-summary: List import pipelines on a container registry.
    examples: 
        - name: List import pipelines on a container registry
          text: az acrtransfer importpipeline list -resource-group $MyRG --registry $MyReg
"""

helps['acrtransfer importpipeline show'] = """
    type: command
    short-summary: Show an import pipeline in detail. 
    examples: 
        - name: Show a specific import pipeline in detail.
          text: az acrtransfer importpipeline show -resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acrtransfer importpipeline delete'] = """
    type: command
    short-summary: Delete an import pipeline.
    examples: 
        - name: Delete an import pipeline.
          text: az acrtransfer importpipeline delete -resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acrtransfer exportpipeline create'] = """
    type: command
    short-summary: Create an export pipeline.
    examples: 
        - name: Create an export pipeline.
          text: az acrtransfer exportpipeline create -resource-group $MyRG --registry $MyReg --name $MyPipeline --keyvault-secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-account-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer
        - name: Create an export pipeline with a user assigned identity, all available options.
          text: az acrtransfer exportpipeline create -resource-group $MyRG --registry $MyReg --name $MyPipeline --keyvault-secret-uri https://$MyKV.vault.azure.net/secrets/$MySecret --storage-account-container-uri https://$MyStorage.blob.core.windows.net/$MyContainer --options OverwriteBlobs,ContinueOnErrors --assign-identity /subscriptions/$MySubID/resourceGroups/$MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$MyIdentity
"""

helps['acrtransfer exportpipeline list'] = """
    type: command
    short-summary: List export pipelines on a container registry.
    examples: 
        - name: List export pipelines on a container registry
          text: az acrtransfer exportpipeline list -resource-group $MyRG --registry $MyReg
"""

helps['acrtransfer exportpipeline show'] = """
    type: command
    short-summary: Show an export pipeline in detail. 
    examples: 
        - name: Show a specific export pipeline in detail.
          text: az acrtransfer exportpipeline show -resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acrtransfer exportpipeline delete'] = """
    type: command
    short-summary: Delete an export pipeline.
    examples: 
        - name: Delete an export pipeline.
          text: az acrtransfer exportpipeline delete -resource-group $MyRG --registry $MyReg --name $MyPipeline
"""

helps['acrtransfer pipelinerun create'] = """
    type: command
    short-summary: Create a pipeline run.
    examples: 
        - name: Create an import pipeline run.
          text: az acrtransfer pipelinerun create --resource-group $MyRG --registry $MyReg --pipeline $MyPipeline --name $MyPipelineRunName --pipeline-type import --storage-blob $MyBlob
        - name: Create an export pipeline run with force update tag.
          text: az acrtransfer pipelinerun create --resource-group $MyRG --registry $MyReg --pipeline $MyPipeline --name $MyPipelineRunName --pipeline-type export --storage-blob $MyBlob --artifacts hello-world:latest,hello-world@sha256:90659bf80b44ce6be8234e6ff90a1ac34acbeb826903b02cfa0da11c82cbc042 --force-update-tag
"""

helps['acrtransfer pipelinerun list'] = """
    type: command
    short-summary: List pipelineruns of all pipelines on a container registry.
    examples: 
        - name: List all export pipelines on a container registry
          text: az acrtransfer pipelinerun list -resource-group $MyRG --registry $MyReg 
"""

helps['acrtransfer pipelinerun show'] = """
    type: command
    short-summary: Show an export pipeline in detail. 
    examples: 
        - name: Show a specific export pipeline in detail.
          text: az acrtransfer pipelinerun show -resource-group $MyRG --registry $MyReg --name $MyPipelineRun
"""

helps['acrtransfer pipelinerun delete'] = """
    type: command
    short-summary: Delete an export pipeline.
    examples: 
        - name: Delete an export pipeline.
          text: az acrtransfer pipelinerun delete -resource-group $MyRG --registry $MyReg --name $MyPipelineRun
"""
