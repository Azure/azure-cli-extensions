# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import urllib.request
import tempfile
from time import sleep
from ._stream_utils import stream_logs
from msrestazure.azure_exceptions import CloudError
from msrestazure.tools import parse_resource_id
from ._utils import _get_upload_local_file, dump
from knack.util import CLIError
from .vendored_sdks.microservices4spring import models
from ._client_factory import cf_asc
from knack.log import get_logger
from urllib.request import urlretrieve
from urllib.parse import urlparse
from .azure_storage_file import FileService
from azure.cli.core.util import sdk_no_wait

logger = get_logger(__name__)
#DEFAULT_DEPLOYMENT_URL='https://github.com/peizhou298/Helloworld/releases/download/0.1/jb-hello-world-maven-0.1.0.jar'
#DEFAULT_DEPLOYMENT_FILE = os.path.join(tempfile.gettempdir(), 'helloworld.jar')
DEFAULT_DEPLOYMENT_NAME = "default01"
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment"

def asc_create(cmd, client, resource_group, name, location=None, no_wait=False):
    resource = None
    if location is not None:
        resource = models.AppClusterResource(location=location)

    return sdk_no_wait(no_wait, client.create_or_update,
                        resource_group_name=resource_group, app_cluster_name=name, resource=resource)
    
def asc_delete(cmd, client, resource_group, name, no_wait=False):
    return sdk_no_wait(no_wait, client.delete,
                        resource_group_name=resource_group, app_cluster_name=name)

def asc_list(cmd, client, resource_group=None):
    if resource_group is None:
        return client.list_by_subscription()
    else:
        return client.list(resource_group)  

def asc_get(cmd, client, resource_group, name):
    return client.get(resource_group, name)  

def asc_debuggingkey_list(cmd, client, resource_group, name):
    return client.list_debugging_keys(resource_group, name)

def asc_debuggingkey_regenerate(cmd, client, resource_group, name, key_type):
    return client.regenerate_debugging_key(resource_group, name, key_type)

def app_create(cmd, client, resource_group, service, name,
               is_public=None,
               cpu=None,
               memory=None,
               instance_count=None,):
    apps = _get_all_apps(client, resource_group, service)
    if name in apps:
        raise CLIError("App " + name + " already exists.")
    logger.warning("Creating app " + name)
    properties = models.AppResourceProperties(public=is_public)
    client.apps.create_or_update(resource_group, service, name, properties)

    deployment_settings = models.DeploymentSettings(
                                    cpu=cpu,
                                    memory_in_gb=memory,
                                    instance_count=instance_count)
    user_source_info = models.UserSourceInfo(relative_path='<default>', type='Jar')
    properties = models.DeploymentResourceProperties(
                            deployment_settings=deployment_settings,
                            source=user_source_info)

    # create default deployment
    logger.warning("Creating default deployment with name '" + DEFAULT_DEPLOYMENT_NAME + "'")
    poller = client.deployments.create_or_update(resource_group, service, name, DEFAULT_DEPLOYMENT_NAME, properties)
    poller.add_done_callback(lambda x: dump(client, x.resource()))
    logger.warning("Waiting for the default deployment completion")
    while poller.done() is False:
        sleep(5)

    logger.warning("Setting default deployment to production")
    properties = models.AppResourceProperties(active_deployment_name=DEFAULT_DEPLOYMENT_NAME)
    return client.apps.update(resource_group, service, name, properties)

def app_update(cmd, client, resource_group, service, name,
               is_public=None,
               deployment=None,
               runtime_version=None,
               jvm_options=None,
               env=None,
               tags=None,
               no_wait=False):
    if is_public is not None:
        properties = models.AppResourceProperties(public=is_public)
        logger.warning("Updating app " + name)
        app_updated = client.apps.update(resource_group, service, name, properties)
        dump(client.apps, app_updated)
    if deployment is None:
        deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
        if deployment is None:
            return

    logger.warning("Updating deployment " + deployment)
    deployment_settings = models.DeploymentSettings(
                                environment_variables=env,
                                jvm_options=jvm_options,
                                runtime_version=runtime_version,)
    properties = models.DeploymentResourceProperties(deployment_settings=deployment_settings)
    return sdk_no_wait(no_wait, client.deployments.update,
                        resource_group, service, name, deployment, properties)

def app_delete(cmd, client,
              resource_group,
              service,
              name):
    return client.apps.delete(resource_group, service, name)

def app_start(cmd, client,
              resource_group,
              service,
              name,
              deployment=None,
              no_wait=False):
    if deployment is None:
        deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    return sdk_no_wait(no_wait, client.deployments.start,
                        resource_group, service, name, deployment)

def app_stop(cmd, client,
             resource_group,
             service,
             name,
             deployment=None,
             no_wait=False):
    if deployment is None:
        deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    return sdk_no_wait(no_wait, client.deployments.stop,
                        resource_group, service, name, deployment)

def app_restart(cmd, client,
                resource_group,
                service,
                name,
                deployment=None,
                no_wait=False):
    if deployment is None:
        deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    return sdk_no_wait(no_wait, client.deployments.restart,
                        resource_group, service, name, deployment)

def app_list(cmd, client,
               resource_group,
               service):
    return client.apps.list(resource_group, service)

def app_get(cmd, client,
            resource_group,
            service,
            name):
    return client.apps.get(resource_group, service, name, True)

def app_deploy(cmd, client, resource_group, service, name,
               deployment=None,
               jar_path=None,
               target_module=None,
               runtime_version=None,
               jvm_options=None,
               cpu=None,
               memory=None,
               instance_count=None,
               env=None,
               tags=None,
               no_wait=False):
    if deployment is None:
        deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
        if deployment is None:
            raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    else:
        deployments = _get_all_deployments(client, resource_group, service, name)
        if deployment not in deployments:
            raise CLIError("Deployment '" + deployment + "' not found, use 'az asc app deploy create' to create a new deployment")

    file_type, file_path = _get_upload_local_file(jar_path)
    return _app_deploy(client,
                       resource_group,
                       service,
                       name,
                       deployment,
                       file_path,
                       runtime_version,
                       jvm_options,
                       cpu,
                       memory,
                       instance_count,
                       env,
                       tags,
                       no_wait,
                       file_type,
                       True)   

def app_scale(cmd, client, resource_group, service, name,
               deployment =None,
               cpu=None,
               memory=None,
               instance_count=None,
               no_wait=False):
    if deployment is None:
        deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)         
    deployment_settings = models.DeploymentSettings(
                                cpu=cpu,
                                memory_in_gb=memory,
                                instance_count=instance_count,)
    properties = models.DeploymentResourceProperties(deployment_settings=deployment_settings)
    return sdk_no_wait(no_wait, client.deployments.update,
                        resource_group, service, name, deployment, properties)

def app_get_log(cmd, client, resource_group, service, name, deployment=None):
    if deployment is None:
        deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)   
    return stream_logs(client.deployments, resource_group, service, name, deployment)


def app_set_deployment(cmd, client, resource_group, service, name, deployment):
    deployments = _get_all_deployments(client, resource_group, service, name)
    active_deployment = client.apps.get(resource_group, service, name).properties.active_deployment_name
    if deployment == active_deployment:
        raise CLIError("Deployment '" + deployment + "' is already the production deployment")
    if deployment not in deployments:
        raise CLIError("Deployment '" + deployment + "' not found, please use 'az asc app deploy create' to create new deployment first")  
    properties = models.AppResourceProperties(active_deployment_name=deployment)
    return client.apps.update(resource_group, service, name, properties)

def deployment_create(cmd, client, resource_group, service, app, name,
                      jar_path=None,
                      target_module=None,
                      runtime_version=None,
                      jvm_options=None,
                      cpu=None,
                      memory=None,
                      instance_count=None,
                      env=None,
                      tags=None,
                      no_wait=False):
    deployments = _get_all_deployments(client, resource_group, service, app)
    if name in deployments:
        raise CLIError("Deployment " + name + " already exists")

    file_type, file_path = _get_upload_local_file(jar_path)
    return _app_deploy(client,
                       resource_group,
                       service,
                       app,
                       name,
                       file_path,
                       runtime_version,
                       jvm_options,
                       cpu,
                       memory,
                       instance_count,
                       env,
                       tags,
                       no_wait,
                       file_type)     

def deployment_list(cmd, client, resource_group, service, app):
    return client.deployments.list(resource_group, service, app)

def deployment_get(cmd, client, resource_group, service, app, name):
    return client.deployments.get(resource_group, service, app, name)

def deployment_delete(cmd, client, resource_group, service, app, name):
    return client.deployments.delete(resource_group, service, app, name)


def binding_list(cmd, client, resource_group, service, app):
    return client.list(resource_group, service, app)

def binding_get(cmd, client, resource_group, service, app, name):
    return client.get(resource_group, service, app, name)

def binding_remove(cmd, client, resource_group, service, app, name):
    return client.delete(resource_group, service, app, name)

def binding_cosmos_add(cmd, client, resource_group, service, app, name,
                       resource_id,
                       api_type=None,
                       database_name=None,
                       key_space=None,
                       collection_name=None):
    resource_id_dict = parse_resource_id(resource_id)
    resource_type = resource_id_dict['resource_type']
    resource_name = resource_id_dict['resource_name']
    bindint_parameters = {}
    bindint_parameters['apiType'] = api_type
    bindint_parameters['databaseName'] = database_name
    bindint_parameters['keySpace'] = key_space
    bindint_parameters['collectionName'] = collection_name
    get_key_url = 'https://management.azure.com/subscriptions/subid/resourceGroups/{}/providers/Microsoft.DocumentDB/databaseAccounts/{}/listKeys?api-version=2015-04-08'.format(resource_group, resource_name)

    properties = models.BindingResourceProperties(
        resource_name = resource_name,
        resource_type = resource_type,
        resource_id = resource_id,
        binding_parameters = bindint_parameters
    )
    return client.create_or_update(resource_group, service, app, name, properties)

def _get_all_deployments(client, resource_group, service, app):
    deployments = []
    deployments_resource = client.deployments.list(resource_group, service, app)
    deployments = list(deployments_resource)
    deployments = (deployment.name for deployment in deployments)
    return deployments

def _get_all_apps(client, resource_group, service):
    apps = []
    apps_resource = client.apps.list(resource_group, service)
    apps = list(apps_resource)
    apps = (app.name for app in apps)
    return apps

def _app_deploy(client,
                resource_group,
                service,
                app,
                name,
                path,
                runtime_version,
                jvm_options,
                cpu,
                memory,
                instance_count,
                env,
                tags,
                no_wait=False,
                file_type="Jar",
                update=False):
    upload_url = None
    relative_path = None
    try:
        response = client.apps.get_resource_upload_url(resource_group,
                                                    service,
                                                    app,
                                                    None,
                                                    None)
        upload_url = response.upload_url
        relative_path = response.relative_path
    except (AttributeError, CloudError) as e:
        raise CLIError("Failed to get a SAS URL to upload context. Error: {}".format(e.message))
    
    if not upload_url:
        raise CLIError("Failed to get a SAS URL to upload context.")

    prase_result = urlparse(upload_url)
    storage_name = prase_result.netloc.split('.')[0]
    split_path = prase_result.path.split('/')[1:3]
    share_name = split_path[0]
    sas_token = "?" + prase_result.query
    deployment_settings = models.DeploymentSettings(
                                    cpu=cpu,
                                    memory_in_gb=memory,
                                    environment_variables=env,
                                    jvm_options=jvm_options,
                                    runtime_version=runtime_version,
                                    instance_count=instance_count,)
    user_source_info = models.UserSourceInfo(relative_path=relative_path, type=file_type)
    properties = models.DeploymentResourceProperties(
                            deployment_settings=deployment_settings,
                            source=user_source_info)

    #upload file 
    file_service = FileService(storage_name, sas_token=sas_token)
    file_service.create_file_from_path(share_name, None, relative_path, path)
    #create deployment
    if update:
        return sdk_no_wait(no_wait, client.deployments.update,
                            resource_group, service, app, name, properties)
    else:
        return sdk_no_wait(no_wait, client.deployments.create_or_update,
                            resource_group, service, app, name, properties)

def test(cmd, resource_group, service=None, app=None, deployment=None):
    return None
    #sfc = cf_asc(cmd.cli_ctx)
    #_get_resource_info("/subscriptions/685ba005-af8d-4b04-8f16-a7bf38b2eab7/resourceGroups/mymongorg/providers/Microsoft.DocumentDB/databaseAccounts/mymongo")
    #_get_upload_local_file()
    #sleep(100000)
    #zero_arg_lambda = lambda: print("dsasdsa")
    #zero_arg_lambda()
    #_pack_source_code(os.getcwd(), TEMP_TAR)
