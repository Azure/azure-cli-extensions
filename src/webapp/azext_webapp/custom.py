# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from knack.log import get_logger
from knack.util import CLIError

from azure.mgmt.web.models import (AppServicePlan, SkuDescription, SnapshotRecoveryRequest, SnapshotRecoveryTarget)

from azure.cli.core.commands.client_factory import get_subscription_id

from azure.cli.command_modules.appservice.custom import (
    enable_zip_deploy,
    create_webapp,
    update_app_settings,
    _get_site_credential,
    _get_scm_url,
    get_sku_name,
    list_publish_profiles,
    get_site_configs,
    config_diagnostics)

from azure.cli.command_modules.appservice._appservice_utils import _generic_site_operation

from .create_util import (
    zip_contents_from_dir,
    get_runtime_version_details,
    create_resource_group,
    check_resource_group_exists,
    check_resource_group_supports_os,
    check_if_asp_exists,
    check_app_exists,
    get_lang_from_content,
    web_client_factory
)

from ._constants import (NODE_RUNTIME_NAME, OS_DEFAULT, JAVA_RUNTIME_NAME, STATIC_RUNTIME_NAME)

import time

logger = get_logger(__name__)

# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements


def create_deploy_webapp(cmd, name, location=None, dryrun=False):
    import os
    import json

    client = web_client_factory(cmd.cli_ctx)
    # the code to deploy is expected to be the current directory the command is running from
    src_dir = os.getcwd()

    # if dir is empty, show a message in dry run
    do_deployment = False if os.listdir(src_dir) == [] else True

    # determine the details for app to be created from src contents
    lang_details = get_lang_from_content(src_dir)
    # we support E2E create and deploy for Node & dotnetcore, any other stack, set defaults for os & runtime
    # and skip deployment
    if lang_details['language'] is None:
        do_deployment = False
        sku = 'F1'
        os_val = OS_DEFAULT
        detected_version = '-'
        runtime_version = '-'
    else:
        sku = lang_details.get("default_sku")
        language = lang_details.get("language")
        is_java = language.lower() == JAVA_RUNTIME_NAME
        is_skip_build = is_java or language.lower() == STATIC_RUNTIME_NAME
        os_val = "Linux" if language.lower() == NODE_RUNTIME_NAME or is_java else OS_DEFAULT
        # detect the version
        data = get_runtime_version_details(lang_details.get('file_loc'), language)
        version_used_create = data.get('to_create')
        detected_version = data.get('detected')
        runtime_version = "{}|{}".format(language, version_used_create) if version_used_create != "-" else version_used_create

    if location is None:
        locs = client.list_geo_regions(sku, True)
        available_locs = []
        for loc in locs:
            available_locs.append(loc.geo_region_name)
        location = available_locs[0]
    # Remove spaces from the location string, incase the GeoRegion string is used
    loc_name = location.replace(" ", "")
    full_sku = get_sku_name(sku)

    is_linux = True if os_val == 'Linux' else False

    asp = "appsvc_asp_{}_{}".format(os_val, loc_name)
    rg_name = "appsvc_rg_{}_{}".format(os_val, loc_name)

    str_no_contents_warn = ""
    if not do_deployment:
        str_no_contents_warn = "[Empty directory, no deployment will be triggered]"

    # Resource group: check if default RG is set
    default_rg = cmd.cli_ctx.config.get('defaults', 'group', fallback=None)
    if default_rg and check_resource_group_exists(cmd, default_rg) and check_resource_group_supports_os(cmd, default_rg, location, is_linux):
        rg_name = default_rg
        rg_mssg = "[Using default Resource group]"
    else:
        rg_mssg = ""

    src_path = "{} {}".format(src_dir.replace("\\", "\\\\"), str_no_contents_warn)
    rg_str = "{} {}".format(rg_name, rg_mssg)
    dry_run_str = r""" {
            "name" : "%s",
            "serverfarm" : "%s",
            "resourcegroup" : "%s",
            "sku": "%s",
            "os": "%s",
            "location" : "%s",
            "src_path" : "%s",
            "version_detected": "%s",
            "version_to_create": "%s"
            }
            """ % (name, asp, rg_str, full_sku, os_val, location, src_path,
                   detected_version, runtime_version)
    create_json = json.loads(dry_run_str)

    if dryrun:
        logger.warning("Web app will be created with the below configuration,re-run command "
                       "without the --dryrun flag to create & deploy a new app")
        return create_json

    # create RG if the RG doesn't already exist
    if not check_resource_group_exists(cmd, rg_name):
        logger.warning("Creating Resource group '%s' ...", rg_name)
        create_resource_group(cmd, rg_name, location)
        logger.warning("Resource group creation complete")
    else:
        logger.warning("Resource group '%s' already exists.", rg_name)

    # create asp
    if not check_if_asp_exists(cmd, rg_name, asp):
        logger.warning("Creating App service plan '%s' ...", asp)
        sku_def = SkuDescription(tier=full_sku, name=sku, capacity=(1 if is_linux else None))
        plan_def = AppServicePlan(loc_name, app_service_plan_name=asp,
                                  sku=sku_def, reserved=(is_linux or None))
        client.app_service_plans.create_or_update(rg_name, asp, plan_def)
        logger.warning("App service plan creation complete")
    else:
        logger.warning("App service plan '%s' already exists.", asp)

    # create the app
    if not check_app_exists(cmd, rg_name, name):
        logger.warning("Creating app '%s' ....", name)
        create_webapp(cmd, rg_name, name, asp, runtime_version if is_linux else None)
        logger.warning("Webapp creation complete")
    else:
        logger.warning("App '%s' already exists", name)
    # update create_json to include the app_url
    url = _get_app_url(cmd, rg_name, name)  # picks the custom domain URL incase a domain is assigned

    if do_deployment:
        if not is_skip_build:
            # setting to build after deployment
            logger.warning("Updating app settings to enable build after deployment")
            update_app_settings(cmd, rg_name, name, ["SCM_DO_BUILD_DURING_DEPLOYMENT=true"])
            # work around until the timeout limits issue for linux is investigated & fixed
            # wakeup kudu, by making an SCM call

        _ping_scm_site(cmd, rg_name, name)

        if is_java:
            zip_file_path = src_path + '\\\\' + lang_details.get('file_loc')[0]
        else:
            logger.warning("Creating zip with contents of dir %s ...", src_dir)
            # zip contents & deploy
            zip_file_path = zip_contents_from_dir(src_dir, language)

        logger.warning("Deploying %s contents to app."
                       "This operation can take some time to finish...", '' if is_skip_build else 'and building')
        enable_zip_deploy(cmd, rg_name, name, zip_file_path)
        if not is_java:
            # Remove the file afer deployment, handling exception if user removed the file manually
            try:
                os.remove(zip_file_path)
            except OSError:
                pass
    else:
        logger.warning("No known package (Node, ASP.NET, .NETCORE, Java or Static Html) found skipping zip and deploy process")
    create_json.update({'app_url': url})
    logger.warning("All done.")
    return create_json


def _ping_scm_site(cmd, resource_group, name):
    #  wakeup kudu, by making an SCM call
    import requests
    #  work around until the timeout limits issue for linux is investigated & fixed
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group, name)
    scm_url = _get_scm_url(cmd, resource_group, name)
    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{}:{}'.format(user_name, password))
    requests.get(scm_url + '/api/settings', headers=authorization)


def list_webapp_snapshots(cmd, resource_group, name, slot=None):
    client = web_client_factory(cmd.cli_ctx)
    if slot is None:
        return client.web_apps.list_snapshots(resource_group, name)
    else:
        return client.web_apps.list_snapshots_slot(resource_group, name, slot)


def restore_webapp_snapshot(cmd, resource_group, name, time, slot=None, restore_config=False, source_resource_group=None, source_name=None, source_slot=None):
    client = web_client_factory(cmd.cli_ctx)

    if all([source_resource_group, source_name]):
        sub_id = get_subscription_id(cmd.cli_ctx)
        target_id = "/subscriptions/" + sub_id + "/resourceGroups/" + resource_group + "/providers/Microsoft.Web/sites/" + name
        if slot:
            target_id = target_id + "/slots/" + slot
        target = SnapshotRecoveryTarget(id=target_id)
        request = SnapshotRecoveryRequest(False, snapshot_time=time, recovery_target=target, recover_configuration=restore_config)
        if source_slot:
            return client.web_apps.recover_slot(source_resource_group, source_name, request, source_slot)
        else:
            return client.web_apps.recover(source_resource_group, source_name, request)
    elif any([source_resource_group, source_name]):
        raise CLIError('usage error: --source-resource-group and --source-name must both be specified if one is used')
    else:
        request = SnapshotRecoveryRequest(True, snapshot_time=time, recover_configuration=restore_config)
        if slot:
            return client.web_apps.recover_slot(resource_group, name, request, slot)
        else:
            return client.web_apps.recover(resource_group, name, request)


def _get_app_url(cmd, rg_name, app_name):
    site = _generic_site_operation(cmd.cli_ctx, rg_name, app_name, 'get')
    return "https://" + site.enabled_host_names[0]


def _check_for_ready_tunnel(remote_debugging, tunnel_server):
    from .tunnel import TunnelServer
    default_port = tunnel_server.is_port_set_to_default()
    if default_port is not remote_debugging:
        return True
    return False


def create_tunnel(cmd, resource_group_name, name, port=None, slot=None):
    profiles = list_publish_profiles(cmd, resource_group_name, name, slot)
    user_name = next(p['userName'] for p in profiles)
    user_password = next(p['userPWD'] for p in profiles)
    import threading
    from .tunnel import TunnelServer

    if port is None:
        port = 0  # Will auto-select a free port from 1024-65535
        logger.info('No port defined, creating on random free port')
    tunnel_server = TunnelServer('', port, name, user_name, user_password)
    config = get_site_configs(cmd, resource_group_name, name, slot)
    _ping_scm_site(cmd, resource_group_name, name)

    t = threading.Thread(target=_start_tunnel, args=(tunnel_server, config.remote_debugging_enabled))
    t.daemon = True
    t.start()

    # Wait indefinitely for CTRL-C
    while True:
        time.sleep(5)


def _start_tunnel(tunnel_server, remote_debugging_enabled):
    if not _check_for_ready_tunnel(remote_debugging_enabled, tunnel_server):
        logger.warning('Tunnel is not ready yet, please wait (may take up to 1 minute)')
        while True:
            time.sleep(1)
            logger.warning('.')
            if _check_for_ready_tunnel(remote_debugging_enabled, tunnel_server):
                break
    if remote_debugging_enabled is False:
        logger.warning('SSH is available { username: root, password: Docker! }')
    tunnel_server.start_server()
