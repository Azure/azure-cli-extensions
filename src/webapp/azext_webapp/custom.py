# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from knack.log import get_logger
from knack.util import CLIError
from azure.mgmt.web.models import (AppServicePlan, SkuDescription)
from azure.cli.command_modules.appservice.custom import (
    show_webapp,
    _get_site_credential,
    _get_scm_url,
    list_publish_profiles,
    get_site_configs,
    update_container_settings,
    create_webapp,
    get_sku_name,
    _check_zip_deployment_status)
from azure.cli.command_modules.appservice._appservice_utils import _generic_site_operation
from azure.cli.command_modules.appservice._create_util import (
    should_create_new_rg,
    create_resource_group,
    web_client_factory,
    should_create_new_app
)
from .acr_util import (queue_acr_build, generate_img_name)
logger = get_logger(__name__)


# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements,too-many-branches,line-too-long
def create_deploy_container_app(cmd, name, source_location=None, docker_custom_image_name=None, dryrun=False, registry_rg=None, registry_name=None):  # pylint: disable=too-many-statements
    import os
    import json
    if not source_location:
        # the dockerfile is expected to be in the current directory the command is running from
        source_location = os.getcwd()

    client = web_client_factory(cmd.cli_ctx)
    _create_new_rg = True
    _create_new_asp = True
    _create_new_app = True
    _create_acr_img = True

    if docker_custom_image_name:
        logger.warning('Image will be pulled from DockerHub')
        img_name = docker_custom_image_name
        _create_acr_img = False
    else:
        logger.warning('Source code will be uploaded and built in Azure Container Registry')
        if not registry_name:
            raise CLIError("--registry-name not specified")
        if not registry_rg:
            raise CLIError("--registry-rg not specified")
        img_name = generate_img_name(source_location)

    sku = 'P1V2'
    full_sku = get_sku_name(sku)
    location = 'Central US'
    loc_name = 'centralus'
    asp = "appsvc_asp_linux_{}".format(loc_name)
    rg_name = "appsvc_rg_linux_{}".format(loc_name)
    # Resource group: check if default RG is set
    _create_new_rg = should_create_new_rg(cmd, rg_name, True)

    rg_str = "{}".format(rg_name)

    dry_run_str = r""" {
            "name" : "%s",
            "serverfarm" : "%s",
            "resourcegroup" : "%s",
            "sku": "%s",
            "location" : "%s"
            }
            """ % (name, asp, rg_str, full_sku, location)
    create_json = json.loads(dry_run_str)

    if dryrun:
        logger.warning("Web app will be created with the below configuration,re-run command "
                       "without the --dryrun flag to create & deploy a new app")
        return create_json

    if _create_acr_img:
        logger.warning("Starting ACR build")
        queue_acr_build(cmd, registry_rg, registry_name, img_name, source_location)
        logger.warning("ACR build done. Deploying web app.")

    # create RG if the RG doesn't already exist
    if _create_new_rg:
        logger.warning("Creating Resource group '%s' ...", rg_name)
        create_resource_group(cmd, rg_name, location)
        logger.warning("Resource group creation complete")
        _create_new_asp = True
    else:
        logger.warning("Resource group '%s' already exists.", rg_name)
        _create_new_asp = _should_create_new_asp(cmd, rg_name, asp, location)
    # create new ASP if an existing one cannot be used
    if _create_new_asp:
        logger.warning("Creating App service plan '%s' ...", asp)
        sku_def = SkuDescription(tier=full_sku, name=sku, capacity=1)
        plan_def = AppServicePlan(location=loc_name, app_service_plan_name=asp,
                                  sku=sku_def, reserved=True)
        client.app_service_plans.create_or_update(rg_name, asp, plan_def)
        logger.warning("App service plan creation complete")
        _create_new_app = True
    else:
        logger.warning("App service plan '%s' already exists.", asp)
        _create_new_app = should_create_new_app(cmd, rg_name, name)

    # create the app
    if _create_new_app:
        logger.warning("Creating app '%s' ....", name)
        # TODO: Deploy without container params and update separately instead?
        # deployment_container_image_name=docker_custom_image_name)
        create_webapp(cmd, rg_name, name, asp, deployment_container_image_name=img_name)
        logger.warning("Webapp creation complete")
    else:
        logger.warning("App '%s' already exists", name)

    # Set up the container
    if _create_acr_img:
        logger.warning("Configuring ACR container settings.")
        registry_url = 'https://' + registry_name + '.azurecr.io'
        acr_img_name = registry_name + '.azurecr.io/' + img_name
        update_container_settings(cmd, rg_name, name, registry_url, acr_img_name)

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


def start_scan(cmd, resource_group_name, name, timeout="", slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    start_scan_url = scm_url + '/api/scan/start?timeout=' + timeout

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(start_scan_url, headers=authorization)
    return response.json()


def get_scan_result(cmd, resource_group_name, name, scan_id, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    scan_result_url = scm_url + '/api/scan/' + scan_id + '/result'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(scan_result_url, headers=authorization)

    return response.json()


def track_scan(cmd, resource_group_name, name, scan_id, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    scan_result_url = scm_url + '/api/scan/' + scan_id + '/track'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(scan_result_url, headers=authorization)

    return response.json()


def get_all_scan_result(cmd, resource_group_name, name, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    scan_result_url = scm_url + '/api/scan/results'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    response = requests.get(scan_result_url, headers=authorization)

    return response.json()


def stop_scan(cmd, resource_group_name, name, slot=None):
    webapp = show_webapp(cmd, resource_group_name, name, slot)
    is_linux = webapp.reserved
    if not is_linux:
        raise CLIError("Only Linux App Service Plans supported, Found a Windows App Service Plan")

    import requests
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    stop_scan_url = scm_url + '/api/scan/stop'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['content-type'] = 'application/octet-stream'

    requests.delete(stop_scan_url, headers=authorization)


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


def _should_create_new_asp(cmd, rg_name, asp_name, location):
    # get all appservice plans from RG
    client = web_client_factory(cmd.cli_ctx)
    for item in list(client.app_service_plans.list_by_resource_group(rg_name)):
        if (item.name.lower() == asp_name.lower() and
                item.location.replace(" ", "").lower() == location or
                item.location == location):
            return False
    return True


# OneDeploy
def perform_onedeploy(cmd,
                      resource_group_name,
                      name,
                      src_path=None,
                      src_url=None,
                      type=None,
                      async=None,
                      target_path=None,
                      restart=None,
                      clean=None,
                      ignore_stack=None,
                      timeout=None,
                      slot=None):
    params = OneDeployParams()

    params.cmd = cmd
    params.resource_group_name = resource_group_name
    params.webapp_name = name
    params.src_path = src_path
    params.src_url = src_url
    params.artifact_type = type
    params.is_async_deployment = async
    params.target_path = target_path
    params.should_restart = restart
    params.is_clean_deployment = clean
    params.should_ignore_stack = ignore_stack
    params.timeout = timeout
    params.slot = slot

    return _perform_onedeploy_internal(params)


# Class for OneDeploy parameters
class OneDeployParams(object):
    pass


def _validate_onedeploy_params(params):
    if params.src_path and params.src_url:
        raise CLIError('Only one of --src-path and --src-url can be specified')

    if not params.src_path and not params.src_url:
        raise CLIError('Either of --src-path or --src-url must be specified')

    if params.src_url and not params.artifact_type:
        raise CLIError('Deployment type is mandatory when deploying from URLs. Use --type')


def _build_onedeploy_url(params):
    scm_url = _get_scm_url(params.cmd, params.resource_group_name, params.webapp_name, params.slot)
    deploy_url = scm_url + '/api/publish?type=' + params.artifact_type

    if params.is_async_deployment is not None:
        deploy_url = deploy_url + '&async=' + str(params.is_async_deployment)

    if params.should_restart is not None:
        deploy_url = deploy_url + '&restart=' + str(params.should_restart)

    if params.is_clean_deployment is not None:
        deploy_url = deploy_url + '&clean=' + str(params.is_clean_deployment)

    if params.should_ignore_stack is not None:
        deploy_url = deploy_url + '&ignorestack=' + str(params.should_ignore_stack)

    if params.target_path is not None:
        deploy_url = deploy_url + '&path=' + params.target_path

    return deploy_url


def _get_onedeploy_status_url(params):
    scm_url = _get_scm_url(params.cmd, params.resource_group_name, params.webapp_name, params.slot)
    return scm_url + '/api/deployments/latest'


def _get_basic_headers(params):
    import urllib3
    from azure.cli.core.util import (
        should_disable_connection_verify,
        get_az_user_agent
    )

    user_name, password = _get_site_credential(params.cmd.cli_ctx, params.resource_group_name, params.webapp_name, params.slot)

    if params.src_path:
        content_type = 'application/octet-stream'
    elif params.src_url:
        content_type = 'application/json'
    else:
        raise CLIError('Unable to determine source location of the artifact being deployed')

    headers = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers['Cache-Control'] = 'no-cache'
    headers['User-Agent'] = get_az_user_agent()
    headers['Content-Type'] = content_type

    return headers


def _get_onedeploy_request_body(params):
    import os
    import json

    if params.src_path:
        logger.info('Deploying from local path: ' + params.src_path)
        try:
            with open(os.path.realpath(os.path.expanduser(params.src_path)), 'rb') as fs:
                body = fs.read()
        except Exception as e:
            raise CLIError("Either '{}' is not a valid local file path or you do not have permissions to access it".format(params.src_path)) from e
    elif params.src_url:
        logger.info('Deploying from URL: ' + params.src_url)
        body = json.dumps({
            "packageUri": params.src_url
        })
    else:
        raise CLIError('Unable to determine source location of the artifact being deployed')

    return body


def _update_artifact_type(params):
    import ntpath

    if params.artifact_type is not None:
        return

    # Interpret deployment type from the file extension if the type parameter is not passed
    file_name = ntpath.basename(params.src_path)
    file_extension = file_name.split(".", 1)[1]
    if file_extension in ('war', 'jar', 'ear', 'zip'):
        params.artifact_type = file_extension
    elif file_extension in ('sh', 'bat'):
        params.artifact_type = 'startup'
    else:
        params.artifact_type = 'static'
    logger.warning("Deployment type: %s. To override deloyment type, please specify the --type parameter. " +
                   "Possible values: war, jar, ear, zip, startup, script, static", params.artifact_type)


def _make_onedeploy_request(params):
    import requests

    from azure.cli.core.util import (
        should_disable_connection_verify,
    )

    # Build the request body, headers, API URL and status URL
    body = _get_onedeploy_request_body(params)
    headers = _get_basic_headers(params)
    deploy_url = _build_onedeploy_url(params)
    deployment_status_url = _get_onedeploy_status_url(params)

    logger.info("Deployment API: " + deploy_url)
    response = requests.post(deploy_url, data=body, headers=headers, verify=not should_disable_connection_verify())

    # check the status of async deployment
    if response.status_code == 202:
        logger.info("Asynchronous deployment request completed")
        response_body = _check_zip_deployment_status(params.cmd, params.resource_group_name, params.webapp_name, deployment_status_url, headers, params.timeout)
        logger.info(response_body)
        return

    if response.status_code == 200:
        return

    # API not available yet!
    if response.status_code == 404:
        raise CLIError("This API isn't available in this environment yet!")

    # check if there's an ongoing process
    if response.status_code == 409:
        raise CLIError("There may be an ongoing deployment or your app setting has WEBSITE_RUN_FROM_PACKAGE. "
                       "Please track your deployment in {} and ensure the WEBSITE_RUN_FROM_PACKAGE app setting "
                       "is removed.".format(deployment_status_url))

    # check if an error occured during deployment
    if response.status_code:
        raise CLIError("An error occured during deployment. Status Code: {}, Details: {}".format(response.status_code, response.text))


# OneDeploy
def _perform_onedeploy_internal(params):

    # Do basic paramter validation
    _validate_onedeploy_params(params)

    # Update artifact type, if required
    _update_artifact_type(params)

    # Now make the OneDeploy API call
    logger.info("Initiating deployment")
    _make_onedeploy_request(params)

    return logger.info("Deployment has completed successfully")
