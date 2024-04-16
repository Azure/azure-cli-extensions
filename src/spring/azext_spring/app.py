# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from datetime import datetime

# pylint: disable=wrong-import-order
from knack.log import get_logger
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import (ValidationError, ArgumentUsageError)
from .custom import app_get
from ._utils import (get_spring_sku, wait_till_end, convert_argument_to_parameter_list)
from ._deployment_factory import (deployment_selector,
                                  deployment_settings_options_from_resource,
                                  deployment_source_options_from_resource,
                                  default_deployment_create_options)
from ._app_factory import app_selector
from ._deployment_deployable_factory import deployable_selector
from ._app_validator import _get_active_deployment
from .custom import app_tail_log_internal
import datetime
from time import sleep
from .log_stream.log_stream_operations import log_stream_from_url

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
               deployment_name=None,
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
               bind_service_registry=None,
               bind_application_configuration_service=None,
               # app.update
               enable_persistent_storage=None,
               persistent_storage=None,
               assign_endpoint=None,
               enable_liveness_probe=None,
               enable_readiness_probe=None,
               enable_startup_probe=None,
               liveness_probe_config=None,
               readiness_probe_config=None,
               startup_probe_config=None,
               termination_grace_period_seconds=None,
               assign_public_endpoint=None,
               loaded_public_certificate_file=None,
               ingress_read_timeout=None,
               ingress_send_timeout=None,
               session_affinity=None,
               session_max_age=None,
               backend_protocol=None,
               client_auth_certs=None,
               # StandardGen2
               min_replicas=None,
               max_replicas=None,
               scale_rule_name=None,
               scale_rule_type=None,
               scale_rule_http_concurrency=None,
               scale_rule_metadata=None,
               scale_rule_auth=None,
               secrets=None,
               workload_profile=None):
    '''app_create
    Create app with an active deployment, deployment should be deployed with default banner
    1. Create app
    2. Create deployment with default banner
    3. [Optional] Update app properties which needs an active deployment exist
    '''
    logger.warning(LOG_RUNNING_PROMPT)
    _ensure_app_not_exist(client, resource_group, service, name)
    sku = get_spring_sku(client, resource_group, service)

    if sku.tier.upper() == 'STANDARDGEN2':
        if cpu is None and memory is None:
            cpu = '500m'
            memory = '1Gi'
    else:
        if cpu is None:
            cpu = 1
        if memory is None:
            memory = '1Gi'

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
        'bind_service_registry': bind_service_registry,
        'bind_application_configuration_service': bind_application_configuration_service,
        'enable_temporary_disk': True,
        'enable_persistent_storage': enable_persistent_storage,
        'persistent_storage': persistent_storage,
        'public': assign_endpoint,
        'public_for_vnet': assign_public_endpoint,
        'loaded_public_certificate_file': loaded_public_certificate_file,
        'ingress_read_timeout': ingress_read_timeout,
        'ingress_send_timeout': ingress_send_timeout,
        'session_affinity': session_affinity,
        'session_max_age': session_max_age,
        'backend_protocol': backend_protocol,
        'client_auth_certs': client_auth_certs,
        'secrets': secrets,
        'workload_profile_name': workload_profile
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
        'enable_liveness_probe': enable_liveness_probe,
        'enable_readiness_probe': enable_readiness_probe,
        'enable_startup_probe': enable_startup_probe,
        'liveness_probe_config_file_path': liveness_probe_config,
        'readiness_probe_config_file_path': readiness_probe_config,
        'startup_probe_config_file_path': startup_probe_config,
        'termination_grace_period_seconds': termination_grace_period_seconds,
        # StandardGen2
        'min_replicas': min_replicas,
        'max_replicas': max_replicas,
        'scale_rule_name': scale_rule_name,
        'scale_rule_type': scale_rule_type,
        'scale_rule_http_concurrency': scale_rule_http_concurrency,
        'scale_rule_metadata': scale_rule_metadata,
        'scale_rule_auth': scale_rule_auth,
    }

    deployable = deployable_selector(**create_deployment_kwargs, **basic_kwargs)
    create_deployment_kwargs['source_type'] = deployable.get_source_type(**create_deployment_kwargs, **basic_kwargs)
    create_deployment_kwargs['deployable_path'] = deployable.build_deployable_path(**create_deployment_kwargs, **basic_kwargs)
    deployment_factory = deployment_selector(**create_deployment_kwargs, **basic_kwargs)
    app_factory = app_selector(sku)
    deployment_factory.validate_instance_count(instance_count)

    app_resource = app_factory.format_resource(**create_app_kwargs, **basic_kwargs)
    banner_deployment_name = deployment_name or DEFAULT_DEPLOYMENT_NAME
    deployment_resource = deployment_factory.format_resource(**create_deployment_kwargs, **basic_kwargs)

    logger.warning('[1/2] Creating app {}'.format(name))
    app_poller = client.apps.begin_create_or_update(resource_group, service, name, app_resource)
    wait_till_end(cmd, app_poller)

    logger.warning('[2/2] Creating default deployment with name "{}"'.format(banner_deployment_name))
    poller = client.deployments.begin_create_or_update(resource_group,
                                                       service,
                                                       name,
                                                       banner_deployment_name,
                                                       deployment_resource)
    wait_till_end(cmd, poller)
    logger.warning('App create succeeded')
    return app_get(cmd, client, resource_group, service, name)


def app_update(cmd, client, resource_group, service, name,
               deployment=None,  # set by validator
               # app
               assign_endpoint=None,
               assign_public_endpoint=None,
               enable_persistent_storage=None,
               enable_ingress_to_app_tls=None,
               https_only=None,
               persistent_storage=None,
               loaded_public_certificate_file=None,
               ingress_read_timeout=None,
               ingress_send_timeout=None,
               session_affinity=None,
               session_max_age=None,
               backend_protocol=None,
               client_auth_certs=None,
               workload_profile=None,
               # deployment.source
               runtime_version=None,
               jvm_options=None,
               main_entry=None,
               # deployment.settings
               env=None,
               disable_probe=None,
               config_file_patterns=None,
               enable_liveness_probe=None,
               enable_readiness_probe=None,
               enable_startup_probe=None,
               liveness_probe_config=None,
               readiness_probe_config=None,
               startup_probe_config=None,
               termination_grace_period_seconds=None,
               secrets=None,
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
        'sku': deployment.sku if deployment else get_spring_sku(client, resource_group, service),
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
        'source_type': deployment.properties.source.type if deployment else None,
        'enable_liveness_probe': enable_liveness_probe,
        'enable_readiness_probe': enable_readiness_probe,
        'enable_startup_probe': enable_startup_probe,
        'liveness_probe_config_file_path': liveness_probe_config,
        'readiness_probe_config_file_path': readiness_probe_config,
        'startup_probe_config_file_path': startup_probe_config,
        'termination_grace_period_seconds': termination_grace_period_seconds,
    }

    app_kwargs = {
        'public': assign_endpoint,
        'public_for_vnet': assign_public_endpoint,
        'enable_persistent_storage': enable_persistent_storage,
        'persistent_storage': persistent_storage,
        'loaded_public_certificate_file': loaded_public_certificate_file,
        'enable_end_to_end_tls': enable_ingress_to_app_tls,
        'https_only': https_only,
        'ingress_read_timeout': ingress_read_timeout,
        'ingress_send_timeout': ingress_send_timeout,
        'session_affinity': session_affinity,
        'session_max_age': session_max_age,
        'backend_protocol': backend_protocol,
        'client_auth_certs': client_auth_certs,
        'secrets': secrets,
        'workload_profile_name': workload_profile
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
               server_version=None,
               jvm_options=None,
               main_entry=None,
               container_image=None,
               container_registry=None,
               registry_username=None,
               registry_password=None,
               container_command=None,
               container_args=None,
               language_framework=None,
               build_env=None,
               builder=None,
               build_cpu=None,
               build_memory=None,
               # deployment.settings
               env=None,
               apms=None,
               build_certificates=None,
               disable_probe=None,
               config_file_patterns=None,
               enable_liveness_probe=None,
               enable_readiness_probe=None,
               enable_startup_probe=None,
               liveness_probe_config=None,
               readiness_probe_config=None,
               startup_probe_config=None,
               termination_grace_period_seconds=None,
               disable_app_log=False,
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
        'apms': apms,
        'build_certificates': build_certificates,
        'runtime_version': runtime_version,
        'server_version': server_version,
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
        'language_framework': language_framework,
        'build_env': build_env,
        'build_cpu': build_cpu,
        'build_memory': build_memory,
        'builder': builder,
        'enable_liveness_probe': enable_liveness_probe,
        'enable_readiness_probe': enable_readiness_probe,
        'enable_startup_probe': enable_startup_probe,
        'liveness_probe_config_file_path': liveness_probe_config,
        'readiness_probe_config_file_path': readiness_probe_config,
        'startup_probe_config_file_path': startup_probe_config,
        'termination_grace_period_seconds': termination_grace_period_seconds,
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
    poller = sdk_no_wait(no_wait, deployment_factory.get_deploy_method(**kwargs),
                         resource_group, service, name, deployment.name,
                         deployment_resource)
    if not disable_app_log:
        # We will wait for the poller to be done to print the deploy process
        _print_deploy_process(client, poller, resource_group, service, name, deployment.name)
        _log_application(cmd, client, no_wait, poller, resource_group, service, name, deployment.name)
    if "succeeded" != poller.status().lower():
        return poller
    return client.deployments.get(resource_group, service, name, deployment.name)


def _log_application(cmd, client, no_wait, poller, resource_group, service, app_name, deployment_name):
    if no_wait:
        return
    deployment_error = None
    try:
        poller.result()
    except Exception as err:
        deployment_error = err
    try:
        deployment_resource = client.deployments.get(resource_group, service, app_name, deployment_name)
        instances = deployment_resource.properties.instances
        start_time = instances[0].start_time
        instance_name = instances[0].name

        # print the newly created instance log
        for temp_instance in instances:
            if temp_instance.start_time > start_time:
                start_time = temp_instance.start_time
                instance_name = temp_instance.name

        logger.warning('Application logs:')
        # For failed deployment we need to print logs as much as possible, we use follow=true to print enough logs
        # for troubleshooting. We add a timeout to force stop logs then the cli can be exited.
        app_tail_log_internal(cmd, client, resource_group, service, app_name, deployment_resource, instance_name,
                              follow=False if deployment_error is None else True, lines=500, limit=1024 * 1024,
                              since=300, timeout=10, get_app_log=_get_app_log_deploy_phase)
    except Exception:
        # ignore
        pass
    if deployment_error:
        raise deployment_error


def _print_deploy_process(client, poller, resource_group, service, app_name, deployment_name):
    try:
        deployment_resource = _get_deployment_ignore_exception(client, resource_group, service, app_name,
                                                               deployment_name)
        if deployment_resource is not None:
            instance_count = deployment_resource.sku.capacity
            rolling_number = max(1, instance_count // 4)
            rounds = int(instance_count // rolling_number + 0 if instance_count % rolling_number == 0 else 1)

            if instance_count > 1:
                instance_desc = str(instance_count) + " instances"
                rounds_desc = str(rounds) + " rounds"
            else:
                instance_desc = str(instance_count) + " instance"
                rounds_desc = str(rounds) + " round"
            logger.warning('Azure Spring Apps will use rolling upgrade to update your deployment, you have {}, '
                           'Azure Spring Apps will update the deployment in {}.'.format(instance_desc, rounds_desc))
            last_round = 0

            deployment_time = deployment_resource.system_data.last_modified_at.strftime("%Y-%m-%dT%H:%M:%S%z")
            while not poller.done():
                deployment_resource = _get_deployment_ignore_exception(client, resource_group, service, app_name,
                                                                       deployment_name)
                if deployment_resource is not None:
                    instances = deployment_resource.properties.instances
                    new_instance_count = 0
                    for temp_instance in instances:
                        if temp_instance.start_time > deployment_time:
                            new_instance_count += 1
                    instance_round = instance_count // rounds
                    current_round = new_instance_count // instance_round + (0 if new_instance_count % instance_round == 0 else 1)
                    if current_round != last_round:
                        if int(current_round) > 1:
                            old_desc = "{} old instances are".format(int(new_instance_count))
                        else:
                            old_desc = "{} old instance is".format(int(new_instance_count))
                        if int(new_instance_count) > 1:
                            new_desc = "{} new instances are".format(int(new_instance_count))
                        else:
                            new_desc = "{} new instance is".format(int(new_instance_count))
                        logger.warning(
                            'The deployment is in round {}, {} deleted/deleting and {} '
                            'started/starting'.format(int(current_round), old_desc, new_desc))
                        last_round = current_round
                sleep(5)
            logger.warning("Your application is successfully deployed.")
    except Exception:
        pass


def _get_deployment_ignore_exception(client, resource_group, service, app_name, deployment_name):
    try:
        return client.deployments.get(resource_group, service, app_name, deployment_name)
    except Exception:
        pass


def _get_app_log_deploy_phase(url, auth, format_json, exceptions):
    try:
        log_stream_from_url(url, auth, format_json, exceptions, chunk_size=10 * 1024, stderr=True)
    except Exception:
        pass


def deployment_create(cmd, client, resource_group, service, app, name,
                      disable_validation=None,
                      # deployment.source
                      version=None,
                      artifact_path=None,
                      source_path=None,
                      target_module=None,
                      runtime_version=None,
                      server_version=None,
                      jvm_options=None,
                      main_entry=None,
                      container_image=None,
                      container_registry=None,
                      registry_username=None,
                      registry_password=None,
                      container_command=None,
                      container_args=None,
                      language_framework=None,
                      build_env=None,
                      builder=None,
                      # deployment.settings
                      skip_clone_settings=False,
                      cpu=None,
                      memory=None,
                      instance_count=None,
                      env=None,
                      apms=None,
                      build_certificates=None,
                      disable_probe=None,
                      config_file_patterns=None,
                      enable_liveness_probe=None,
                      enable_readiness_probe=None,
                      enable_startup_probe=None,
                      liveness_probe_config=None,
                      readiness_probe_config=None,
                      startup_probe_config=None,
                      termination_grace_period_seconds=None,
                      disable_app_log=False,
                      # StandardGen2
                      min_replicas=None,
                      max_replicas=None,
                      scale_rule_name=None,
                      scale_rule_type=None,
                      scale_rule_http_concurrency=None,
                      scale_rule_metadata=None,
                      scale_rule_auth=None,
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
        'apms': apms,
        'build_certificates': build_certificates,
        'runtime_version': runtime_version,
        'server_version': server_version,
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
        'language_framework': language_framework,
        'cpu': cpu,
        'memory': memory,
        'instance_count': instance_count,
        'build_env': build_env,
        'builder': builder,
        'enable_liveness_probe': enable_liveness_probe,
        'enable_readiness_probe': enable_readiness_probe,
        'enable_startup_probe': enable_startup_probe,
        'liveness_probe_config_file_path': liveness_probe_config,
        'readiness_probe_config_file_path': readiness_probe_config,
        'startup_probe_config_file_path': startup_probe_config,
        'termination_grace_period_seconds': termination_grace_period_seconds,
        # StandardGen2
        'min_replicas': min_replicas,
        'max_replicas': max_replicas,
        'scale_rule_name': scale_rule_name,
        'scale_rule_type': scale_rule_type,
        'scale_rule_http_concurrency': scale_rule_http_concurrency,
        'scale_rule_metadata': scale_rule_metadata,
        'scale_rule_auth': scale_rule_auth,
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
    poller = sdk_no_wait(no_wait, client.deployments.begin_create_or_update,
                         resource_group, service, app, name,
                         deployment_resource)
    if not disable_app_log:
        _log_application(cmd, client, no_wait, poller, resource_group, service, app, name)
    if "succeeded" != poller.status().lower():
        return poller
    return client.deployments.get(resource_group, service, app, name)


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
        options['sku'] = get_spring_sku(client, resource_group, service)

    # For StandardGen2, if skip the deployment settings clone and don't input any value for CPU and memory, will use default value
    if options['sku'].tier.upper() == 'STANDARDGEN2' and skip_clone_settings and kwargs['cpu'] is None and kwargs['memory'] is None:
        options['cpu'] = '500m'
        options['memory'] = '1Gi'

    options.update({k: v for k, v in kwargs.items() if v})
    return options
