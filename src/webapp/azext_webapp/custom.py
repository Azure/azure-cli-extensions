# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
import json
from knack.log import get_logger
from azure.mgmt.web.models import (AppServicePlan, SkuDescription)
from azure.cli.command_modules.appservice.custom import (
    create_webapp,
    show_webapp,
    update_app_settings,
    get_app_settings,
    _get_site_credential,
    _get_scm_url,
    get_sku_name,
    list_publish_profiles,
    get_site_configs)
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
from ._constants import (NODE_RUNTIME_NAME, OS_DEFAULT, STATIC_RUNTIME_NAME, PYTHON_RUNTIME_NAME)
logger = get_logger(__name__)

# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements,too-many-branches,line-too-long


def create_deploy_webapp(cmd, name, location=None, sku=None, dryrun=False):
    import os
    client = web_client_factory(cmd.cli_ctx)
    # the code to deploy is expected to be the current directory the command is running from
    src_dir = os.getcwd()
    # if dir is empty, show a message in dry run
    do_deployment = False if os.listdir(src_dir) == [] else True
    create_new_rg = True
    create_new_asp = True
    set_build_appSetting = False

    # determine the details for app to be created from src contents
    lang_details = get_lang_from_content(src_dir)
    # we support E2E create and deploy for Node & dotnetcore, any other stack, set defaults for os & runtime
    # and skip deployment
    if lang_details['language'] is None:
        do_deployment = False
        sku = sku | 'F1'
        os_val = OS_DEFAULT
        detected_version = '-'
        runtime_version = '-'
    else:
        # update SKU to user set value
        if sku is None:
            sku = lang_details.get("default_sku")
        else:
            sku = sku
        language = lang_details.get("language")
        is_skip_build = language.lower() == STATIC_RUNTIME_NAME or language.lower() == PYTHON_RUNTIME_NAME
        os_val = "Linux" if language.lower() == NODE_RUNTIME_NAME \
            or language.lower() == PYTHON_RUNTIME_NAME else OS_DEFAULT
        # detect the version
        data = get_runtime_version_details(lang_details.get('file_loc'), language)
        version_used_create = data.get('to_create')
        detected_version = data.get('detected')
        runtime_version = "{}|{}".format(language, version_used_create) if \
            version_used_create != "-" else version_used_create

    full_sku = get_sku_name(sku)

    if location is None:
        locs = client.list_geo_regions(sku, True)
        available_locs = []
        for loc in locs:
            available_locs.append(loc.name)
        location = available_locs[0]
    else:
        location = location
    # Remove spaces from the location string, incase the GeoRegion string is used
    loc_name = location.replace(" ", "").lower()

    is_linux = True if os_val == 'Linux' else False

    asp = "appsvc_asp_{}_{}".format(os_val, loc_name)
    rg_name = "appsvc_rg_{}_{}".format(os_val, loc_name)

    str_no_contents_warn = ""
    if not do_deployment:
        str_no_contents_warn = "[Empty directory, no deployment will be triggered]"

    # Resource group: check if default RG is set
    default_rg = cmd.cli_ctx.config.get('defaults', 'group', fallback=None)

    if default_rg and check_resource_group_exists(cmd, default_rg) and check_resource_group_supports_os(cmd, default_rg, is_linux):
        create_new_rg = False
    elif check_resource_group_exists(cmd, rg_name) and check_resource_group_supports_os(cmd, rg_name, is_linux):
        create_new_rg = False
    else:
        create_new_rg = True

    src_path = "{} {}".format(src_dir.replace("\\", "\\\\"), str_no_contents_warn)
    rg_str = "{}".format(rg_name)
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
    if create_new_rg:
        logger.warning("Creating Resource group '%s' ...", rg_name)
        create_resource_group(cmd, rg_name, location)
        logger.warning("Resource group creation complete")
    else:
        logger.warning("Resource group '%s' already exists.", rg_name)

    # create asp ], if are creating a new RG we can skip the checks for if asp exists
    if create_new_rg:
        logger.warning("Creating App service plan '%s' ...", asp)
        sku_def = SkuDescription(tier=full_sku, name=sku, capacity=(1 if is_linux else None))
        plan_def = AppServicePlan(location=loc_name, app_service_plan_name=asp,
                                  sku=sku_def, reserved=(is_linux or None))
        client.app_service_plans.create_or_update(rg_name, asp, plan_def)
        logger.warning("App service plan creation complete")
        create_new_asp = True

    elif not check_if_asp_exists(cmd, rg_name, asp, location):
        logger.warning("Creating App service plan '%s' ...", asp)
        sku_def = SkuDescription(tier=full_sku, name=sku, capacity=(1 if is_linux else None))
        plan_def = AppServicePlan(location=loc_name, app_service_plan_name=asp,
                                  sku=sku_def, reserved=(is_linux or None))
        client.app_service_plans.create_or_update(rg_name, asp, plan_def)
        create_new_asp = True
        logger.warning("App service plan creation complete")
    else:
        logger.warning("App service plan '%s' already exists.", asp)
        create_new_asp = False

    # create the app, skip checks for if app exists if a New RG or New ASP is created
    if create_new_rg or create_new_asp:
        logger.warning("Creating app '%s' ....", name)
        create_webapp(cmd, rg_name, name, asp, runtime_version if is_linux else None)
        logger.warning("Webapp creation complete")
        set_build_appSetting = True
    elif not check_app_exists(cmd, rg_name, name):
        logger.warning("Creating app '%s' ....", name)
        create_webapp(cmd, rg_name, name, asp, runtime_version if is_linux else None)
        logger.warning("Webapp creation complete")
        set_build_appSetting = True
    else:
        logger.warning("App '%s' already exists", name)
        if do_deployment:
            # setting the appsettings causes a app restart so we avoid if not needed
            set_build_appSetting = False
            _app_settings = get_app_settings(cmd, rg_name, name)
            if all(not d for d in _app_settings):
                set_build_appSetting = True
            elif '"name": "SCM_DO_BUILD_DURING_DEPLOYMENT", "value": "true"' not in json.dumps(_app_settings[0]):
                set_build_appSetting = True
            else:
                set_build_appSetting = False

    # update create_json to include the app_url
    url = _get_app_url(cmd, rg_name, name)  # picks the custom domain URL incase a domain is assigned

    if do_deployment:
        if not is_skip_build and set_build_appSetting:
            # setting to build after deployment
            logger.warning("Updating app settings to enable build after deployment")
            update_app_settings(cmd, rg_name, name, ["SCM_DO_BUILD_DURING_DEPLOYMENT=true"])
            # work around until the timeout limits issue for linux is investigated & fixed
            # wakeup kudu, by making an SCM call
        # TODO: replace this with a call to check if AppSettings, was set before calling zip deployment
        import time
        time.sleep(5)
        _ping_scm_site(cmd, rg_name, name)

        logger.warning("Creating zip with contents of dir %s ...", src_dir)
        # zip contents & deploy
        zip_file_path = zip_contents_from_dir(src_dir, language)

        logger.warning("Preparing to deploy %s contents to app.",
                       '' if is_skip_build else 'and build')
        enable_zip_deploy(cmd, rg_name, name, zip_file_path)
        # Remove the file afer deployment, handling exception if user removed the file manually
        try:
            os.remove(zip_file_path)
        except OSError:
            pass
    else:
        logger.warning('No known package (Node, ASP.NET, .NETCORE, or Static Html) '
                       'found skipping zip and deploy process')
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


def _get_app_url(cmd, rg_name, app_name):
    site = _generic_site_operation(cmd.cli_ctx, rg_name, app_name, 'get')
    return "https://" + site.enabled_host_names[0]


def _check_for_ready_tunnel(remote_debugging, tunnel_server):
    default_port = tunnel_server.is_port_set_to_default()
    if default_port is not remote_debugging:
        return True
    return False


def create_tunnel(cmd, resource_group_name, name, port=None, slot=None):
    logger.warning("remote-connection is deprecated and moving to cli-core, use `webapp create-remote-connection`")

    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        logger.error("Only Linux App Service Plans supported, Found a Windows App Service Plan")
        return
    import time
    profiles = list_publish_profiles(cmd, resource_group_name, name, slot)
    user_name = next(p['userName'] for p in profiles)
    user_password = next(p['userPWD'] for p in profiles)
    import threading
    from .tunnel import TunnelServer

    if port is None:
        port = 0  # Will auto-select a free port from 1024-65535
        logger.info('No port defined, creating on random free port')
    host_name = name
    if slot is not None:
        host_name += "-" + slot
    tunnel_server = TunnelServer('', port, host_name, user_name, user_password)
    config = get_site_configs(cmd, resource_group_name, name, slot)
    _ping_scm_site(cmd, resource_group_name, name)

    t = threading.Thread(target=_start_tunnel, args=(tunnel_server, config.remote_debugging_enabled))
    t.daemon = True
    t.start()

    # Wait indefinitely for CTRL-C
    while True:
        time.sleep(5)


def _start_tunnel(tunnel_server, remote_debugging_enabled):
    import time
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


# zip deployment copies from core with some error handling enabled, once we get the fix in core we will remove this
def enable_zip_deploy(cmd, resource_group_name, name, src, slot=None):
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    zip_url = scm_url + '/api/zipdeploy?isAsync=true'
    deployment_status_url = scm_url + '/api/deployments/latest'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    import requests
    import os
    # Read file content
    with open(os.path.realpath(os.path.expanduser(src)), 'rb') as fs:
        zip_content = fs.read()
        requests.post(zip_url, data=zip_content, headers=headers)
    # check the status of async deployment
    try:
        from json.decoder import JSONDecodeError
    except ImportError:
        JSONDecodeError = ValueError

    response = requests.get(deployment_status_url, headers=authorization)
    try:
        response = response.json()
        if response.get('status', 0) != 4:
            logger.warning(response.get('progress', ''))
            response = _check_zip_deployment_status(deployment_status_url, authorization)
        return response
    except JSONDecodeError:
        logger.warning("""Unable to fetch status of deployment. Please check status manually using link '%s'
            """, deployment_status_url)


def _check_zip_deployment_status(deployment_status_url, authorization):
    import requests
    import time
    num_trials = 1
    while num_trials < 10:
        time.sleep(15)
        response = requests.get(deployment_status_url, headers=authorization)
        res_dict = response.json()
        num_trials = num_trials + 1
        if res_dict.get('status', 0) == 5:
            logger.warning("Zip deployment failed status %s", res_dict['status_text'])
            break
        elif res_dict.get('status', 0) == 4:
            break
        if 'progress' in res_dict:
            logger.info(res_dict['progress'])  # show only in debug mode, customers seem to find this confusing
    # if the deployment is taking longer than expected
    if res_dict.get('status', 0) != 4:
        logger.warning("""Deployment is taking longer than expected. Please verify status at '%s'
            beforing launching the app""", deployment_status_url)
    return res_dict
