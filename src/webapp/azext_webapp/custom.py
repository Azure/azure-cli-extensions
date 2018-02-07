# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from knack.log import get_logger

from azure.mgmt.web.models import (AppServicePlan, SkuDescription)

from azure.cli.command_modules.appservice.custom import (
    enable_zip_deploy,
    create_webapp,
    update_app_settings,
    _get_site_credential,
    _get_scm_url,
    _get_sku_name)

from .create_util import (
    zip_contents_from_dir,
    is_node_application,
    get_node_runtime_version_toSet,
    create_resource_group,
    check_resource_group_exists,
    check_resource_group_supports_linux,
    check_if_asp_exists,
    check_app_exists,
    web_client_factory
)

logger = get_logger(__name__)

# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements


def create_deploy_webapp(cmd, name, location=None, dryrun=False):
    import os
    import json

    client = web_client_factory(cmd.cli_ctx)
    sku = "S1"
    os_val = "Linux"
    language = "node"
    full_sku = _get_sku_name(sku)

    if location is None:
        locs = client.list_geo_regions(sku, True)
        available_locs = []
        for loc in locs:
            available_locs.append(loc.geo_region_name)
        location = available_locs[0]

    # Remove spaces from the location string, incase the GeoRegion string is used
    loc_name = location.replace(" ", "")

    asp = "appsvc_asp_{}_{}".format(os_val, loc_name)
    rg_name = "appsvc_rg_{}_{}".format(os_val, loc_name)

    # the code to deploy is expected to be the current directory the command is running from
    src_dir = os.getcwd()

    # if dir is empty, show a message in dry run
    do_deployment = False if os.listdir(src_dir) == [] else True
    package_json_path = is_node_application(src_dir)

    str_no_contents_warn = ""
    if not do_deployment:
        str_no_contents_warn = "[Empty directory, no deployment will be triggered]"

    if package_json_path == '':
        node_version = "[No package.json file found in root directory, not a Node app?]"
        version_used_create = "8.0"
    else:
        with open(package_json_path) as data_file:
            data = json.load(data_file)
            node_version = data['version']
            version_used_create = get_node_runtime_version_toSet()

    # Resource group: check if default RG is set
    default_rg = cmd.cli_ctx.config.get('defaults', 'group', fallback=None)
    if default_rg and check_resource_group_supports_linux(cmd, default_rg, location):
        rg_name = default_rg
        rg_mssg = "[Using default Resource group]"
    else:
        rg_mssg = ""

    runtime_version = "{}|{}".format(language, version_used_create)
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
                   node_version, runtime_version)

    create_json = json.dumps(json.loads(dry_run_str), indent=4, sort_keys=True)
    if dryrun:
        logger.warning("Web app will be created with the below configuration,re-run command "
                       "without the --dryrun flag to create & deploy a new app")
        logger.warning(create_json)
        return None

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
        sku_def = SkuDescription(tier=full_sku, name=sku, capacity=1)
        plan_def = AppServicePlan(loc_name, app_service_plan_name=asp,
                                  sku=sku_def, reserved=True)
        client.app_service_plans.create_or_update(rg_name, asp, plan_def)
        logger.warning("App service plan creation complete")
    else:
        logger.warning("App service plan '%s' already exists.", asp)

    # create the Linux app
    if not check_app_exists(cmd, rg_name, name):
        logger.warning("Creating app '%s' ....", name)
        create_webapp(cmd, rg_name, name, asp, runtime_version)
        logger.warning("Webapp creation complete")
    else:
        logger.warning("App '%s' already exists", name)

    # setting to build after deployment
    logger.warning("Updating app settings to enable build after deployment")
    update_app_settings(cmd, rg_name, name, ["SCM_DO_BUILD_DURING_DEPLOYMENT=true"])
    # work around until the timeout limits issue for linux is investigated & fixed
    # wakeup kudu, by making an SCM call

    import requests
    # work around until the timeout limits issue for linux is investigated & fixed
    user_name, password = _get_site_credential(cmd.cli_ctx, rg_name, name)
    scm_url = _get_scm_url(cmd, rg_name, name)
    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    requests.get(scm_url + '/api/settings', headers=authorization)

    if package_json_path != '':
        logger.warning("Creating zip with contents of dir %s ...", src_dir)
        # zip contents & deploy
        zip_file_path = zip_contents_from_dir(src_dir)

        logger.warning("Deploying and building contents to app."
                       "This operation can take some time to finish...")
        enable_zip_deploy(cmd, rg_name, name, zip_file_path)
    else:
        logger.warning("No package.json found, skipping zip and deploy process")

    logger.warning("All done. %s", create_json)
    return None
