# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

from knack.log import get_logger

logger = get_logger(__name__)


def enable_zip_deploy_functionapp(cmd, resource_group_name, name, src, build_remote=False, timeout=None, slot=None):
    from azure.cli.command_modules.appservice.custom import (
        web_client_factory,
        is_plan_consumption,
        enable_zip_deploy,
        add_remote_build_app_settings,
        remove_remote_build_app_settings,
    )
    from azure.cli.core.azclierror import ResourceNotFoundError
    from azure.mgmt.core.tools import parse_resource_id

    client = web_client_factory(cmd.cli_ctx)
    app = client.web_apps.get(resource_group_name, name)
    if app is None:
        raise ResourceNotFoundError(
            "The function app '{}' was not found in resource group '{}'. "
            "Please make sure these values are correct.".format(name, resource_group_name))

    parse_plan_id = parse_resource_id(app.server_farm_id)
    plan_info = None
    retry_delay = 10  # seconds
    # We need to retry getting the plan because sometimes if the plan is created as part of function app,
    # it can take a couple of tries before it gets the plan
    for _ in range(5):
        try:
            plan_info = client.app_service_plans.get(parse_plan_id['resource_group'],
                                                     parse_plan_id['name'])
        except Exception:  # pylint: disable=broad-except
            pass
        if plan_info is not None:
            break
        time.sleep(retry_delay)

    is_consumption = is_plan_consumption(cmd, plan_info)

    # Handle flex function apps if the core CLI supports it
    try:
        from azure.cli.command_modules.appservice.custom import (
            is_flex_functionapp,
            enable_zip_deploy_flex,
            check_flex_app_after_deployment,
        )
        if is_flex_functionapp(cmd.cli_ctx, resource_group_name, name):
            enable_zip_deploy_flex(cmd, resource_group_name, name, src, timeout, slot, build_remote)
            return check_flex_app_after_deployment(cmd, resource_group_name, name)
    except ImportError:
        pass

    build_remote = build_remote is True or build_remote == 'true'
    if (not build_remote) and is_consumption and app.reserved:
        return _upload_zip_to_storage(cmd, resource_group_name, name, src, slot)
    if build_remote and app.reserved:
        add_remote_build_app_settings(cmd, resource_group_name, name, slot)
    elif app.reserved:
        remove_remote_build_app_settings(cmd, resource_group_name, name, slot)

    return enable_zip_deploy(cmd, resource_group_name, name, src, timeout, slot)


def _upload_zip_to_storage(cmd, resource_group_name, name, src, slot=None):
    import datetime
    import os
    import uuid
    from azure.cli.command_modules.appservice.custom import (
        get_app_settings,
        update_app_settings,
        web_client_factory,
    )
    from azure.cli.core.profiles import ResourceType, get_sdk

    settings = get_app_settings(cmd, resource_group_name, name, slot)
    storage_connection = None
    for keyval in settings:
        if keyval['name'] == 'AzureWebJobsStorage':
            storage_connection = str(keyval['value'])

    container_name = "function-releases"
    blob_name = "{}-{}.zip".format(datetime.datetime.today().strftime('%Y%m%d%H%M%S'), str(uuid.uuid4()))
    BlobServiceClient = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE_BLOB,
                                '_blob_service_client#BlobServiceClient')
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=storage_connection)
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    # https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
    def progress_callback(current, total):
        total_length = 30
        filled_length = int(round(total_length * current) / float(total))
        percents = round(100.0 * current / float(total), 1)
        progress_bar = '=' * filled_length + '-' * (total_length - filled_length)
        progress_message = 'Uploading {} {}%'.format(progress_bar, percents)
        cmd.cli_ctx.get_progress_controller().add(message=progress_message)

    blob_client = None
    with open(os.path.realpath(os.path.expanduser(src)), 'rb') as fs:
        zip_content = fs.read()
        blob_client = container_client.upload_blob(blob_name, zip_content, validate_content=True,
                                                   progress_hook=progress_callback)

    now = datetime.datetime.utcnow()
    blob_start = now - datetime.timedelta(minutes=10)
    blob_end = now + datetime.timedelta(weeks=520)
    BlobSharedAccessSignature = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE_BLOB,
                                        '_shared_access_signature#BlobSharedAccessSignature')
    BlobSasPermissions = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE_BLOB, '_models#BlobSasPermissions')
    sas_client = BlobSharedAccessSignature(blob_service_client.account_name,
                                           account_key=blob_service_client.credential.account_key)
    blob_token = sas_client.generate_blob(container_name, blob_name, permission=BlobSasPermissions(read=True),
                                          expiry=blob_end, start=blob_start)

    blob_uri = blob_client.url
    if '?' not in blob_uri:
        blob_uri += '?' + blob_token
    website_run_from_setting = "WEBSITE_RUN_FROM_PACKAGE={}".format(blob_uri)
    update_app_settings(cmd, resource_group_name, name, settings=[website_run_from_setting], slot=slot)

    client = web_client_factory(cmd.cli_ctx)
    try:
        logger.info('\nSyncing Triggers...')
        if slot is not None:
            client.web_apps.sync_function_triggers_slot(resource_group_name, name, slot)
        else:
            client.web_apps.sync_function_triggers(resource_group_name, name)
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning('\nWarning: Unable to sync triggers. %s', ex)


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
