# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import get_file_json
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from ._deployment_source_factory import source_selector
from .custom import format_scale


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
            apms=self._get_apms(**kwargs),
            addon_configs=self._get_addon_configs(**kwargs),
            termination_grace_period_seconds=self._get_termination_grace_period_seconds(**kwargs),
            startup_probe=self._format_startup_probe(**kwargs),
            liveness_probe=self._format_liveness_probe(**kwargs),
            readiness_probe=self._format_readiness_probe(**kwargs),
            scale=format_scale(**kwargs),
        )

    def _get_termination_grace_period_seconds(self, termination_grace_period_seconds=None, **_):
        if termination_grace_period_seconds is None:
            return None
        return termination_grace_period_seconds

    def _format_startup_probe(self, enable_startup_probe=None, startup_probe_config_file_path=None, **_):
        if enable_startup_probe is None:
            return None

        if not enable_startup_probe:
            return models.Probe(disable_probe=True)

        probe = self._load_probe_config(startup_probe_config_file_path)
        return probe

    def _format_liveness_probe(self, enable_liveness_probe=None, liveness_probe_config_file_path=None, **_):
        if enable_liveness_probe is None:
            return None

        if not enable_liveness_probe:
            return models.Probe(disable_probe=True)

        probe = self._load_probe_config(liveness_probe_config_file_path)
        return probe

    def _format_readiness_probe(self, enable_readiness_probe=None, readiness_probe_config_file_path=None, **_):
        if enable_readiness_probe is None:
            return None

        if not enable_readiness_probe:
            return models.Probe(disable_probe=True)

        probe = self._load_probe_config(readiness_probe_config_file_path)
        return probe

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

    def _get_apms(self, apms=None, **_):
        return apms

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

    def _load_probe_config(self, probe_config=None, **_):
        if not probe_config:
            return
        data = get_file_json(probe_config, throw_on_empty=False)
        if not data:
            return

        if not data.get('probe'):
            raise InvalidArgumentValueError("Probe must be provided in the json file")

        invalidProperties = not data['probe'].get('probeAction') or \
            not data['probe'].get('probeAction').get('type')
        if invalidProperties:
            raise InvalidArgumentValueError("probeAction, Type mast be provided in the json file")
        probe_action = None
        if data['probe']['probeAction']['type'].casefold() == "HTTPGetAction".casefold():
            probe_action = models.HTTPGetAction(
                type="HTTPGetAction",
                path=data['probe']['probeAction']['path'] if 'path' in data['probe']['probeAction'] else None,
                scheme=data['probe']['probeAction']['scheme'] if 'scheme' in data['probe']['probeAction'] else None,
            )
        elif data['probe']['probeAction']['type'].casefold() == "TCPSocketAction".casefold():
            probe_action = models.TCPSocketAction(
                type="TCPSocketAction",
            )
        elif data['probe']['probeAction']['type'].casefold() == "ExecAction".casefold():
            probe_action = models.ExecAction(
                type="ExecAction",
                command=data['probe']['probeAction']['command'] if 'command' in data['probe']['probeAction'] else None,
            )
        else:
            raise InvalidArgumentValueError("ProbeAction.Type is invalid")
        probe_settings = models.Probe(
            probe_action=probe_action,
            disable_probe=False,
            initial_delay_seconds=data['probe']['initialDelaySeconds'] if 'initialDelaySeconds' in data['probe'] else None,
            period_seconds=data['probe']['periodSeconds'] if 'periodSeconds' in data['probe'] else None,
            timeout_seconds=data['probe']['timeoutSeconds'] if 'timeoutSeconds' in data['probe'] else None,
            failure_threshold=data['probe']['failureThreshold'] if 'failureThreshold' in data['probe'] else None,
            success_threshold=data['probe']['successThreshold'] if 'successThreshold' in data['probe'] else None
        )

        return probe_settings


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

    def validate_instance_count(self, instance_count):
        if instance_count < 1 or instance_count > 1000:
            raise InvalidArgumentValueError('Invalid --instance-count, should be in range [1, 1000]')


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
    if hasattr(original.properties.source, 'server_version'):
        options['server_version'] = original.properties.source.server_version
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
        'runtime_version': 'Java_11',
        'instance_count': 1,
        'env': {},
        'sku': None,
        'disable_probe': None
    }
