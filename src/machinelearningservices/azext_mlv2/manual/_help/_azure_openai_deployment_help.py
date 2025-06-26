# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from knack.help_files import helps


def get_azure_openai_deployment_help():
    helps[
        "ml azure-openai-deployment"
    ] = """
        type: group
        short-summary: Manage Azure OpenAI Deployments.
        """
    helps[
        "ml azure-openai-deployment list"
    ] = """
        type: command
        short-summary: List Azure OpenAI deployments.
    """
