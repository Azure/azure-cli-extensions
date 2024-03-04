# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from knack.log import get_logger

from ._client_factory import web_client_factory
logger = get_logger(__name__)


def get_site_availability(cmd, name):
    """ This is used by az webapp up to verify if a site needs to be created or should just be deployed"""
    client = web_client_factory(cmd.cli_ctx)
    availability = client.check_name_availability(name, 'Site')

    # check for "." in app name. it is valid for hostnames to contain it, but not allowed for webapp names
    if "." in name:
        availability.name_available = False
        availability.reason = "Invalid"
        availability.message = ("Site names only allow alphanumeric characters and hyphens, "
                                "cannot start or end in a hyphen, and must be less than 64 chars.")
    return availability


def get_app_details(cmd, name, resource_group):
    from azure.core.exceptions import ResourceNotFoundError as E
    client = web_client_factory(cmd.cli_ctx)
    try:
        return client.web_apps.get(resource_group, name)
    except E:
        return None


# Portal uses the current_stack property in the app metadata to display the correct stack
# This value should be one of: ['dotnet', 'dotnetcore', 'node', 'php', 'python', 'java']
def get_current_stack_from_runtime(runtime):
    language = runtime.split('|')[0].lower()
    if language == 'aspnet':
        return 'dotnet'
    return language


def generate_default_app_service_plan_name(webapp_name):
    import uuid
    random_uuid = str(uuid.uuid4().hex)
    webapp_name = webapp_name[:222]  # max length for app service plan name is 260

    return f'{webapp_name}_plan_{random_uuid}'
