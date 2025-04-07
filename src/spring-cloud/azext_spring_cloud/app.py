# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from knack.log import get_logger
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import (ValidationError, ArgumentUsageError)
from .custom import app_get
from ._utils import (get_spring_cloud_sku, wait_till_end, convert_argument_to_parameter_list)
from ._deployment_factory import (deployment_selector,
                                  deployment_settings_options_from_resource,
                                  deployment_source_options_from_resource,
                                  default_deployment_create_options)
from ._app_factory import app_selector
from ._deployment_deployable_factory import deployable_selector
from ._app_validator import _get_active_deployment


logger = get_logger(__name__)
DEFAULT_DEPLOYMENT_NAME = "default"

# pylint: disable=line-too-long
LOG_RUNNING_PROMPT = "This command usually takes minutes to run. Add '--verbose' parameter if needed."

#  App's command usually operates an Spring/Apps and the active Spring/Apps/Deployments under the app.
# The general idea of these command is putting all input command in parameter dict and let the Resource factory to construct the payload.
# - _app_factory construct the App's properties
# - _deployment_factory construct the Deployment's properties, which includes source and other settings.
# - There are 5 types for different deployment source types, here use _deployment_source_factory to construct the payload according to the source_type
# - A deployment must consume a path can be deployable, it can be a relative path, custom container or build result resource id,
#   - _deployment_deployable_factory determines the deployable type and upload necessary binary/code to the service when constructing the deployable_path.
#   - _deployment_uploadable_factory will upload the local file to a given destination, or compress the local folder and upload according to the parameter.


def app_create(cmd, client, resource_group, service, name,
               # deployment.settings
               cpu=None,
               memory=None,
               instance_count=None,
               disable_probe=None,
               env=None,
               # deployment.source
               runtime_version=None,
               jvm_options=None,
               # app.create
               assign_identity=None,
               system_assigned=None,
               user_assigned=None,
               # app.update
               enable_persistent_storage=None,
               persistent_storage=None,
               assign_endpoint=None,
               loaded_public_certificate_file=None):
    '''app_create
    Create app with an active deployment, deployment should be deployed with default banner
    1. Create app
    2. Create deployment with default banner
    3. [Optional] Update app properties which needs an active deployment exist
    '''
    logger.warning(LOG_RUNNING_PROMPT)
    _ensure_app_not_exist(client, resource_group, service, name)
    sku = get_spring_cloud_sku(client, resource_group, service)
    basic_kwargs = {
        'cmd': cmd,
        'client': client,
        'resource_group': resource_group,
        'service': service,
        'app': name,
        'deployment': 'default',
        'sku': sku
    }

    create_app_kwargs = {
        'system_assigned': system_assigned,
        'user_assigned': user_assigned,
        'enable_temporary_disk': True,
        'enable_persistent_storage': enable_persistent_storage,
        'persistent_storage': persistent_storage,
        'public': assign_endpoint,
        'loaded_public_certificate_file': loaded_public_certificate_file
    }
    create_deployment_kwargs = {
        'cpu': cpu,
        'memory': memory,
        'instance_count': instance_count,
        'active': True,
        'disable_probe': disable_probe,
        'env': env,
        'runtime_version': runtime_version,
        'jvm_options': jvm_options,
    }
    update_app_kwargs = {
        'enable_persistent_storage': enable_persistent_storage,
        'public': assign_endpoint,
    }

    deployable = deployable_selector(**create_deployment_kwargs, **basic_kwargs)
    create_deployment_kwargs['source_type'] = deployable.get_source_type(**create_deployment_kwargs, **basic_kwargs)
    create_deployment_kwargs['deployable_path'] = deployable.build_deployable_path(**create_deployment_kwargs, **basic_kwargs)
    deployment_factory = deployment_selector(**create_deployment_kwargs, **basic_kwargs)
    app_factory = app_selector(sku)
    deployment_factory.validate_instance_count(instance_count)

    app_resource = app_factory.format_resource(**create_app_kwargs, **basic_kwargs)
    logger.warning('[1/3] Creating app {}'.format(name))
    app_poller = client.apps.begin_create_or_update(resource_group, service, name, app_resource)
    wait_till_end(cmd, app_poller)

    logger.warning('[2/3] Creating default deployment with name "{}"'.format(DEFAULT_DEPLOYMENT_NAME))
    deployment_resource = deployment_factory.format_resource(**create_deployment_kwargs, **basic_kwargs)
    poller = client.deployments.begin_create_or_update(resource_group,
                                                       service,
                                                       name,
                                                       DEFAULT_DEPLOYMENT_NAME,
                                                       deployment_resource)
    logger.warning('[3/3] Updating app "{}" (this operation can take a while to complete)'.format(name))
    app_resource = app_factory.format_resource(**update_app_kwargs, **basic_kwargs)
    app_poller = client.apps.begin_update(resource_group, service, name, app_resource)

    wait_till_end(cmd, poller, app_poller)
    logger.warning('App create succeeded')
    return app_get(cmd, client, resource_group, service, name)


def app_update(cmd, client, resource_group, service, name,
               deployment=None,  # set by validator
               # app
               assign_endpoint=None,
               enable_persistent_storage=None,
               enable_ingress_to_app_tls=None,
               https_only=None,
               persistent_storage=None,
               loaded_public_certificate_file=None,
               # deployment.source
               runtime_version=None,
               jvm_options=None,
               main_entry=None,
               # deployment.settings
               env=None,
               disable_probe=None,
               config_file_patterns=None,
               # general
               no_wait=False):
    '''app_update
    Update app and active deployment according to the input
    1. Update app
    2. Update deployment
    '''
    logger.warning(LOG_RUNNING_PROMPT)
    basic_kwargs = {
        'cmd': cmd,
        'client': client,
        'resource_group': resource_group,
        'service': service,
        'app': name,
        'sku': deployment.sku if deployment else get_spring_cloud_sku(client, resource_group, service),
        'deployment': deployment.name if deployment else None,
        'deployment_resource': deployment,
    }

    deployment_kwargs = {
        'disable_probe': disable_probe,
        'config_file_patterns': config_file_patterns,
        'env': env,
        'runtime_version': runtime_version,
        'jvm_options': jvm_options,
        'main_entry': main_entry,
        'source_type': deployment.properties.source.type if deployment else None
    }

    app_kwargs = {
        'public': assign_endpoint,
        'enable_persistent_storage': enable_persistent_storage,
        'persistent_storage': persistent_storage,
        'loaded_public_certificate_file': loaded_public_certificate_file,
        'enable_end_to_end_tls': enable_ingress_to_app_tls,
        'https_only': https_only,
    }

    if deployment is None:
        updated_deployment_kwargs = {k: v for k, v in deployment_kwargs.items() if v}
        if updated_deployment_kwargs:
            raise ArgumentUsageError('{} cannot be set when there is no active deployment.'
                                     .format(convert_argument_to_parameter_list(updated_deployment_kwargs.keys())))

    deployment_factory = deployment_selector(**deployment_kwargs, **basic_kwargs)
    app_factory = app_selector(**basic_kwargs)
    deployment_kwargs.update(deployment_factory.get_update_backfill_options(**deployment_kwargs, **basic_kwargs))

    app_resource = app_factory.format_resource(**app_kwargs, **basic_kwargs)
    deployment_factory.source_factory.validate_source(**deployment_kwargs, **basic_kwargs)
    deployment_resource = deployment_factory.format_resource(**deployment_kwargs, **basic_kwargs)

    pollers = [
        client.apps.begin_update(resource_group, service, name, app_resource)
    ]
    if deployment:
        pollers.append(client.deployments.begin_update(resource_group,
                                                       service,
                                                       name,
                                                       deployment.name,
                                                       deployment_resource))
    if no_wait:
        return
    wait_till_end(cmd, *pollers)
    return app_get(cmd, client, resource_group, service, name)


def app_deploy(cmd, client, resource_group, service, name,
               deployment=None,  # set by validator
               # only used in validator
               disable_validation=None,
               # deployment.source
               version=None,
               artifact_path=None,
               source_path=None,
               target_module=None,
               runtime_version=None,
               jvm_options=None,
               main_entry=None,
               container_image=None,
               container_registry=None,
               registry_username=None,
               registry_password=None,
               container_command=None,
               container_args=None,
               build_env=None,
               builder=None,
               # deployment.settings
               env=None,
               disable_probe=None,
               config_file_patterns=None,
               # general
               no_wait=False):
    '''app_deploy
    Deploy the local file or container image to the given deployment
    1. Prepare the deployable path for deployment which can be apply to deployment.source
        - [BYOC] construct DeploymentResourceSource directly
        - [Enterprise] Format a BuildResult user info
        - [Source Code for Standard] Compress and Upload
        - [Others] Upload
    2. Prepare the Deployment Source
    2. Update Deployment resource
    '''
    logger.warning(LOG_RUNNING_PROMPT)
    kwargs = {
        'cmd': cmd,
        'client': client,
        'resource_group': resource_group,
        'service': service,
        'app': name,
        'deployment': deployment.name,
        'deployment_resource': deployment,
        'sku': deployment.sku,
        'disable_probe': disable_probe,
        'config_file_patterns': config_file_patterns,
        'env': env,
        'runtime_version': runtime_version,
        'jvm_options': jvm_options,
        'main_entry': main_entry,
        'version': version,
        'artifact_path': artifact_path,
        'source_path': source_path,
        'target_module': target_module,
        'container_image': container_image,
        'container_registry': container_registry,
        'registry_username': registry_username,
        'registry_password': registry_password,
        'container_command': container_command,
        'container_args': container_args,
        'build_env': build_env,
        'builder': builder,
        'no_wait': no_wait
    }

    # inherit source type or runtime version from the existing deployment if not specified in command.
    orginal_source_options = deployment_source_options_from_resource(deployment)
    orginal_source_options.update({k: v for k, v in kwargs.items() if v})
    kwargs.update(orginal_source_options)

    deploy = deployable_selector(**kwargs)
    kwargs['source_type'] = deploy.get_source_type(**kwargs)
    kwargs['total_steps'] = deploy.get_total_deploy_steps(**kwargs)
    kwargs['deployable_path'] = deploy.build_deployable_path(**kwargs)

    deployment_factory = deployment_selector(**kwargs)
    kwargs.update(deployment_factory.get_fulfill_options(**kwargs))
    deployment_resource = deployment_factory.format_resource(**kwargs)
    logger.warning('[{}/{}] Updating deployment in app "{}" (this operation can take a '
                   'while to complete)'.format(kwargs['total_steps'],
                                               kwargs['total_steps'],
                                               name))
    return sdk_no_wait(no_wait, deployment_factory.get_deploy_method(**kwargs),
                       resource_group, service, name, deployment.name,
                       deployment_resource)


def deployment_create(cmd, client, resource_group, service, app, name,
                      disable_validation=None,
                      # deployment.source
                      version=None,
                      artifact_path=None,
                      source_path=None,
                      target_module=None,
                      runtime_version=None,
                      jvm_options=None,
                      main_entry=None,
                      container_image=None,
                      container_registry=None,
                      registry_username=None,
                      registry_password=None,
                      container_command=None,
                      container_args=None,
                      build_env=None,
                      builder=None,
                      # deployment.settings
                      skip_clone_settings=False,
                      cpu=None,
                      memory=None,
                      instance_count=None,
                      env=None,
                      disable_probe=None,
                      config_file_patterns=None,
                      # general
                      no_wait=False):
    '''deployment_create
    Create a deployment under app as in-active
    1. Copy settings from active deployment if --skip-clone-settings not set
    2. Prepare the Deployment.Source
        - Prepare default user source info
        - [BYOC] construct DeploymentResourceSource directly
        - [Enterprise] Format a BuildResult user info
        - [Source Code for Standard] Compress and Upload
        - [Others] Upload
    3. Create Deployment resource
    '''
    kwargs = {
        'cmd': cmd,
        'client': client,
        'resource_group': resource_group,
        'service': service,
        'app': app,
        'deployment': name,
        'disable_probe': disable_probe,
        'config_file_patterns': config_file_patterns,
        'env': env,
        'runtime_version': runtime_version,
        'jvm_options': jvm_options,
        'main_entry': main_entry,
        'version': version,
        'artifact_path': artifact_path,
        'source_path': source_path,
        'target_module': target_module,
        'container_image': container_image,
        'container_registry': container_registry,
        'registry_username': registry_username,
        'registry_password': registry_password,
        'container_command': container_command,
        'container_args': container_args,
        'cpu': cpu,
        'memory': memory,
        'instance_count': instance_count,
        'build_env': build_env,
        'builder': builder,
        'no_wait': no_wait
    }

    kwargs.update(_fulfill_deployment_creation_options(skip_clone_settings, **kwargs))

    deploy = deployable_selector(**kwargs)
    kwargs['source_type'] = deploy.get_source_type(**kwargs)
    kwargs['total_steps'] = deploy.get_total_deploy_steps()
    kwargs['deployable_path'] = deploy.build_deployable_path(**kwargs)
    deployment_factory = deployment_selector(**kwargs)
    deployment_resource = deployment_factory.format_resource(**kwargs)
    logger.warning('[{}/{}] Creating deployment in app "{}" (this operation can take a '
                   'while to complete)'.format(kwargs['total_steps'],
                                               kwargs['total_steps'],
                                               app))
    return sdk_no_wait(no_wait, client.deployments.begin_create_or_update,
                       resource_group, service, app, name,
                       deployment_resource)


def _ensure_app_not_exist(client, resource_group, service, name):
    app = None
    try:
        app = client.apps.get(resource_group, service, name)
    except Exception:
        # ignore
        return
    if app:
        raise ValidationError('App {} already exist.'.format(app.id))


def _fulfill_deployment_creation_options(skip_clone_settings, client, resource_group, service, app, **kwargs):
    options = default_deployment_create_options()
    if not skip_clone_settings:
        active_deployment = _get_active_deployment(client, resource_group, service, app)
        if not active_deployment:
            logger.warning('No production deployment found, use --skip-clone-settings to skip copying settings from '
                           'production deployment.')
        else:
            options.update(deployment_settings_options_from_resource(active_deployment))
            options.update(deployment_source_options_from_resource(active_deployment))
    if not options.get('sku', None):
        options['sku'] = get_spring_cloud_sku(client, resource_group, service)
    options.update({k: v for k, v in kwargs.items() if v})
    return options
