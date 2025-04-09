# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base_converter import BaseConverter
from knack.log import get_logger

logger = get_logger(__name__)


# Concrete Converter Subclass for Config Server
class ConfigServerConverter(BaseConverter):

    CONFIGURATION_KEY_PREFIX = "spring.cloud.config.server.git"
    KEY_URI = ".uri"
    KEY_LABEL = ".default-label"
    KEY_SEARCH_PATHS = ".search-paths"
    KEY_USERNAME = ".username"
    KEY_PASSWORD = ".password"
    KEY_PRIVATE_KEY = ".private-key"
    KEY_HOST_KEY = ".host-key"
    KEY_HOST_KEY_ALGORITHM = ".host-key-algorithm"
    KEY_PATTERN = ".pattern"

    def __init__(self, source):
        def transform_data():
            if self.wrapper_data.is_support_ossconfigserver():
                configServer = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/configServers')[0]
                name = "config"
                configurations, params = self._get_configurations_and_params(configServer)
                replicas = 2
                return {
                    "configServerName": name,
                    "params": params,
                    "configurations": configurations,
                    "replicas": replicas
                }
            else:
                return None
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "config_server.bicep"

    def _get_configurations_and_params(self, configServer):
        configurations = []
        params = []

        git_property = configServer.get('properties', {}).get('configServer', {}).get('gitProperty')
        if git_property is not None:
            self._add_property_if_exists(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_URI, git_property.get('uri'))
            self._add_property_if_exists(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_LABEL, git_property.get('label'))
            self._add_property_if_exists(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_SEARCH_PATHS, git_property.get('searchPaths'))
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_USERNAME, git_property.get('username'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_PASSWORD, git_property.get('password'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_PRIVATE_KEY, git_property.get('privateKey'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_HOST_KEY, git_property.get('hostKey'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_HOST_KEY_ALGORITHM, git_property.get('hostKeyAlgorithm'), configurations, params)

            git_repos = git_property.get('repositories', [])
            for repo in git_repos:
                configuration_key_repo_prefix = self.CONFIGURATION_KEY_PREFIX + ".repos." + repo['name']
                self._add_property_if_exists(configurations, configuration_key_repo_prefix + self.KEY_URI, repo.get('uri'))
                self._add_property_if_exists(configurations, configuration_key_repo_prefix + self.KEY_LABEL, repo.get('label'))
                self._add_property_if_exists(configurations, configuration_key_repo_prefix + self.KEY_SEARCH_PATHS, repo.get('searchPaths'))
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_USERNAME, repo.get('username'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_PASSWORD, repo.get('password'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_PRIVATE_KEY, repo.get('privateKey'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_HOST_KEY, repo.get('hostKey'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_HOST_KEY_ALGORITHM, repo.get('hostKeyAlgorithm'), configurations, params)
                self._add_property_if_exists(configurations, configuration_key_repo_prefix + self.KEY_PATTERN, repo.get('pattern'))

        return configurations, params

    def _add_property_if_exists(self, configurations, key, value):
        if value:
            if isinstance(value, (list, tuple)):
                value = ",".join(map(str, value))
            configurations.append({
                "propertyName": key,
                "value": value
            })

    def _add_secret_config(self, key, value, configurations, params):
        if value:
            param_name = key.replace(".", "_").replace("-", "_")
            self._add_property_if_exists(configurations, key, param_name)
            params.append(param_name)
