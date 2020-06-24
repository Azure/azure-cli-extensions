# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from base64 import b64encode
from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.util import CLIError
from nacl import encoding, public
import requests
from azure.mgmt.web.models import (AppServicePlan, SkuDescription, SiteSourceControl)
from azure.cli.command_modules.appservice.custom import (
    show_webapp,
    _get_site_credential,
    _get_scm_url,
    list_publish_profiles,
    get_site_configs,
    update_container_settings,
    create_webapp,
    get_sku_name,
    _check_zip_deployment_status,
    get_app_settings)
from azure.cli.command_modules.appservice._appservice_utils import _generic_site_operation
from azure.cli.command_modules.appservice._create_util import (
    should_create_new_rg,
    create_resource_group,
    web_client_factory,
    should_create_new_app,
    get_app_details,
    get_site_availability
)
from azure.cli.command_modules.appservice._github_oauth import (get_github_access_token)
from azure.cli.core.commands import LongRunningOperation
from ._constants import (
    LINUX_GITHUB_ACTIONS_SUPPORTED_STACKS,
    WINDOWS_GITHUB_ACTIONS_SUPPORTED_STACKS,
    LINUX_RUNTIME_STACK_INFO,
    WINDOWS_RUNTIME_STACK_INFO,
    LINUX_GITHUB_ACTIONS_WORKFLOW_TEMPLATE_PATH,
    WINDOWS_GITHUB_ACTIONS_WORKFLOW_TEMPLATE_PATH
)
from .acr_util import (queue_acr_build, generate_img_name)
from msrestazure.tools import parse_resource_id
logger = get_logger(__name__)


# pylint:disable=no-member,too-many-lines,too-many-locals,too-many-statements,too-many-branches,line-too-long,import-outside-toplevel
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
                      target_path=None,
                      artifact_type=None,
                      is_async=None,
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
    params.target_path = target_path
    params.artifact_type = artifact_type
    params.is_async_deployment = is_async
    params.should_restart = restart
    params.is_clean_deployment = clean
    params.should_ignore_stack = ignore_stack
    params.timeout = timeout
    params.slot = slot

    return _perform_onedeploy_internal(params)


# Class for OneDeploy parameters
# pylint: disable=too-many-instance-attributes,too-few-public-methods
class OneDeployParams(object):
    def __init__(self):
        self.cmd = None
        self.resource_group_name = None
        self.webapp_name = None
        self.src_path = None
        self.src_url = None
        self.artifact_type = None
        self.is_async_deployment = None
        self.target_path = None
        self.should_restart = None
        self.is_clean_deployment = None
        self.should_ignore_stack = None
        self.timeout = None
        self.slot = None
# pylint: enable=too-many-instance-attributes,too-few-public-methods


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
        get_az_user_agent,
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
        logger.info('Deploying from local path: %s', params.src_path)
        try:
            with open(os.path.realpath(os.path.expanduser(params.src_path)), 'rb') as fs:
                body = fs.read()
        except Exception as e:
            raise CLIError("Either '{}' is not a valid local file path or you do not have permissions to access it".format(params.src_path)) from e
    elif params.src_url:
        logger.info('Deploying from URL: %s', params.src_url)
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
    logger.warning("Deployment type: %s. To override deloyment type, please specify the --type parameter. "
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

    logger.info("Deployment API: %s", deploy_url)
    response = requests.post(deploy_url, data=body, headers=headers, verify=not should_disable_connection_verify())

    # For debugging purposes only, you can change the async deployment into a sync deployment by polling the API status
    # For that, set poll_async_deployment_for_debugging=True
    poll_async_deployment_for_debugging = False

    # check the status of async deployment
    if response.status_code == 202:
        if poll_async_deployment_for_debugging:
            logger.info('Polloing the status of async deployment')
            response_body = _check_zip_deployment_status(params.cmd, params.resource_group_name, params.webapp_name, deployment_status_url, headers, params.timeout)
            logger.info('Async deployment complete. Server response: %s', response_body)
        return

    if response.status_code == 200:
        return

    # API not available yet!
    if response.status_code == 404:
        raise CLIError("This API isn't available in this environment yet!")

    # check if there's an ongoing process
    if response.status_code == 409:
        raise CLIError("Another deployment is in progress. You can track the ongoing deployment at {}".format(deployment_status_url))

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


def add_github_actions(cmd, resource_group, name, repo, runtime=None, token=None, slot=None, branch='master', force=False):
    if not token:
        token = get_github_access_token(cmd, ["admin:repo_hook", "repo", "workflow"])

    # Verify resource group, app
    site_availability = get_site_availability(cmd, name)
    if site_availability.name_available or (not site_availability.name_available and site_availability.reason == 'Invalid'):
        raise CLIError("The Resource 'Microsoft.Web/sites/{}' under resource group '{}' was not found.".format(name, resource_group))
    app_details = get_app_details(cmd, name)
    if app_details is None:
        raise CLIError("Unable to retrieve details of the existing app {}. Please check that the app is a part of the current subscription".format(name))
    current_rg = app_details.resource_group
    if resource_group is not None and (resource_group.lower() != current_rg.lower()):
        raise CLIError("The webapp {} exists in ResourceGroup {} and does not match the value entered {}. Please "
                        "re-run command with the correct parameters.".format(name, current_rg, resource_group))
    parsed_plan_id = parse_resource_id(app_details.server_farm_id)
    client = web_client_factory(cmd.cli_ctx)
    plan_info = client.app_service_plans.get(parsed_plan_id['resource_group'], parsed_plan_id['name'])
    is_linux = plan_info.reserved

    # Verify github repo
    from github import Github, GithubException
    from github.GithubException import BadCredentialsException, UnknownObjectException
    import yaml

    if repo.strip()[-1] == '/':
        repo = repo.strip()[:-1]

    g = Github(token)
    github_repo = None
    github_branch = None
    try:
        github_repo = g.get_repo(repo)
        try:
            github_branch = github_repo.get_branch(branch=branch)
        except GithubException as e:
            error_msg = "Encountered GitHub error when accessing {} branch in {} repo.".format(branch, repo)
            if e.data and e.data['message']:
                error_msg += " Error: {}".format(e.data['message'])
            raise CLIError(error_msg)
        logger.warning('Verified GitHub repo and branch')
    except BadCredentialsException as e:
        raise CLIError("Could not authenticate to the repository. Please create a Personal Access Token and use the --token argument. Run 'az webapp deployment github-actions add --help' for more information.")
    except GithubException as e:
        error_msg = "Encountered GitHub error when accessing {} repo".format(repo)
        if e.data and e.data['message']:
            error_msg += " Error: {}".format(e.data['message'])
        raise CLIError(error_msg)

    # Verify runtime
    app_runtime_info = _get_app_runtime_info(cmd=cmd, resource_group=resource_group, name=name, slot=slot, is_linux=is_linux)
    app_runtime_string = app_runtime_info['display_name'] if (app_runtime_info and app_runtime_info['display_name']) else None
    github_actions_version = app_runtime_info['github_actions_version'] if (app_runtime_info and app_runtime_info['github_actions_version']) else None

    if runtime and app_runtime_string:
        if app_runtime_string.lower() != runtime.lower():
            logger.warning('The app runtime: {} does not match the runtime specified: {}. Using the specified runtime {}.'.format(app_runtime_string, runtime, runtime))
            app_runtime_string = runtime
    elif runtime:
        app_runtime_string = runtime

    if not app_runtime_string:
        raise CLIError('Could not detect runtime. Please specify using the --runtime flag.')

    if not _runtime_supports_github_actions(runtime_string=app_runtime_string, is_linux=is_linux):
        raise CLIError("Runtime {} is not supported for GitHub Actions deployments.".format(app_runtime_string))

    # Get workflow template
    logger.warning('Getting workflow template using runtime: {}'.format(app_runtime_string))
    workflow_template = _get_workflow_template(github=g, runtime_string=app_runtime_string, is_linux=is_linux)

    # Fill workflow template
    import uuid
    guid = str(uuid.uuid4()).replace('-', '')
    publish_profile_name = "AzureAppService_PublishProfile_{}".format(guid)
    logger.warning('Fill workflow template with name: {}, branch: {}, version: {}, slot: {}'.format(name, branch, github_actions_version, slot if slot else 'production'))
    completed_workflow_file = _fill_workflow_template(content=workflow_template.decoded_content.decode(), name=name,
                                                      branch=branch, slot=slot, publish_profile=publish_profile_name, version=github_actions_version)
    completed_workflow_file = completed_workflow_file.encode()

    # Check if workflow exists in repo, otherwise push
    file_name = "{}_{}({}).yml".format(branch.replace('/', '-'), name.lower(), slot) if slot else "{}_{}.yml".format(branch.replace('/', '-'), name.lower())
    dir_path = "{}/{}".format('.github', 'workflows')
    file_path = "{}/{}".format(dir_path, file_name)
    try:
        existing_workflow_file = github_repo.get_contents(path=file_path, ref=branch)
        existing_publish_profile_name = _get_publish_profile_from_workflow_file(workflow_file=str(existing_workflow_file.decoded_content))
        if existing_publish_profile_name:
            completed_workflow_file = completed_workflow_file.decode()
            completed_workflow_file = completed_workflow_file.replace(publish_profile_name, existing_publish_profile_name)
            completed_workflow_file = completed_workflow_file.encode()
            publish_profile_name = existing_publish_profile_name
        logger.warning("Existing workflow file found")
        if force:
            logger.warning("Replacing the existing workflow file")
            github_repo.update_file(path=file_path, message="Update workflow using Azure CLI",
                                    content=completed_workflow_file, sha=existing_workflow_file.sha, branch=branch)
        else:
            option = prompt_y_n('Replace existing workflow file?')
            if option:
                logger.warning("Replacing the existing workflow file")
                github_repo.update_file(path=file_path, message="Update workflow using Azure CLI",
                                        content=completed_workflow_file, sha=existing_workflow_file.sha, branch=branch)
            else:
                logger.warning("Use the existing workflow file")
                if existing_publish_profile_name:
                    publish_profile_name = existing_publish_profile_name
    except UnknownObjectException as e:
        logger.warning("Creating new workflow file: {}".format(file_path))
        github_repo.create_file(path=file_path, message="Create workflow using Azure CLI",
                                content=completed_workflow_file, branch=branch)

    # Add publish profile to GitHub
    logger.warning('Add publish profile to GitHub')
    _add_publish_profile_to_github(cmd=cmd, resource_group=resource_group, name=name, repo=repo, token=token,
                                   github_actions_secret_name=publish_profile_name, slot=slot)

    # Set site source control properties
    logger.warning('Set site source control properties')
    _set_site_source_control_properties(cmd=cmd, resource_group=resource_group, name=name, repo=repo, slot=slot)

    github_actions_url = "https://github.com/{}/actions".format(repo)
    return github_actions_url


def _get_publish_profile_from_workflow_file(workflow_file):
    import re
    publish_profile = None
    regex = re.search(r'publish-profile: \$\{\{ secrets\..*?\}\}', workflow_file)
    if regex:
        publish_profile = regex.group()
        publish_profile = publish_profile.replace('publish-profile: ${{ secrets.', '')
        publish_profile = publish_profile[:-2]

    if publish_profile:
        return publish_profile.strip()
    return None


def _set_site_source_control_properties(cmd, resource_group, name, repo, slot):
    repo_url = 'https://github.com/' + repo
    site_source_control = _generic_site_operation(cmd.cli_ctx, resource_group, name, 'get_source_control', slot)
    if not site_source_control:
        site_source_control = SiteSourceControl(repo_url=repo_url)
    else:
        site_source_control.repo_url = repo_url
    # TODO: Set is_github_action when new SDK is in
    # TODO: Test create or update. If changing to new github repo works, then we can remove delete_source_control
    _generic_site_operation(cmd.cli_ctx, resource_group, name, 'delete_source_control', slot=slot)
    _generic_site_operation(cmd.cli_ctx, resource_group, name, 'create_or_update_source_control',
                            slot=slot, extra_parameter=site_source_control)


def _get_workflow_template(github, runtime_string, is_linux):
    from github import GithubException
    from github.GithubException import BadCredentialsException

    file_contents = None
    template_repo_path = 'Azure/actions-workflow-templates'
    template_file_path = _get_template_file_path(runtime_string=runtime_string, is_linux=is_linux)

    try:
        template_repo = github.get_repo(template_repo_path)
        file_contents = template_repo.get_contents(template_file_path)
    except BadCredentialsException as e:
        raise CLIError("Could not authenticate to the repository. Please create a Personal Access Token and use the --token argument. Run 'az webapp deployment github-actions add --help' for more information.")
    except GithubException as e:
        error_msg = "Encountered GitHub error when retrieving workflow template"
        if e.data and e.data['message']:
            error_msg += ": {}".format(e.data['message'])
        raise CLIError(error_msg)
    return file_contents


def _fill_workflow_template(content, name, branch, slot, publish_profile, version):
    if not slot:
        slot = 'production'

    content = content.replace('${web-app-name}', name)
    content = content.replace('${branch}', branch)
    content = content.replace('${slot-name}', slot)
    content = content.replace('${azure-webapp-publish-profile-name}', publish_profile)
    content = content.replace('${AZURE_WEBAPP_PUBLISH_PROFILE}', publish_profile)
    content = content.replace('${dotnet-core-version}', version)
    content = content.replace('${java-version}', version)
    content = content.replace('${node-version}', version)
    content = content.replace('${python-version}', version)
    return content


def _get_template_file_path(runtime_string, is_linux):
    if not runtime_string:
        raise CLIError('Unable to retrieve workflow template')

    runtime_string = runtime_string.lower()
    runtime_stack = runtime_string.split('|')[0]
    template_file_path = None

    if is_linux:
        template_file_path = LINUX_GITHUB_ACTIONS_WORKFLOW_TEMPLATE_PATH.get(runtime_stack, None)
    else:
        # Handle java naming
        if runtime_stack == 'java':
            java_container_split = runtime_string.split('|')
            if java_container_split and len(java_container_split) >= 2:
                if java_container_split[2] == 'tomcat':
                    runtime_stack = 'tomcat'
                elif java_container_split[2] == 'java se':
                    runtime_stack = 'java'
        template_file_path = WINDOWS_GITHUB_ACTIONS_WORKFLOW_TEMPLATE_PATH.get(runtime_stack, None)

    if not template_file_path:
        raise CLIError('Unable to retrieve workflow template.')
    return template_file_path


def _add_publish_profile_to_github(cmd, resource_group, name, repo, token, github_actions_secret_name, slot=None):
    # Get publish profile with secrets
    logger.warning("Fetching publish profile with secrets for the app '%s'", name)
    publish_profile_bytes= _generic_site_operation(cmd.cli_ctx, resource_group, name, 'list_publishing_profile_xml_with_secrets', slot)
    publish_profile = [x for x in publish_profile_bytes]
    if publish_profile:
        publish_profile = publish_profile[0].decode('ascii')
    else:
        raise CLIError('Unable to retrieve publish profile.')

    # Add publish profile with secrets as a GitHub Actions Secret in the repo
    headers = {}
    headers['Authorization'] = 'Token {}'.format(token)
    headers['Content-Type'] = 'application/json;'
    headers['Accept'] = 'application/json;'

    public_key_url = "https://api.github.com/repos/{}/actions/secrets/public-key".format(repo)
    public_key = requests.get(public_key_url, headers=headers)
    if not public_key.ok:
        raise CLIError('Request to GitHub for public key failed.')
    public_key = public_key.json()

    encrypted_github_actions_secret = _encrypt_github_actions_secret(public_key=public_key['key'], secret_value=str(publish_profile))
    payload = {
        "encrypted_value": encrypted_github_actions_secret,
        "key_id": public_key['key_id']
    }

    import json
    store_secret_url = "https://api.github.com/repos/{}/actions/secrets/{}".format(repo, github_actions_secret_name)
    stored_secret = requests.put(store_secret_url, data=json.dumps(payload), headers=headers)
    if str(stored_secret.status_code)[0] != '2':
        raise CLIError('Unable to add publish profile to GitHub. Request status code: {}'.format(stored_secret.status_code))


def _runtime_supports_github_actions(runtime_string, is_linux):
    if is_linux:
        return runtime_string.lower() in [x.lower() for x in LINUX_GITHUB_ACTIONS_SUPPORTED_STACKS]
    else:
        return runtime_string.lower() in [x.lower() for x in WINDOWS_GITHUB_ACTIONS_SUPPORTED_STACKS]


def _get_app_runtime_info(cmd, resource_group, name, slot, is_linux):
    app_settings = None
    app_runtime = None
    app_runtime_info = None

    if is_linux:
        app_metadata = get_site_configs(cmd=cmd, resource_group_name=resource_group, name=name, slot=slot)
        app_runtime = getattr(app_metadata, 'linux_fx_version', None)
        if app_runtime and (app_runtime.lower() in LINUX_RUNTIME_STACK_INFO):
            app_runtime_info = LINUX_RUNTIME_STACK_INFO[app_runtime.lower()]
    else:
        app_metadata = _generic_site_operation(cmd.cli_ctx, resource_group, name, 'list_metadata', slot)
        app_metadata_properties = getattr(app_metadata, 'properties', {})
        if 'CURRENT_STACK' in app_metadata_properties:
            app_runtime = app_metadata_properties['CURRENT_STACK']

        if app_runtime and app_runtime.lower() == 'node':
            app_settings = get_app_settings(cmd=cmd, resource_group_name=resource_group, name=name, slot=slot)
            for app_setting in app_settings:
                if 'name' in app_setting and app_setting['name'] == 'WEBSITE_NODE_DEFAULT_VERSION':
                    app_runtime_version = app_setting['value'] if 'value' in app_setting else None
                    if app_runtime_version:
                        app_runtime_info = WINDOWS_RUNTIME_STACK_INFO['node'].get(app_runtime_version.lower(), None)
        elif app_runtime and app_runtime.lower() == 'python':
            app_settings = get_site_configs(cmd=cmd, resource_group_name=resource_group, name=name, slot=slot)
            app_runtime_version = getattr(app_settings, 'python_version', '')
            app_runtime_info = WINDOWS_RUNTIME_STACK_INFO['python'].get(app_runtime_version.lower(), None)
        elif app_runtime and app_runtime.lower() == 'dotnetcore':
            app_runtime_version = '3.1'
            app_runtime_info = WINDOWS_RUNTIME_STACK_INFO['dotnetcore'].get(app_runtime_version.lower(), None)
        elif app_runtime and app_runtime.lower() == 'java':
            app_settings = get_site_configs(cmd=cmd, resource_group_name=resource_group, name=name, slot=slot)
            java_version = getattr(app_settings, 'java_version', '').lower()
            java_container = getattr(app_settings, 'java_container', '').lower()
            java_container_version = getattr(app_settings, 'java_container_version', '').lower()
            app_runtime_info = WINDOWS_RUNTIME_STACK_INFO['java'].get((java_version, java_container, java_container_version), None)
    return app_runtime_info


def _encrypt_github_actions_secret(public_key, secret_value):
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")
