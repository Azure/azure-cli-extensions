# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.mgmt.resource import ResourceManagementClient
import os
import json

def deploy_arm_template_with_tags(cli_ctx, subscription_id, resource_group_name, deployment_name, template_path, agent_version, cluster_name = None):
    """
    Deploys an ARM template with the specified tags.

    :param subscription_id: Azure subscription ID
    :param resource_group_name: Name of the resource group
    :param deployment_name: Name of the deployment
    :param template_path: Path to the ARM template file
    :param tags: Dictionary of tags to include in the deployment
    """

    print(f"Deploying '{deployment_name}' with tags.")
    credential = _get_data_credentials(cli_ctx, subscription_id)

    # Initialize the resource client
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Load the template
    with open(template_path, "r") as template_file:
        template = json.load(template_file)

    # Define the deployment properties
    deployment_properties = {
        "properties": {
            "mode": "Incremental",
            "template": template,
            "parameters": {}
        },
        "tags": {
            "AgentVersion": agent_version
        }
    }

    if cluster_name:
        deployment_properties["properties"]["parameters"]["clusterName"] = {
            "value": cluster_name
        }

    # Deploy the ARM template
    try:
        deployment = resource_client.deployments.begin_create_or_update(resource_group_name, deployment_name, deployment_properties)
        deployment.result()
    except Exception as e:
        print(f"Arm template deployment failed: {e}")

    print(f"Deployed '{deployment_name}' with tags successfully.")


def delete_arm_template(cli_ctx, subscription_id, resource_group_name, deployment_name):

    print(f"Deleting deployment '{deployment_name}'.")
    credential = _get_data_credentials(cli_ctx, subscription_id)

    # Initialize the resource client
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Delete the ARM template
    try:
        deployment = resource_client.deployments.begin_delete(resource_group_name, deployment_name)
        deployment.result()
    except Exception as e:
        print(f"Arm template deployment failed: {e}")

    print(f"Deleted deployment '{deployment_name}' successfully.")


def _get_data_credentials(cli_ctx, subscription_id=None):
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    creds, _, _ = profile.get_login_credentials(subscription_id=subscription_id)
    return creds