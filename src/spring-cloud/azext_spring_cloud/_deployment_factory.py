# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from azure.cli.core.azclierror import InvalidArgumentValueError
from .vendored_sdks.appplatform.v2022_01_01_preview import models
from ._deployment_source_factory import source_selector


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
            environment_variables=self._get_env(**kwargs)
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

    def _get_env(self, env, **_):
        return env

    def format_source(self, **kwargs):
        return self.source_factory.format_source(**kwargs)

    def get_fulfill_options(self, deployment_resource, **kwargs):
        '''
        If the required method is PUT, should put the properties on original deployment back.
        '''
        options = {}
        if self.require_put_method(deployment_resource, **kwargs):
            return options_settings_assign_from(options, deployment_resource)
        options.update({k: v for k, v in kwargs.items() if v})
        return options

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
        if not jvm_options:
            return env
        env = env or {}
        env['JAVA_OPTS'] = jvm_options
        return env


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


def options_assign_from(options, original):
    options = options_settings_assign_from(options, original)
    return options_source_assign_from(options, original)


def options_settings_assign_from(options, original):
    options['cpu'] = original.properties.deployment_settings.resource_requests.cpu
    options['memory'] = original.properties.deployment_settings.resource_requests.memory
    options['instance_count'] = original.sku.capacity
    options['sku'] = original.sku
    options['env'] = original.properties.deployment_settings.environment_variables
    if original.properties.deployment_settings.container_probe_settings is not None:
        options['disable_probe'] = original.properties.deployment_settings.container_probe_settings.disable_probe
    return options


def options_source_assign_from(options, original):
    if hasattr(original.properties.source, 'jvm_options'):
        options['jvm_options'] = original.properties.source.jvm_options
    if hasattr(original.properties.source, 'runtime_version'):
        options['runtime_version'] = original.properties.source.runtime_version
    return options
