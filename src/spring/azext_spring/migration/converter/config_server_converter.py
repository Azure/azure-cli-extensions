from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Config Server
class ConfigServerConverter(ConverterTemplate):

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

    def __init__(self):
        super().__init__()

    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        name = f"config"
        configurations = self._get_configurations(self.source)
        replicas = 2

        self.data = {
            "configServerName": name,
            "configurations": configurations,
            "replicas": replicas
        }

    def get_template_name(self):
        return "config_server.bicep"
    
    def _get_configurations(self, source):
        configurations = []
        
        git_property = source.get('properties', {}).get('configServer', {}).get('gitProperty')
        if git_property is not None:
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_URI, git_property.get('uri'))
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_LABEL, git_property.get('label'))
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_SEARCH_PATHS, git_property.get('searchPaths'))
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_USERNAME, git_property.get('username'))
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_PASSWORD, git_property.get('password'))
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_PRIVATE_KEY, git_property.get('privateKey'))
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_HOST_KEY, git_property.get('hostKey'))
            self._add_property_if_existss(configurations, self.CONFIGURATION_KEY_PREFIX + self.KEY_HOST_KEY_ALGORITHM, git_property.get('hostKeyAlgorithm'))

            git_repos = git_property.get('repositories', [])
            for repo in git_repos:
                configuration_key_repo_prefix = self.CONFIGURATION_KEY_PREFIX + ".repos." + repo['name']
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_URI, repo.get('uri'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_LABEL, repo.get('label'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_SEARCH_PATHS, repo.get('searchPaths'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_USERNAME, repo.get('username'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_PASSWORD, repo.get('password'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_PRIVATE_KEY, repo.get('privateKey'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_HOST_KEY, repo.get('hostKey'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_HOST_KEY_ALGORITHM, repo.get('hostKeyAlgorithm'))
                self._add_property_if_existss(configurations, configuration_key_repo_prefix + self.KEY_PATTERN, repo.get('pattern'))

        return configurations

    def _add_property_if_existss(self, configurations, key, value):
        if value:
            if isinstance(value, (list, tuple)):
                value = ",".join(map(str, value))
            configurations.append({
                "propertyName": key,
                "value": value
            })
    