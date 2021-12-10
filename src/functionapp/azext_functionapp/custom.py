# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

logger = get_logger(__name__)


def create_devops_pipeline(
        cmd,
        functionapp_name=None,
        organization_name=None,
        project_name=None,
        repository_name=None,
        overwrite_yaml=None,
        allow_force_push=None,
        github_pat=None,
        github_repository=None
):
    from .azure_devops_build_interactive import AzureDevopsBuildInteractive
    azure_devops_build_interactive = AzureDevopsBuildInteractive(cmd, logger, functionapp_name,
                                                                 organization_name, project_name, repository_name,
                                                                 overwrite_yaml, allow_force_push,
                                                                 github_pat, github_repository)
    return azure_devops_build_interactive.interactive_azure_devops_build()
