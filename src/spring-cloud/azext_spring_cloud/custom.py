# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines

import yaml   # pylint: disable=import-error
from time import sleep
from ._stream_utils import stream_logs
from msrestazure.azure_exceptions import CloudError
from msrestazure.tools import parse_resource_id, is_valid_resource_id
from ._utils import _get_upload_local_file, _get_persistent_disk_size
from knack.util import CLIError
from .vendored_sdks.appplatform import models
from knack.log import get_logger
from .azure_storage_file import FileService
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from ast import literal_eval
from azure.cli.core.commands import cached_put
from ._utils import _get_rg_location
from ._utils import _get_sku_name
from six.moves.urllib import parse
from threading import Thread
from threading import Timer
import certifi
import urllib3
import sys
import urllib3.contrib.pyopenssl

logger = get_logger(__name__)
DEFAULT_DEPLOYMENT_NAME = "default"
DEPLOYMENT_CREATE_OR_UPDATE_SLEEP_INTERVAL = 5
APP_CREATE_OR_UPDATE_SLEEP_INTERVAL = 2

# pylint: disable=line-too-long
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment or create deployment with: az spring-cloud app deployment create"
LOG_RUNNING_PROMPT = "This command usually takes minutes to run. Add '--verbose' parameter if needed."


def spring_cloud_create(cmd, client, resource_group, name, location=None, app_insights_key=None, app_insights=None,
                        disable_distributed_tracing=None, sku=None, tags=None, no_wait=False):
    rg_location = _get_rg_location(cmd.cli_ctx, resource_group)
    if location is None:
        location = rg_location

    if sku is None:
        sku = "Standard"
    full_sku = models.Sku(name=_get_sku_name(sku), tier=sku)

    properties = models.ClusterResourceProperties()

    check_tracing_parameters(app_insights_key, app_insights, disable_distributed_tracing)
    update_tracing_config(cmd, resource_group, name, location, properties,
                          app_insights_key, app_insights, disable_distributed_tracing)

    resource = models.ServiceResource(location=location, sku=full_sku, properties=properties, tags=tags)
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name=resource_group, service_name=name, resource=resource)


def spring_cloud_update(cmd, client, resource_group, name, app_insights_key=None, app_insights=None,
                        disable_distributed_tracing=None, sku=None, tags=None, no_wait=False):
    updated_resource = models.ServiceResource()
    update_app_insights = False
    update_service_tags = False
    update_service_sku = False

    # update service sku
    if sku is not None:
        full_sku = models.Sku(name=_get_sku_name(sku), tier=sku)
        updated_resource.sku = full_sku
        update_service_sku = True

    resource = client.get(resource_group, name)
    location = resource.location
    resource_properties = resource.properties
    updated_resource_properties = models.ClusterResourceProperties()

    check_tracing_parameters(app_insights_key, app_insights, disable_distributed_tracing)
    app_insights_target_status = False
    if app_insights is not None or app_insights_key is not None or disable_distributed_tracing is False:
        app_insights_target_status = True
        if resource_properties.trace.enabled is False:
            update_app_insights = True
    elif disable_distributed_tracing is True:
        app_insights_target_status = False
        if resource_properties.trace.enabled is True:
            update_app_insights = True

    # update application insights
    if update_app_insights is True:
        if app_insights_target_status is False:
            resource_properties.trace.enabled = app_insights_target_status
        elif resource_properties.trace.app_insight_instrumentation_key is not None \
                and app_insights is None and app_insights_key is None:
            resource_properties.trace.enabled = app_insights_target_status
        else:
            update_tracing_config(cmd, resource_group, name, location, resource_properties, app_insights_key,
                                  app_insights, disable_distributed_tracing)
        updated_resource_properties.trace = resource_properties.trace

    # update service tags
    if tags is not None:
        updated_resource.tags = tags
        update_service_tags = True

    if update_app_insights is False and update_service_tags is False and update_service_sku is False:
        return resource

    updated_resource.properties = updated_resource_properties
    return sdk_no_wait(no_wait, client.update,
                       resource_group_name=resource_group, service_name=name, resource=updated_resource)


def spring_cloud_delete(cmd, client, resource_group, name, no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group, service_name=name)


def spring_cloud_list(cmd, client, resource_group=None):
    if resource_group is None:
        return client.list_by_subscription()
    return client.list(resource_group)


def spring_cloud_get(cmd, client, resource_group, name):
    return client.get(resource_group, name)


def enable_test_endpoint(cmd, client, resource_group, name):
    return client.services.enable_test_endpoint(resource_group, name)


def disable_test_endpoint(cmd, client, resource_group, name):
    return client.services.disable_test_endpoint(resource_group, name)


def list_keys(cmd, client, resource_group, name, app=None, deployment=None):
    keys = client.services.list_test_keys(resource_group, name)
    if not keys.enabled:
        return None
    if app:
        if deployment is None:
            deployment = client.apps.get(
                resource_group, name, app).properties.active_deployment_name
        if deployment:
            client.deployments.get(resource_group, name, app, deployment)
            keys.primary_test_endpoint = "{}/{}/{}/".format(
                keys.primary_test_endpoint, app, deployment)
            keys.secondary_test_endpoint = "{}/{}/{}/".format(
                keys.secondary_test_endpoint, app, deployment)
    return keys


# pylint: disable=redefined-builtin
def regenerate_keys(cmd, client, resource_group, name, type):
    return client.services.regenerate_test_key(resource_group, name, type)


def app_create(cmd, client, resource_group, service, name,
               is_public=None,
               cpu=None,
               memory=None,
               instance_count=None,
               runtime_version=None,
               jvm_options=None,
               env=None,
               enable_persistent_storage=None,
               assign_identity=None):
    apps = _get_all_apps(client, resource_group, service)
    if name in apps:
        raise CLIError("App '{}' already exists.".format(name))
    logger.warning("[1/4] Creating app with name '{}'".format(name))
    properties = models.AppResourceProperties()
    properties.temporary_disk = models.TemporaryDisk(
        size_in_gb=5, mount_path="/tmp")

    resource = client.services.get(resource_group, service)
    location = resource.location

    app_resource = models.AppResource()
    app_resource.properties = properties
    app_resource.location = location
    if assign_identity is True:
        app_resource.identity = models.ManagedIdentityProperties(type="systemassigned")

    poller = client.apps.create_or_update(
        resource_group, service, name, app_resource)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    deployment_settings = models.DeploymentSettings(
        cpu=cpu,
        memory_in_gb=memory,
        instance_count=instance_count,
        environment_variables=env,
        jvm_options=jvm_options,
        runtime_version=runtime_version,)
    user_source_info = models.UserSourceInfo(
        relative_path='<default>', type='Jar')
    properties = models.DeploymentResourceProperties(
        deployment_settings=deployment_settings,
        source=user_source_info)

    # create default deployment
    logger.warning(
        "[2/4] Creating default deployment with name '{}'".format(DEFAULT_DEPLOYMENT_NAME))
    poller = client.deployments.create_or_update(
        resource_group, service, name, DEFAULT_DEPLOYMENT_NAME, properties)

    logger.warning("[3/4] Setting default deployment to production")
    properties = models.AppResourceProperties(
        active_deployment_name=DEFAULT_DEPLOYMENT_NAME, public=is_public)

    if enable_persistent_storage:
        properties.persistent_disk = models.PersistentDisk(
            size_in_gb=_get_persistent_disk_size(resource.sku.tier), mount_path="/persistent")
    else:
        properties.persistent_disk = models.PersistentDisk(
            size_in_gb=0, mount_path="/persistent")

    app_resource.properties = properties
    app_resource.location = location

    app_poller = client.apps.update(resource_group, service, name, app_resource)
    logger.warning(
        "[4/4] Updating app '{}' (this operation can take a while to complete)".format(name))
    while not poller.done() or not app_poller.done():
        sleep(DEPLOYMENT_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    active_deployment = client.deployments.get(
        resource_group, service, name, DEFAULT_DEPLOYMENT_NAME)
    app = client.apps.get(resource_group, service, name)
    app.properties.active_deployment = active_deployment
    logger.warning("App create succeeded")
    return app


def app_update(cmd, client, resource_group, service, name,
               is_public=None,
               deployment=None,
               runtime_version=None,
               jvm_options=None,
               env=None,
               enable_persistent_storage=None,
               https_only=None):
    resource = client.services.get(resource_group, service)
    location = resource.location

    properties = models.AppResourceProperties(public=is_public, https_only=https_only)
    if enable_persistent_storage is True:
        properties.persistent_disk = models.PersistentDisk(
            size_in_gb=_get_persistent_disk_size(resource.sku.tier), mount_path="/persistent")
    if enable_persistent_storage is False:
        properties.persistent_disk = models.PersistentDisk(size_in_gb=0)

    app_resource = models.AppResource()
    app_resource.properties = properties
    app_resource.location = location

    logger.warning("[1/2] updating app '{}'".format(name))
    poller = client.apps.update(
        resource_group, service, name, app_resource)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    app_updated = client.apps.get(resource_group, service, name)

    if deployment is None:
        logger.warning(
            "No '--deployment' given, will update app's production deployment")
        deployment = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
        if deployment is None:
            logger.warning("No deployment found for update")
            return app_updated

    logger.warning("[2/2] Updating deployment '{}'".format(deployment))
    deployment_settings = models.DeploymentSettings(
        cpu=None,
        memory_in_gb=None,
        instance_count=None,
        environment_variables=env,
        jvm_options=jvm_options,
        runtime_version=runtime_version,)
    properties = models.DeploymentResourceProperties(
        deployment_settings=deployment_settings)
    poller = client.deployments.update(
        resource_group, service, name, deployment, properties)
    while poller.done() is False:
        sleep(DEPLOYMENT_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    deployment = client.deployments.get(
        resource_group, service, name, deployment)
    app_updated.properties.active_deployment = deployment
    return app_updated


def app_delete(cmd, client,
               resource_group,
               service,
               name):
    client.apps.get(resource_group, service, name)
    return client.apps.delete(resource_group, service, name)


def app_start(cmd, client,
              resource_group,
              service,
              name,
              deployment=None,
              no_wait=False):
    if deployment is None:
        deployment = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
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
        deployment = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
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
        deployment = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    return sdk_no_wait(no_wait, client.deployments.restart,
                       resource_group, service, name, deployment)


def app_list(cmd, client,
             resource_group,
             service):
    apps = list(client.apps.list(resource_group, service))
    deployments = list(
        client.deployments.list_cluster_all_deployments(resource_group, service))
    for app in apps:
        if app.properties.active_deployment_name:
            deployment = next(
                (x for x in deployments if x.properties.app_name == app.name))
            app.properties.active_deployment = deployment

    return apps


def app_get(cmd, client,
            resource_group,
            service,
            name):
    app = client.apps.get(resource_group, service, name)
    deployment_name = app.properties.active_deployment_name
    if deployment_name:
        deployment = client.deployments.get(
            resource_group, service, name, deployment_name)
        app.properties.active_deployment = deployment

    return app


def app_deploy(cmd, client, resource_group, service, name,
               version=None,
               deployment=None,
               jar_path=None,
               target_module=None,
               runtime_version=None,
               jvm_options=None,
               cpu=None,
               memory=None,
               instance_count=None,
               env=None,
               no_wait=False):
    logger.warning(LOG_RUNNING_PROMPT)
    if not deployment:
        deployment = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
        if not deployment:
            raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)

    client.deployments.get(resource_group, service, name, deployment)

    file_type, file_path = _get_upload_local_file(jar_path)

    return _app_deploy(client,
                       resource_group,
                       service,
                       name,
                       deployment,
                       version,
                       file_path,
                       runtime_version,
                       jvm_options,
                       cpu,
                       memory,
                       instance_count,
                       env,
                       target_module,
                       no_wait,
                       file_type,
                       True)


def app_scale(cmd, client, resource_group, service, name,
              deployment=None,
              cpu=None,
              memory=None,
              instance_count=None,
              no_wait=False):
    if deployment is None:
        deployment = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    deployment_settings = models.DeploymentSettings(
        cpu=cpu,
        memory_in_gb=memory,
        instance_count=instance_count,)
    properties = models.DeploymentResourceProperties(
        deployment_settings=deployment_settings)
    return sdk_no_wait(no_wait, client.deployments.update,
                       resource_group, service, name, deployment, properties)


def app_get_build_log(cmd, client, resource_group, service, name, deployment=None):
    if deployment is None:
        deployment = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
    if deployment is None:
        raise CLIError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    deployment_properties = client.deployments.get(
        resource_group, service, name, deployment).properties
    if deployment_properties.source.type == "Jar":
        raise CLIError("Jar deployment has no build logs.")
    return stream_logs(client.deployments, resource_group, service, name, deployment)


def app_tail_log(cmd, client, resource_group, service, name, instance=None, follow=False, lines=50, since=None, limit=2048):
    if not instance:
        deployment_name = client.apps.get(
            resource_group, service, name).properties.active_deployment_name
        if not deployment_name:
            raise CLIError(
                "No production deployment found for app '{}'".format(name))
        deployment = client.deployments.get(
            resource_group, service, name, deployment_name)
        if not deployment.properties.instances:
            raise CLIError("No instances found for deployment '{0}' in app '{1}'".format(
                deployment_name, name))
        instances = deployment.properties.instances
        if len(instances) > 1:
            logger.warning("Mulitple app instances found:")
            for temp_instance in instances:
                logger.warning("{}".format(temp_instance.name))
            logger.warning("Please use '-i/--instance' parameter to specify the instance name")
            return None
        instance = instances[0].name

    primary_key = client.services.list_test_keys(
        resource_group, service).primary_key
    if not primary_key:
        raise CLIError("To use the log streaming feature, please enable the test endpoint")

    base_url = 'azuremicroservices.io' if cmd.cli_ctx.cloud.name == 'AzureCloud' else 'asc-test.net'
    streaming_url = "https://{0}.{1}/api/logstream/apps/{2}/instances/{3}".format(
        service, base_url, name, instance)
    params = {}
    params["tailLines"] = lines
    params["limitBytes"] = limit
    if since:
        params["sinceSeconds"] = since
    if follow:
        params["follow"] = True

    exceptions = []
    streaming_url += "?{}".format(parse.urlencode(params)) if params else ""
    t = Thread(target=_get_app_log, args=(
        streaming_url, "primary", primary_key, exceptions))
    t.daemon = True
    t.start()

    while t.is_alive():
        sleep(5)  # so that ctrl+c can stop the command

    if exceptions:
        raise exceptions[0]


def app_identity_assign(cmd, client, resource_group, service, name, role=None, scope=None):
    app_resource = models.AppResource()
    identity = models.ManagedIdentityProperties(type="systemassigned")
    properties = models.AppResourceProperties()
    resource = client.services.get(resource_group, service)
    location = resource.location

    app_resource.identity = identity
    app_resource.properties = properties
    app_resource.location = location
    client.apps.update(resource_group, service, name, app_resource)
    app = client.apps.get(resource_group, service, name)
    if role:
        principal_id = app.identity.principal_id

        from azure.cli.core.commands import arm as _arm
        identity_role_id = _arm.resolve_role_id(cmd.cli_ctx, role, scope)
        assignments_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION).role_assignments
        RoleAssignmentCreateParameters = get_sdk(cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                                 'RoleAssignmentCreateParameters', mod='models',
                                                 operation_group='role_assignments')
        parameters = RoleAssignmentCreateParameters(role_definition_id=identity_role_id, principal_id=principal_id)
        logger.info("Creating an assignment with a role '%s' on the scope of '%s'", identity_role_id, scope)
        retry_times = 36
        assignment_name = _arm._gen_guid()
        for l in range(0, retry_times):
            try:
                assignments_client.create(scope=scope, role_assignment_name=assignment_name,
                                          parameters=parameters)
                break
            except CloudError as ex:
                if 'role assignment already exists' in ex.message:
                    logger.info('Role assignment already exists')
                    break
                elif l < retry_times and ' does not exist in the directory ' in ex.message:
                    sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)
                    logger.warning('Retrying role assignment creation: %s/%s', l + 1,
                                   retry_times)
                    continue
                else:
                    raise
    return app


def app_identity_remove(cmd, client, resource_group, service, name):
    app_resource = models.AppResource()
    identity = models.ManagedIdentityProperties(type="none")
    properties = models.AppResourceProperties()
    resource = client.services.get(resource_group, service)
    location = resource.location

    app_resource.identity = identity
    app_resource.properties = properties
    app_resource.location = location
    return client.apps.update(resource_group, service, name, app_resource)


def app_identity_show(cmd, client, resource_group, service, name):
    app = client.apps.get(resource_group, service, name)
    return app.identity


def app_set_deployment(cmd, client, resource_group, service, name, deployment):
    deployments = _get_all_deployments(client, resource_group, service, name)
    active_deployment = client.apps.get(
        resource_group, service, name).properties.active_deployment_name
    if deployment == active_deployment:
        raise CLIError("Deployment '" + deployment +
                       "' is already the production deployment")
    if deployment not in deployments:
        raise CLIError("Deployment '" + deployment +
                       "' not found, please use 'az spring-cloud app deployment create' to create the new deployment")
    properties = models.AppResourceProperties(
        active_deployment_name=deployment)

    resource = client.services.get(resource_group, service)
    location = resource.location

    app_resource = models.AppResource()
    app_resource.properties = properties
    app_resource.location = location

    return client.apps.update(resource_group, service, name, app_resource)


def deployment_create(cmd, client, resource_group, service, app, name,
                      skip_clone_settings=False,
                      version=None,
                      jar_path=None,
                      target_module=None,
                      runtime_version=None,
                      jvm_options=None,
                      cpu=None,
                      memory=None,
                      instance_count=None,
                      env=None,
                      no_wait=False):
    logger.warning(LOG_RUNNING_PROMPT)
    deployments = _get_all_deployments(client, resource_group, service, app)
    if name in deployments:
        raise CLIError("Deployment " + name + " already exists")

    if not skip_clone_settings:
        active_deployment_name = client.apps.get(
            resource_group, service, app).properties.active_deployment_name
        active_deployment = client.deployments.get(
            resource_group, service, app, active_deployment_name)
        if active_deployment:
            cpu = cpu or active_deployment.properties.deployment_settings.cpu
            memory = memory or active_deployment.properties.deployment_settings.memory_in_gb
            instance_count = instance_count or active_deployment.properties.deployment_settings.instance_count
            jvm_options = jvm_options or active_deployment.properties.deployment_settings.jvm_options
            env = env or active_deployment.properties.deployment_settings.environment_variables

    file_type, file_path = _get_upload_local_file(jar_path)
    return _app_deploy(client, resource_group, service, app, name, version, file_path,
                       runtime_version,
                       jvm_options,
                       cpu,
                       memory,
                       instance_count,
                       env,
                       target_module,
                       no_wait,
                       file_type)


def deployment_list(cmd, client, resource_group, service, app):
    return client.deployments.list(resource_group, service, app)


def deployment_get(cmd, client, resource_group, service, app, name):
    return client.deployments.get(resource_group, service, app, name)


def deployment_delete(cmd, client, resource_group, service, app, name):
    client.deployments.get(resource_group, service, app, name)
    return client.deployments.delete(resource_group, service, app, name)


def config_set(cmd, client, resource_group, name, config_file, no_wait=False):
    def standardization(dic):
        new_dic = {}
        for k, v in dic.items():
            ks = k.split("-")
            ks = [seg[0].upper() + seg[1:] for seg in ks]
            k = ''.join(ks)
            k = k[0].lower() + k[1:]
            new_dic[k] = v

        if 'pattern' in new_dic and isinstance(new_dic['pattern'], str):
            new_dic['pattern'] = new_dic['pattern'].split(',')
        if 'searchPaths' in new_dic and isinstance(new_dic['searchPaths'], str):
            new_dic['searchPaths'] = new_dic['searchPaths'].split(',')
        return new_dic

    with open(config_file, 'r') as stream:
        yaml_object = yaml.safe_load(stream)
    config_property = yaml_object['spring']['cloud']['config']['server']['git']

    if 'default-label' in config_property:
        config_property['label'] = config_property['default-label']
        del config_property['default-label']

    config_property = standardization(config_property)
    repositories = []
    if 'repos' in config_property:
        for k, v in config_property['repos'].items():
            if 'default-label' in v:
                v['label'] = v['default-label']
                del v['default-label']
            v['name'] = k
            v = standardization(v)
            repositories.append(v)
        del config_property['repos']

    config_property['repositories'] = repositories
    git_property = client._deserialize(
        'ConfigServerGitProperty', config_property)
    config_server_settings = models.ConfigServerSettings(
        git_property=git_property)
    config_server_properties = models.ConfigServerProperties(
        config_server=config_server_settings)
    cluster_esource_properties = models.ClusterResourceProperties(
        config_server_properties=config_server_properties)
    service_resource = models.ServiceResource(
        properties=cluster_esource_properties)
    return sdk_no_wait(no_wait, client.update,
                       resource_group, name, service_resource)


def config_get(cmd, client, resource_group, name):
    resource = client.get(resource_group, name)
    config_server = resource.properties.config_server_properties.config_server
    if not config_server:
        raise CLIError("Config server not set.")
    return config_server.git_property


def config_delete(cmd, client, resource_group, name):
    config_server_properties = models.ConfigServerProperties(
        config_server=models.ConfigServerSettings())
    properties = models.ClusterResourceProperties(
        config_server_properties=config_server_properties)
    appResource = models.ServiceResource(properties=properties)

    return client.update(resource_group, name, appResource)


def config_git_set(cmd, client, resource_group, name, uri,
                   label=None,
                   search_paths=None,
                   username=None,
                   password=None,
                   host_key=None,
                   host_key_algorithm=None,
                   private_key=None,
                   strict_host_key_checking=None):
    resource = client.get(resource_group, name)
    config_server = resource.properties.config_server_properties.config_server
    config = models.ConfigServerGitProperty(
        uri=uri) if not config_server else config_server.git_property

    if search_paths:
        search_paths = search_paths.split(",")

    config.uri = uri
    config.label = label
    config.search_paths = search_paths
    config.username = username
    config.password = password
    config.host_key = host_key
    config.host_key_algorithm = host_key_algorithm
    config.private_key = private_key
    config.strict_host_key_checking = strict_host_key_checking

    config_server = models.ConfigServerSettings(git_property=config)
    config_server_properties = models.ConfigServerProperties(
        config_server=config_server)
    cluster_esource_properties = models.ClusterResourceProperties(
        config_server_properties=config_server_properties)
    service_resource = models.ServiceResource(
        properties=cluster_esource_properties)

    return cached_put(cmd, client.update, service_resource, resource_group, name).result()


def config_repo_add(cmd, client, resource_group, name, uri, repo_name,
                    pattern=None,
                    label=None,
                    search_paths=None,
                    username=None,
                    password=None,
                    host_key=None,
                    host_key_algorithm=None,
                    private_key=None,
                    strict_host_key_checking=None):
    resource = client.get(resource_group, name)
    config_server = resource.properties.config_server_properties.config_server
    config = models.ConfigServerGitProperty(
        uri=uri) if not config_server else config_server.git_property

    if search_paths:
        search_paths = search_paths.split(",")

    if config.repositories:
        repos = [repo for repo in config.repositories if repo.name == repo_name]
        if repos:
            raise CLIError("Repo '{}' already exiests.".format(repo_name))
    else:
        config.repositories = []

    repository = models.GitPatternRepository(
        uri=uri,
        name=repo_name,
        label=label,
        search_paths=search_paths,
        username=username,
        password=password,
        host_key=host_key,
        host_key_algorithm=host_key_algorithm,
        private_key=private_key,
        strict_host_key_checking=strict_host_key_checking)

    config.repositories.append(repository)
    config_server_settings = models.ConfigServerSettings(git_property=config)
    config_server_properties = models.ConfigServerProperties(
        config_server=config_server_settings)
    cluster_resource_properties = models.ClusterResourceProperties(
        config_server_properties=config_server_properties)
    service_resource = models.ServiceResource(
        properties=cluster_resource_properties)
    return cached_put(cmd, client.update, service_resource, resource_group, name).result()


def config_repo_delete(cmd, client, resource_group, name, repo_name):
    resource = client.get(resource_group, name)
    config_server = resource.properties.config_server_properties.config_server
    if not config_server or not config_server.config or not config_server.config.repositories:
        raise CLIError("Repo '{}' not found.".format(repo_name))

    config = config_server.git_property
    repository = [
        repo for repo in config.repositories if repo.name == repo_name]
    if not repository:
        raise CLIError("Repo '{}' not found.".format(repo_name))

    config.repositories.remove(repository[0])

    config_server_settings = models.ConfigServerSettings(git_property=config)
    config_server_properties = models.ConfigServerProperties(
        config_server=config_server_settings)
    cluster_esource_properties = models.ClusterResourceProperties(
        config_server_properties=config_server_properties)
    service_resource = models.ServiceResource(
        properties=cluster_esource_properties)

    return cached_put(cmd, client.update, service_resource, resource_group, name).result()


def config_repo_update(cmd, client, resource_group, name, repo_name,
                       uri=None,
                       pattern=None,
                       label=None,
                       search_paths=None,
                       username=None,
                       password=None,
                       host_key=None,
                       host_key_algorithm=None,
                       private_key=None,
                       strict_host_key_checking=None):
    resource = client.get(resource_group, name)
    config_server = resource.properties.config_server_properties.config_server
    if not config_server or not config_server.git_property or not config_server.git_property.repositories:
        raise CLIError("Repo '{}' not found.".format(repo_name))
    config = config_server.git_property
    repository = [
        repo for repo in config.repositories if repo.name == repo_name]
    if not repository:
        raise CLIError("Repo '{}' not found.".format(repo_name))

    if search_paths:
        search_paths = search_paths.split(",")

    if pattern:
        pattern = pattern.split(",")

    repository = repository[0]
    repository = models.GitPatternRepository()
    repository.uri = uri or repository.uri
    repository.label = label or repository.label
    repository.search_paths = search_paths or repository.search_paths
    repository.username = username or repository.username
    repository.password = password or repository.password
    repository.host_key = host_key or repository.host_key
    repository.host_key_algorithm = host_key_algorithm or repository.host_key_algorithm
    repository.private_key = private_key or repository.private_key
    repository.strict_host_key_checking = strict_host_key_checking or repository.strict_host_key_checking

    config_server_settings = models.ConfigServerSettings(git_property=config)
    config_server_properties = models.ConfigServerProperties(
        config_server=config_server_settings)
    cluster_esource_properties = models.ClusterResourceProperties(
        config_server_properties=config_server_properties)
    service_resource = models.ServiceResource(
        properties=cluster_esource_properties)

    return cached_put(cmd, client.update, service_resource, resource_group, name).result()


def config_repo_list(cmd, client, resource_group, name):
    resource = client.get(resource_group, name)
    config = resource.properties.config_server_properties.config_server.git_property
    return config.repositories


def binding_list(cmd, client, resource_group, service, app):
    return client.list(resource_group, service, app)


def binding_get(cmd, client, resource_group, service, app, name):
    return client.get(resource_group, service, app, name)


def binding_remove(cmd, client, resource_group, service, app, name):
    return client.delete(resource_group, service, app, name)


def binding_cosmos_add(cmd, client, resource_group, service, app, name,
                       resource_id,
                       api_type,
                       database_name=None,
                       key_space=None,
                       collection_name=None):
    resource_id_dict = parse_resource_id(resource_id)
    resource_type = resource_id_dict['resource_type']
    resource_name = resource_id_dict['resource_name']
    binding_parameters = {}
    binding_parameters['apiType'] = api_type
    if database_name:
        binding_parameters['databaseName'] = database_name
    if key_space:
        binding_parameters['keySpace'] = key_space
    if collection_name:
        binding_parameters['collectionName'] = collection_name

    try:
        primary_key = _get_cosmosdb_primary_key(client, resource_id)
    except:
        raise CLIError(
            "Couldn't get cosmosdb {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        resource_name=resource_name,
        resource_type=resource_type,
        resource_id=resource_id,
        key=primary_key,
        binding_parameters=binding_parameters
    )
    return client.create_or_update(resource_group, service, app, name, properties)


def binding_cosmos_update(cmd, client, resource_group, service, app, name,
                          database_name=None,
                          key_space=None,
                          collection_name=None):
    binding = client.get(resource_group, service, app, name).properties
    resource_id = binding.resource_id
    resource_name = binding.resource_name
    binding_parameters = {}
    binding_parameters['databaseName'] = database_name
    binding_parameters['keySpace'] = key_space
    binding_parameters['collectionName'] = collection_name

    try:
        primary_key = _get_cosmosdb_primary_key(client, resource_id)
    except:
        raise CLIError(
            "Couldn't get cosmosdb {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        key=primary_key,
        binding_parameters=binding_parameters
    )
    return client.update(resource_group, service, app, name, properties)


def binding_mysql_add(cmd, client, resource_group, service, app, name,
                      resource_id,
                      key,
                      username,
                      database_name):
    resource_id_dict = parse_resource_id(resource_id)
    resource_type = resource_id_dict['resource_type']
    resource_name = resource_id_dict['resource_name']
    binding_parameters = {}
    binding_parameters['username'] = username
    binding_parameters['databaseName'] = database_name

    properties = models.BindingResourceProperties(
        resource_name=resource_name,
        resource_type=resource_type,
        resource_id=resource_id,
        key=key,
        binding_parameters=binding_parameters
    )
    return client.create_or_update(resource_group, service, app, name, properties)


def binding_mysql_update(cmd, client, resource_group, service, app, name,
                         key=None,
                         username=None,
                         database_name=None):
    binding_parameters = {}
    binding_parameters['username'] = username
    binding_parameters['databaseName'] = database_name

    properties = models.BindingResourceProperties(
        key=key,
        binding_parameters=binding_parameters
    )
    return client.update(resource_group, service, app, name, properties)


def binding_redis_add(cmd, client, resource_group, service, app, name,
                      resource_id,
                      disable_ssl=None):
    use_ssl = not disable_ssl
    resource_id_dict = parse_resource_id(resource_id)
    resource_type = resource_id_dict['resource_type']
    resource_name = resource_id_dict['resource_name']
    binding_parameters = {}
    binding_parameters['useSsl'] = use_ssl
    primary_key = None
    try:
        primary_key = _get_redis_primary_key(client, resource_id)
    except:
        raise CLIError(
            "Couldn't get redis {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        resource_name=resource_name,
        resource_type=resource_type,
        resource_id=resource_id,
        key=primary_key,
        binding_parameters=binding_parameters
    )

    return client.create_or_update(resource_group, service, app, name, properties)


def binding_redis_update(cmd, client, resource_group, service, app, name,
                         disable_ssl=None):
    binding = client.get(resource_group, service, app, name).properties
    resource_id = binding.resource_id
    resource_name = binding.resource_name
    binding_parameters = {}
    if disable_ssl:
        binding_parameters['useSsl'] = not disable_ssl

    primary_key = None
    try:
        primary_key = _get_redis_primary_key(client, resource_id)
    except:
        raise CLIError(
            "Couldn't get redis {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        key=primary_key,
        binding_parameters=binding_parameters
    )
    return client.update(resource_group, service, app, name, properties)


def _get_cosmosdb_primary_key(client, resource_id):
    url = '{}/listKeys'.format(resource_id)
    operation_config = {}
    # Construct parameters
    query_parameters = {}
    query_parameters['api-version'] = client._serialize.query(
        "client.api_version", '2015-04-08', 'str')

    # Construct headers
    header_parameters = {}
    header_parameters['Accept'] = 'application/json'

    # Construct and send request
    request = client._client.post(url, query_parameters, header_parameters)
    response = client._client.send(request, stream=False, **operation_config)
    keys = response.content.decode("utf-8")
    keys_dict = literal_eval(keys)
    return keys_dict['primaryMasterKey']


def _get_redis_primary_key(client, resource_id):
    url = '{}/listKeys'.format(resource_id)
    operation_config = {}
    # Construct parameters
    query_parameters = {}
    query_parameters['api-version'] = client._serialize.query(
        "client.api_version", '2016-04-01', 'str')

    # Construct headers
    header_parameters = {}
    header_parameters['Accept'] = 'application/json'

    # Construct and send request
    request = client._client.post(url, query_parameters, header_parameters)
    response = client._client.send(request, stream=False, **operation_config)
    keys = response.content.decode("utf-8")
    keys_dict = literal_eval(keys)
    return keys_dict['primaryKey']


def _get_all_deployments(client, resource_group, service, app):
    deployments = []
    deployments_resource = client.deployments.list(
        resource_group, service, app)
    deployments = list(deployments_resource)
    deployments = (deployment.name for deployment in deployments)
    return deployments


def _get_all_apps(client, resource_group, service):
    apps = []
    apps_resource = client.apps.list(resource_group, service)
    apps = list(apps_resource)
    apps = (app.name for app in apps)
    return apps


# pylint: disable=too-many-locals, no-member
def _app_deploy(client, resource_group, service, app, name, version, path, runtime_version, jvm_options, cpu, memory,
                instance_count,
                env,
                target_module=None,
                no_wait=False,
                file_type="Jar",
                update=False):
    upload_url = None
    relative_path = None
    logger.warning("[1/3] Requesting for upload URL")
    try:
        response = client.apps.get_resource_upload_url(resource_group,
                                                       service,
                                                       app,
                                                       None,
                                                       None)
        upload_url = response.upload_url
        relative_path = response.relative_path
    except (AttributeError, CloudError) as e:
        raise CLIError(
            "Failed to get a SAS URL to upload context. Error: {}".format(e.message))

    if not upload_url:
        raise CLIError("Failed to get a SAS URL to upload context.")

    prase_result = parse.urlparse(upload_url)
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
    user_source_info = models.UserSourceInfo(
        version=version,
        relative_path=relative_path,
        type=file_type,
        artifact_selector=target_module)
    properties = models.DeploymentResourceProperties(
        deployment_settings=deployment_settings,
        source=user_source_info)

    # upload file
    logger.warning("[2/3] Uploading package to blob")
    file_service = FileService(storage_name, sas_token=sas_token)
    file_service.create_file_from_path(share_name, None, relative_path, path)

    if file_type == "Source" and not no_wait:
        def get_log_url():
            try:
                log_file_url_response = client.deployments.get_log_file_url(
                    resource_group_name=resource_group,
                    service_name=service,
                    app_name=app,
                    deployment_name=name)
                if not log_file_url_response:
                    return None
                return log_file_url_response.url
            except CloudError:
                return None

        def get_logs_loop():
            log_url = None
            while not log_url or log_url == old_log_url:
                log_url = get_log_url()
                sleep(10)

            logger.info("Trying to fetch build logs")
            stream_logs(client.deployments, resource_group, service,
                        app, name, logger_level_func=logger.info)

        old_log_url = get_log_url()

        timer = Timer(3, get_logs_loop)
        timer.daemon = True
        timer.start()

    # create deployment
    logger.warning(
        "[3/3] Updating deployment in app '{}' (this operation can take a while to complete)".format(app))
    if update:
        return sdk_no_wait(no_wait, client.deployments.update,
                           resource_group, service, app, name, properties)

    return sdk_no_wait(no_wait, client.deployments.create_or_update,
                       resource_group, service, app, name, properties)


def _get_app_log(url, user_name, password, exceptions):
    try:
        urllib3.contrib.pyopenssl.inject_into_urllib3()
    except ImportError:
        pass

    def stream(self, amt=2 ** 16, decode_content=None):
        if self.chunked and self.supports_chunked_reads():
            try:
                for line in self.read_chunked(amt, decode_content=decode_content):
                    yield line
            except urllib3.exceptions.ProtocolError:
                return
        else:
            while not self.is_fp_closed(self._fp):
                data = self.read(amt=amt, decode_content=decode_content)

                if data:
                    yield data

    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    headers = urllib3.util.make_headers(
        basic_auth='{0}:{1}'.format(user_name, password))
    response = http.request(
        'GET',
        url,
        headers=headers,
        preload_content=False
    )
    try:
        if response.status != 200:
            raise CLIError("Failed to connect to the server with status code '{}' and reason '{}'".format(
                response.status, response.reason))
        std_encoding = sys.stdout.encoding

        for chunk in stream(response):
            if chunk:
                sys.stdout.write(chunk.decode(encoding='utf-8', errors='replace')
                                 .encode(std_encoding, errors='replace')
                                 .decode(std_encoding, errors='replace'))
        response.release_conn()
    except CLIError as e:
        exceptions.append(e)


def certificate_add(cmd, client, resource_group, service, name, vault_uri, vault_certificate_name):
    properties = models.CertificateProperties(
        vault_uri=vault_uri,
        key_vault_cert_name=vault_certificate_name
    )
    return client.certificates.create_or_update(resource_group, service, name, properties)


def certificate_show(cmd, client, resource_group, service, name):
    return client.certificates.get(resource_group, service, name)


def certificate_list(cmd, client, resource_group, service):
    return client.certificates.list(resource_group, service)


def certificate_remove(cmd, client, resource_group, service, name):
    client.certificates.get(resource_group, service, name)
    return client.certificates.delete(resource_group, service, name)


def domain_bind(cmd, client, resource_group, service, app,
                domain_name,
                certificate=None):
    properties = models.CustomDomainProperties()
    if certificate is not None:
        certificate_response = client.certificates.get(resource_group, service, certificate)
        properties = models.CustomDomainProperties(
            thumbprint=certificate_response.properties.thumbprint,
            cert_name=certificate
        )
    return client.custom_domains.create_or_update(resource_group, service, app, domain_name, properties)


def domain_show(cmd, client, resource_group, service, app, domain_name):
    return client.custom_domains.get(resource_group, service, app, domain_name)


def domain_list(cmd, client, resource_group, service, app):
    return client.custom_domains.list(resource_group, service, app)


def domain_update(cmd, client, resource_group, service, app,
                  domain_name,
                  certificate=None):
    properties = models.CustomDomainProperties()
    if certificate is not None:
        certificate_response = client.certificates.get(resource_group, service, certificate)
        properties = models.CustomDomainProperties(
            thumbprint=certificate_response.properties.thumbprint,
            cert_name=certificate
        )
    return client.custom_domains.create_or_update(resource_group, service, app, domain_name, properties)


def domain_unbind(cmd, client, resource_group, service, app, domain_name):
    client.custom_domains.get(resource_group, service, app, domain_name)
    return client.custom_domains.delete(resource_group, service, app, domain_name)


def get_app_insights_key(cli_ctx, resource_group, name):
    appinsights_client = get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient)
    appinsights = appinsights_client.components.get(resource_group, name)
    if appinsights is None or appinsights.instrumentation_key is None:
        raise CLIError("App Insights {} under resource group {} was not found.".format(name, resource_group))
    return appinsights.instrumentation_key


def check_tracing_parameters(app_insights_key, app_insights, disable_distributed_tracing):
    if (app_insights is not None or app_insights_key is not None) and disable_distributed_tracing is True:
        raise CLIError("Conflict detected: '--app-insights' or '--app-insights-key' can not be set with '--disable-distributed-tracing true'.")
    if app_insights is not None and app_insights_key is not None:
        raise CLIError("Conflict detected: '--app-insights' and '--app-insights-key' can not be set at the same time.")


def update_tracing_config(cmd, resource_group, service_name, location, resource_properties, app_insights_key,
                          app_insights, disable_distributed_tracing):
    create_app_insights = False

    if app_insights_key is not None:
        resource_properties.trace = models.TraceProperties(
            enabled=True, app_insight_instrumentation_key=app_insights_key)
    elif app_insights is not None:
        if is_valid_resource_id(app_insights):
            resource_id_dict = parse_resource_id(app_insights)
            instrumentation_key = get_app_insights_key(cmd.cli_ctx, resource_id_dict['resource_group'],
                                                       resource_id_dict['resource_name'])
            resource_properties.trace = models.TraceProperties(
                enabled=True, app_insight_instrumentation_key=instrumentation_key)
        else:
            instrumentation_key = get_app_insights_key(cmd.cli_ctx, resource_group, app_insights)
            resource_properties.trace = models.TraceProperties(
                enabled=True, app_insight_instrumentation_key=instrumentation_key)
    elif disable_distributed_tracing is not True:
        create_app_insights = True

    if create_app_insights is True:
        try:
            instrumentation_key = try_create_application_insights(cmd, resource_group, service_name, location)
            if instrumentation_key is not None:
                resource_properties.trace = models.TraceProperties(
                    enabled=True, app_insight_instrumentation_key=instrumentation_key)
        except Exception:  # pylint: disable=broad-except
            logger.warning(
                'Error while trying to create and configure an Application Insights for the Azure Spring Cloud. '
                'Please use the Azure Portal to create and configure the Application Insights, if needed.')


def try_create_application_insights(cmd, resource_group, name, location):
    creation_failed_warn = 'Unable to create the Application Insights for the Azure Spring Cloud. ' \
                           'Please use the Azure Portal to manually create and configure the Application Insights, ' \
                           'if needed.'

    ai_resource_group_name = resource_group
    ai_name = name
    ai_location = location

    app_insights_client = get_mgmt_service_client(cmd.cli_ctx, ApplicationInsightsManagementClient)
    ai_properties = {
        "name": ai_name,
        "location": ai_location,
        "kind": "web",
        "properties": {
            "Application_Type": "web"
        }
    }
    appinsights = app_insights_client.components.create_or_update(ai_resource_group_name, ai_name, ai_properties)
    if appinsights is None or appinsights.instrumentation_key is None:
        logger.warning(creation_failed_warn)
        return None

    # We make this success message as a warning to no interfere with regular JSON output in stdout
    logger.warning('Application Insights \"%s\" was created for this Azure Spring Cloud. '
                   'You can visit https://portal.azure.com/#resource%s/overview to view your '
                   'Application Insights component', appinsights.name, appinsights.id)

    return appinsights.instrumentation_key
