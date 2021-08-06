from time import sleep
from knack.util import CLIError
from knack.log import get_logger
from msrestazure.azure_exceptions import CloudError
from msrestazure.tools import parse_resource_id
from .vendored_sdks.appplatform.v2022_05_01_preview import models
from ._utils import  get_azure_files_info, _pack_source_code
from azure.cli.core.util import sdk_no_wait
from .azure_storage_file import FileService
import requests
import sys

logger = get_logger(__name__)
APPLICATION_CONFIGURATION_SERVICE_NAME = "ApplicationConfigurationService"
APPLICATION_CONFIGURATION_SERVICE_PROPERTY_PATTERN = "ConfigFilePatterns"

# pylint: disable=line-too-long
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment or create deployment with: az spring-cloud app deployment create"
NO_PRODUCTION_DEPLOYMENT_SET_ERROR = "This app has no production deployment, use \"az spring-cloud app deployment create\" to create a deployment and \"az spring-cloud app set-deployment\" to set production deployment."
DELETE_PRODUCTION_DEPLOYMENT_WARNING = "You are going to delete production deployment, the app will be inaccessible after this operation."
LOG_RUNNING_PROMPT = "This command usually takes minutes to run. Add '--verbose' parameter if needed."


def app_get_enterprise(cmd, client, resource_group, service, name):
    app = client.apps.get(resource_group, service, name)
    app.properties.activeDeployment = _get_active_deployment(client, resource_group, service, name)
    return app


def app_deploy_enterprise(cmd, client, resource_group, service, name,
                          version, deployment, artifact_path, target_module, jvm_options,
                          env, config_file_patterns, no_wait):
    '''app_deploy_enterprise
    Deploy artifact to deployment under the existing app.
    Update active deployment's pattern if --config-profile-patterns are provided.
    Throw exception if app or deployment not found.
    This method does:
    1. Call build service to get upload url
    2. Upload artifact to given Storage file url
    3. Send the url to build service
    4. Query build result from build service
    5. Send build result id to deployment
    '''
    logger.warning(LOG_RUNNING_PROMPT)
    if not deployment:
        deployment_resource = _get_active_deployment(client, resource_group, service, name)
        if not deployment_resource:
            raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
        deployment = deployment_resource.name
    
    deployment_settings = _format_deployment_settings(jvm_options=jvm_options, env=env, config_file_patterns=config_file_patterns)
    user_source_info = _build_and_get_result(cmd, client, resource_group, service, name, version, artifact_path, target_module, additional_steps=1)
    logger.warning("[5/5] Deploying the built docker image to deployment {} under app {}".format(deployment, name))
    resource = models.DeploymentResource(
        properties=models.DeploymentResourceProperties(
            deployment_settings=deployment_settings,
            source=user_source_info
        )
    )
    return sdk_no_wait(no_wait, client.deployments.begin_update, resource_group, service, name, deployment, resource)


def _build_and_get_result(cmd, client, resource_group, service, name, version, artifact_path, target_module, additional_steps=0):
    total_steps = 4 + additional_steps
    logger.warning("[1/{}] Requesting for upload URL.".format(total_steps))
    upload_url, relative_path = _request_upload_url(client,  resource_group, service, name)
    logger.warning("[2/{}] Uploading package to blob.".format(total_steps))
    _compress_and_upload(cmd, client, upload_url, artifact_path)
    logger.warning("[3/{}] Creating or Updating build '{}'.".format(total_steps, name))
    build_result_id = _queue_build(client, resource_group, service, name, relative_path, target_module)
    logger.warning("[4/{}] Waiting for building docker image to finish. This may take a few minutes.".format(total_steps))
    _wait_build_finished(cmd, client, build_result_id)
    return models.BuildResultUserSourceInfo(version=version, build_result_id=build_result_id)


def _wait_build_finished(cmd, client, build_result_id):
    resource_id = parse_resource_id(build_result_id)
    resource_group = resource_id['resource_group']
    service = resource_id['name']
    build_service = resource_id['child_name_1']
    build = resource_id['child_name_2']
    build_result_name = resource_id['resource_name']

    progress_bar = cmd.cli_ctx.get_progress_controller()
    result = client.build_service.get_build_result(resource_group, service, build_service, build, build_result_name)
    progress_bar.add(message=result.properties.status)
    progress_bar.begin()
    while result.properties.status == "Building" or result.properties.status == "Queuing":
        progress_bar.add(message=result.properties.status)
        sleep(5)
        result = client.build_service.get_build_result(resource_group, service, build_service, build, build_result_name)
    progress_bar.stop()
    if result.properties.status != "Succeeded":
        raise CLIError("Failed to build docker image, please check the build logs and retry.")


def _queue_build(client, resource_group, service, name, relative_path, target_module=None):
    properties = models.BuildProperties(
        builder="default-enterprise-builder",
        relative_path=relative_path,
        env={"BP_MAVEN_BUILT_MODULE": target_module} if target_module else None)
    build = models.Build(properties=properties)
    try:
        return client.build_service.create_or_update_build(resource_group,
                                                           service,
                                                           'default',
                                                           name,
                                                           build).properties.triggered_build_result.id
    except (AttributeError, CloudError) as e:
        raise CLIError("Failed to create or update a build. Error: {}".format(e.message))


def _compress_and_upload(cmd, client, upload_url, artifact_path):
    account_name, endpoint_suffix, share_name, relative_name, sas_token = get_azure_files_info(upload_url)
    progress_bar = cmd.cli_ctx.get_progress_controller()
    progress_bar.add(message='Uploading')
    progress_bar.begin()
    FileService(account_name,
                sas_token=sas_token,
                endpoint_suffix=endpoint_suffix).create_file_from_path(share_name,
                                                                       None,
                                                                       relative_name,
                                                                       artifact_path or _get_upload_local_file())
    progress_bar.stop()


def _request_upload_url(client,  resource_group, service, name):
    try:
        response = client.build_service.get_resource_upload_url(resource_group, service)
        if not response.upload_url:
            raise CLIError("Failed to get a SAS URL to upload context.")
        return response.upload_url, response.relative_path
    except CloudError as e:
        raise CLIError("Failed to get a SAS URL to upload context. Error: {}".format(e.message))
    except AttributeError as e:
        raise CLIError("Failed to get a SAS URL to upload context. Error: {}".format(e))


def _get_addon_configs(config_file_patterns):
    patterns = models.AddonProfile(
        properties = {
            APPLICATION_CONFIGURATION_SERVICE_PROPERTY_PATTERN: config_file_patterns
        }
    )
    addon_configs = {}
    addon_configs[APPLICATION_CONFIGURATION_SERVICE_NAME] = patterns
    return addon_configs


def _get_active_deployment(client, resource_group, service, name):
    deployments = client.deployments.list(resource_group, service, name)
    return next(x for x in deployments if x.properties.active)

def _format_deployment_settings(cpu=None, memory=None, jvm_options=None, env=None, config_file_patterns=None):
    if all(x is None for x in [cpu, memory, jvm_options, env, config_file_patterns]):
        return None
    resource_requests = models.ResourceRequests(cpu=cpu, memory=memory) if cpu or memory else None
    # TODO set jvm to env
    addon_configs = _get_addon_configs(config_file_patterns) if config_file_patterns is not None else None
    return models.DeploymentSettings(
        addon_configs=addon_configs,
        resource_requests=resource_requests,
        env=env
    )


def _get_upload_local_file():
    file_path = os.path.join(tempfile.gettempdir(), 'build_archive_{}.tar.gz'.format(uuid.uuid4().hex))
    _pack_source_code(os.getcwd(), file_path)
    return file_path