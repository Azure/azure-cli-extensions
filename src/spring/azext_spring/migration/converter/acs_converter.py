# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from .base_converter import BaseConverter

logger = get_logger(__name__)


# Concrete Converter Subclass for Config Server
class ACSConverter(BaseConverter):

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
            if self.wrapper_data.is_support_ossconfigserver() is False and self.wrapper_data.is_support_acs():
                acs = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/configurationServices')[0]
                name = "config"
                configurations, params = self._get_configurations_and_params(acs)
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

    def _get_configurations_and_params(self, acs):
        configurations = []
        params = []

        git_repos = acs.get('properties', {}).get('settings', {}).get('gitProperty', {}).get('repositories', None)
        if git_repos is not None and len(git_repos) > 0:
            default_repo = git_repos[0]
            self._add_property_if_exists(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_URI, default_repo.get('uri'))
            self._add_property_if_exists(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_LABEL, default_repo.get('label'))
            self._add_property_if_exists(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_SEARCH_PATHS, default_repo.get('searchPaths'))
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_USERNAME, default_repo.get('username'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_PASSWORD, default_repo.get('password'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_PRIVATE_KEY, default_repo.get('privateKey'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_HOST_KEY, default_repo.get('hostKey'), configurations, params)
            self._add_secret_config(self.CONFIGURATION_KEY_PREFIX + self.KEY_HOST_KEY_ALGORITHM, default_repo.get('hostKeyAlgorithm'), configurations, params)
            self._check_patterns(default_repo)

            for i in range(1, len(git_repos)):
                repo = git_repos[i]
                configuration_key_repo_prefix = self.CONFIGURATION_KEY_PREFIX + ".repos." + repo['name']
                self._add_property_if_exists(configurations, configuration_key_repo_prefix + self.KEY_URI, repo.get('uri'))
                self._add_property_if_exists(configurations, configuration_key_repo_prefix + self.KEY_LABEL, repo.get('label'))
                self._add_property_if_exists(configurations, configuration_key_repo_prefix + self.KEY_SEARCH_PATHS, repo.get('searchPaths'))
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_USERNAME, repo.get('username'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_PASSWORD, repo.get('password'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_PRIVATE_KEY, repo.get('privateKey'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_HOST_KEY, repo.get('hostKey'), configurations, params)
                self._add_secret_config(configuration_key_repo_prefix + self.KEY_HOST_KEY_ALGORITHM, repo.get('hostKeyAlgorithm'), configurations, params)
                self._check_patterns(repo)

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

    def _check_patterns(self, repo):
        patterns = repo.get('patterns', [])
        if len(patterns) > 0:
            pattern_str = ",".join(map(str, patterns))
            logger.info(f"The patterns '{pattern_str}' of the git repository '{repo.get('name')}' in Application Configuration Service not need in Config Server of Azure Container Apps.")
