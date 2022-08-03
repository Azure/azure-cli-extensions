# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from azure.cli.core.azclierror import InvalidArgumentValueError
from .vendored_sdks.appplatform.v2022_01_01_preview import models
from ._deployment_source_factory import source_selector


APPLICATION_CONFIGURATION_SERVICE_NAME = "applicationConfigurationService"
APPLICATION_CONFIGURATION_SERVICE_PROPERTY_PATTERN = "configFilePatterns"


class DefaultDeployment:
    def __init__(self, **kwargs):
        self.source_factory = source_selector(**kwargs)

    def validate_instance_count(self, instance_count):
        if instance_count < 1 or instance_count > 500:
            raise InvalidArgumentValueError('Invalid --instance-count, should be in range [1, 500]')

    def format_resource(self, sku=None, instance_count=None, active=None, **kwargs):
        sku.capacity = instance_count
        return models.DeploymentResource(
            properties=models.DeploymentResourceProperties(
                active=active,
                source=self.format_source(**kwargs),
                deployment_settings=self.format_settings(**kwargs)
            ),
            sku=sku
        )

    def format_settings(self, **kwargs):
        return models.DeploymentSettings(
            resource_requests=self._format_resource_request(**kwargs),
            container_probe_settings=self._format_container_probe(**kwargs),
            environment_variables=self._get_env(**kwargs),
            addon_configs=self._get_addon_configs(**kwargs)
        )

    def _format_container_probe(self, disable_probe=None, **_):
        if disable_probe is None:
            return None
        return models.ContainerProbeSettings(
            disable_probe=disable_probe
        )

    def _format_resource_request(self, cpu=None, memory=None, **_):
        if not cpu and not memory:
            return None
        return models.ResourceRequests(
            cpu=cpu,
            memory=memory
        )

    def _get_env(self, env=None, **_):
        return env

    def _get_addon_configs(self, config_file_patterns=None, **_):
        if config_file_patterns is not None:
            addon_configs = {
                APPLICATION_CONFIGURATION_SERVICE_NAME: {
                    APPLICATION_CONFIGURATION_SERVICE_PROPERTY_PATTERN: config_file_patterns
                }
            }
            return addon_configs
        return None

    def format_source(self, **kwargs):
        return self.source_factory.format_source(**kwargs)

    def get_fulfill_options(self, deployment_resource, **kwargs):
        '''
        If the required method is PUT, should put the properties on original deployment back.
        '''
        options = deployment_settings_options_from_resource(deployment_resource) \
            if self.require_put_method(deployment_resource, **kwargs) else {}
        options.update({k: v for k, v in kwargs.items() if v})
        return options

    def get_update_backfill_options(self, **kwargs):
        source_options = self.source_factory.fulfilled_options_from_original_source_info(**kwargs)
        settings_options = self._backfill_settings(**kwargs)
        return {**source_options, **settings_options}

    def _backfill_settings(self, **_):
        return {}

    def get_deploy_method(self, client, **kwargs):
        if self.require_put_method(**kwargs):
            return client.deployments.begin_create_or_update
        return client.deployments.begin_update

    def require_put_method(self, deployment_resource, source_type, **_):
        '''
        If properties.source.type is changed from or to 'Container'.
        The method must be PUT.
        '''
        return 'Container' in [source_type, deployment_resource.properties.source.type] and \
               deployment_resource.properties.source.type != source_type


class EnterpriseDeployment(DefaultDeployment):
    def _get_env(self, env, jvm_options, **_):
        if jvm_options is None:
            return env
        env = env or {}
        if jvm_options:
            env['JAVA_OPTS'] = jvm_options
        else:
            env.pop('JAVA_OPTS', None)
        return env

    def _backfill_settings(self, deployment_resource=None, env=None, jvm_options=None, **_):
        if jvm_options is None or env is not None:
            return {}
        return {'env': deployment_resource.properties.deployment_settings.environment_variables}


class BasicTierDeployment(DefaultDeployment):
    def validate_instance_count(self, instance_count):
        if instance_count < 1 or instance_count > 25:
            raise InvalidArgumentValueError('Invalid --instance-count, should be in range [1, 25]')


def deployment_selector(**kwargs):
    sku = kwargs.get('sku', None)
    if sku.name == 'E0':
        return EnterpriseDeployment(**kwargs)
    if sku.name == 'B0':
        return BasicTierDeployment(**kwargs)
    return DefaultDeployment(**kwargs)


def deployment_settings_options_from_resource(original):
    '''
    Construct the options about deployment settings from original resource.
    '''
    options = {
        'cpu': original.properties.deployment_settings.resource_requests.cpu,
        'memory': original.properties.deployment_settings.resource_requests.memory,
        'instance_count': original.sku.capacity,
        'sku': original.sku,
        'env': original.properties.deployment_settings.environment_variables,
        'config_file_patterns': _get_origin_config_file_patterns(original.properties.deployment_settings.addon_configs)
    }
    if original.properties.deployment_settings.container_probe_settings is not None:
        options['disable_probe'] = original.properties.deployment_settings.container_probe_settings.disable_probe
    return options


def _get_origin_config_file_patterns(origin_addon_configs):
    if origin_addon_configs:
        acs_addon = origin_addon_configs.get(APPLICATION_CONFIGURATION_SERVICE_NAME)
        return acs_addon.get(APPLICATION_CONFIGURATION_SERVICE_PROPERTY_PATTERN) if acs_addon is not None else None
    return None


def deployment_source_options_from_resource(original):
    '''
    Construct the options about deployment source from original resource.
    '''
    options = {}
    if hasattr(original.properties.source, 'jvm_options'):
        options['jvm_options'] = original.properties.source.jvm_options
    if hasattr(original.properties.source, 'runtime_version'):
        options['runtime_version'] = original.properties.source.runtime_version
    return options


def default_deployment_create_options():
    '''
    Construct the default options for deployment creation.
    TODO This is currently used for staging deployment creation when --skip-clone-settings set.
    Putting it to validator and fulfill the command args makes more sense.
    '''
    return {
        'cpu': '1',
        'memory': '1Gi',
        'runtime_version': 'Java_8',
        'instance_count': 1,
        'env': {},
        'sku': None,
        'disable_probe': None
    }
