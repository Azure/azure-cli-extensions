# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
import json
import os
import requests

from azure.cli.core.azclierror import ClientRequestError, ValidationError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.tools import resource_id
from .vendored_sdks.appplatform.v2024_05_01_preview.models._app_platform_management_client_enums import (GitImplementation, ConfigurationServiceGeneration)
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from ._utils import (get_hostname, get_bearer_auth)

APPLICATION_CONFIGURATION_SERVICE_NAME = "applicationConfigurationService"
RESOURCE_ID = "resourceId"

RESOURCE_TYPE = "configurationServices"
DEFAULT_NAME = "default"

CONFIGURATION_FILES = "configurationFiles"

logger = get_logger(__name__)


def application_configuration_service_create(cmd, client, service, resource_group,
                                             generation=None, refresh_interval=None):
    if generation is None:
        generation = ConfigurationServiceGeneration.GEN1

    properties = models.ConfigurationServiceProperties(generation=generation)
    if refresh_interval is not None:
        properties.settings = models.ConfigurationServiceSettings(refresh_interval_in_seconds=refresh_interval)
    acs_resource = models.ConfigurationServiceResource(properties=properties)
    logger.warning("Create with generation {}".format(acs_resource.properties.generation))
    return client.configuration_services.begin_create_or_update(resource_group, service, DEFAULT_NAME, acs_resource)


def application_configuration_service_update(cmd, client, service, resource_group,
                                             generation=None, refresh_interval=None):
    acs_resource = client.configuration_services.get(resource_group, service, DEFAULT_NAME)
    if generation is not None:
        acs_resource.properties.generation = generation
        logger.warning("Updating with generation {}".format(generation))
    else:
        acs_resource.properties.generation = ConfigurationServiceGeneration.GEN1
        logger.warning("Default generation will be Gen1")
    logger.warning(acs_resource.properties.generation)
    if refresh_interval is not None:
        acs_resource.properties.settings = acs_resource.properties.settings or models.ConfigurationServiceSettings()
        acs_resource.properties.settings.refresh_interval_in_seconds = refresh_interval
    return client.configuration_services.begin_create_or_update(resource_group, service, DEFAULT_NAME, acs_resource)


def application_configuration_service_delete(cmd, client, service, resource_group):
    return client.configuration_services.begin_delete(resource_group, service, DEFAULT_NAME)


def application_configuration_service_show(cmd, client, service, resource_group):
    return client.configuration_services.get(resource_group, service, DEFAULT_NAME)


def application_configuration_service_clear(cmd, client, service, resource_group):
    logger.warn("Please make sure no patterns are used in your apps.")
    acs_resource = client.configuration_services.get(resource_group, service, DEFAULT_NAME)
    acs_resource.properties.settings = models.ConfigurationServiceSettings()
    return client.configuration_services.begin_create_or_update(resource_group, service, DEFAULT_NAME, acs_resource)


def application_configuration_service_git_add(cmd, client, service, resource_group,
                                              name, patterns, uri, label,
                                              search_paths=None,
                                              username=None,
                                              password=None,
                                              host_key=None,
                                              host_key_algorithm=None,
                                              private_key=None,
                                              host_key_check=None,
                                              ca_cert_name=None,
                                              no_wait=False):
    repo = models.ConfigurationServiceGitRepository(name=name, patterns=patterns, uri=uri, label=label)
    repo = _replace_repo_with_input(repo, patterns, uri, label, search_paths, username, password, host_key, host_key_algorithm, private_key, host_key_check, _get_cert_resource_id_by_name(cmd, resource_group, service, ca_cert_name))

    acs_resource = _get_or_default_acs_resource(client, resource_group, service)
    repos = acs_resource.properties.settings.git_property.repositories
    if next((r for r in repos if r.name == name), None) is not None:
        raise ValidationError("Repo '{}' already exists.".format(name))
    repos.append(repo)
    acs_resource.properties.settings.git_property.repositories = repos

    _validate_acs_settings(client, resource_group, service, acs_resource.properties.settings)

    logger.warning("[2/2] Adding item to Application Configuration Service settings, (this operation can take a while to complete)")
    return sdk_no_wait(no_wait, client.configuration_services.begin_create_or_update, resource_group, service, DEFAULT_NAME, acs_resource)


def application_configuration_service_git_update(cmd, client, service, resource_group, name,
                                                 patterns=None,
                                                 uri=None,
                                                 label=None,
                                                 search_paths=None,
                                                 username=None,
                                                 password=None,
                                                 host_key=None,
                                                 host_key_algorithm=None,
                                                 private_key=None,
                                                 host_key_check=None,
                                                 ca_cert_name=None,
                                                 no_wait=False):
    acs_resource = _get_or_default_acs_resource(client, resource_group, service)
    repo = _get_existing_repo(acs_resource.properties.settings.git_property.repositories, name)
    repo = _replace_repo_with_input(repo, patterns, uri, label, search_paths, username, password, host_key, host_key_algorithm, private_key, host_key_check, _get_cert_resource_id_by_name(cmd, resource_group, service, ca_cert_name))

    _validate_acs_settings(client, resource_group, service, acs_resource.properties.settings)

    logger.warning("[2/2] Updating item of Application Configuration Service settings, (this operation can take a while to complete)")
    return sdk_no_wait(no_wait, client.configuration_services.begin_create_or_update, resource_group, service, DEFAULT_NAME, acs_resource)


def application_configuration_service_git_remove(cmd, client, service, resource_group, name, no_wait=False):
    acs_resource = _get_or_default_acs_resource(client, resource_group, service)

    repo = _get_existing_repo(acs_resource.properties.settings.git_property.repositories, name)
    acs_resource.properties.settings.git_property.repositories.remove(repo)

    _validate_acs_settings(client, resource_group, service, acs_resource.properties.settings)

    logger.warning("[2/2] Removing item of Application Configuration Service settings, (this operation can take a while to complete)")
    return sdk_no_wait(no_wait, client.configuration_services.begin_create_or_update, resource_group, service, DEFAULT_NAME, acs_resource)


def application_configuration_service_git_list(cmd, client, service, resource_group):
    acs_resource = client.configuration_services.get(resource_group, service, DEFAULT_NAME)
    acs_settings = acs_resource.properties.settings

    return acs_settings.git_property.repositories


def application_configuration_service_bind(cmd, client, service, resource_group, app):
    return _acs_bind_or_unbind_app(cmd, client, service, resource_group, app, True)


def application_configuration_service_unbind(cmd, client, service, resource_group, app):
    return _acs_bind_or_unbind_app(cmd, client, service, resource_group, app, False)


def application_configuration_service_config_show(cmd, client, service, resource_group, config_file_pattern,
                                                  export_path=None):
    url = _get_show_configs_urls(cmd, client, service, resource_group, config_file_pattern)
    auth = get_bearer_auth(cmd.cli_ctx)
    connect_timeout_in_seconds = 30
    read_timeout_in_seconds = 60
    timeout = (connect_timeout_in_seconds, read_timeout_in_seconds)
    with requests.get(url, stream=False, auth=auth, timeout=timeout) as response:
        if response.status_code != 200:
            _handle_and_raise_get_acs_config_error(url, response)
        response_json = response.json()
        if export_path is not None:
            _export_configs_to_files(response_json, export_path)
            # Return None after export to the files
            return None
        else:
            return _split_config_lines(response_json)


def _acs_bind_or_unbind_app(cmd, client, service, resource_group, app_name, enabled):
    app = client.apps.get(resource_group, service, app_name)
    app.properties.addon_configs = _get_app_addon_configs_with_acs(app.properties.addon_configs)

    if (app.properties.addon_configs[APPLICATION_CONFIGURATION_SERVICE_NAME][RESOURCE_ID] != "") == enabled:
        logger.warning('App "{}" has been {}binded'.format(app_name, '' if enabled else 'un'))
        return app

    acs_id = resource_id(
        subscription=get_subscription_id(cmd.cli_ctx),
        resource_group=resource_group,
        namespace='Microsoft.AppPlatform',
        type='Spring',
        name=service,
        child_type_1=RESOURCE_TYPE,
        child_name_1=DEFAULT_NAME
    )
    if enabled:
        app.properties.addon_configs[APPLICATION_CONFIGURATION_SERVICE_NAME][RESOURCE_ID] = acs_id
    else:
        app.properties.addon_configs[APPLICATION_CONFIGURATION_SERVICE_NAME][RESOURCE_ID] = ""
    return client.apps.begin_update(resource_group, service, app_name, app)


def _get_app_addon_configs_with_acs(addon_configs):
    if addon_configs is None:
        addon_configs = {}
    if addon_configs.get(APPLICATION_CONFIGURATION_SERVICE_NAME) is None:
        addon_configs[APPLICATION_CONFIGURATION_SERVICE_NAME] = {}
    if addon_configs[APPLICATION_CONFIGURATION_SERVICE_NAME].get(RESOURCE_ID) is None:
        addon_configs[APPLICATION_CONFIGURATION_SERVICE_NAME][RESOURCE_ID] = ""
    return addon_configs


def _get_cert_resource_id_by_name(cmd, resource_group, service, ca_cert_name):
    ca_cert_resource_id = None
    if ca_cert_name:
        subscription = get_subscription_id(cmd.cli_ctx)
        ca_cert_resource_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/certificates/{}".format(subscription, resource_group, service, ca_cert_name)
    return ca_cert_resource_id


def _replace_repo_with_input(repo, patterns, uri, label, search_paths, username, password, host_key, host_key_algorithm, private_key, strict_host_key_checking, ca_cert_resource_id):
    if patterns:
        patterns = patterns.split(",")
    if search_paths:
        search_paths = search_paths.split(",")
    if private_key:
        private_key = private_key.replace('\\n', '\n')

    repo.patterns = patterns or repo.patterns
    repo.uri = uri or repo.uri
    repo.label = label or repo.label
    repo.search_paths = search_paths or repo.search_paths
    repo.username = username or repo.username
    repo.password = password or repo.password
    repo.host_key = host_key or repo.host_key
    repo.host_key_algorithm = host_key_algorithm or repo.host_key_algorithm
    repo.private_key = private_key or repo.private_key
    repo.strict_host_key_checking = strict_host_key_checking or repo.strict_host_key_checking
    repo.ca_cert_resource_id = ca_cert_resource_id or repo.ca_cert_resource_id
    return repo


def _get_existing_repo(repos, name):
    repo = next((r for r in repos if r.name == name), None)
    if not repo:
        raise ClientRequestError("Repo '{}' not found.".format(name))
    return repo


def _get_or_default_acs_resource(client, resource_group, service):
    acs_resource = client.configuration_services.get(resource_group, service, DEFAULT_NAME)
    if acs_resource is None:
        acs_resource = models.ConfigurationServiceResource()
    acs_resource.properties = _get_acs_properties(acs_resource.properties)
    return acs_resource


def _get_acs_properties(properties):
    if properties is None:
        properties = models.ConfigurationServiceProperties()
    if properties.provisioning_state == "Updating":
        raise ClientRequestError("Application Configuration Service is updating, please try again later.")
    properties.settings = _get_acs_settings(properties.settings)
    return properties


def _get_acs_settings(acs_settings):
    if acs_settings is None:
        acs_settings = models.ConfigurationServiceSettings()
    acs_settings.git_property = _get_acs_git_property(acs_settings.git_property)
    return acs_settings


def _get_acs_git_property(git_property):
    if git_property is None:
        git_property = models.ConfigurationServiceGitProperty()
    git_property.repositories = _get_acs_repos(git_property.repositories)
    return git_property


def _get_acs_repos(repos):
    return repos or []


def _validate_acs_settings(client, resource_group, service, acs_settings):
    logger.warning("[1/2] Validating Application Configuration Service settings")

    if acs_settings is None or acs_settings.git_property is None:
        return

    try:
        result = sdk_no_wait(False, client.configuration_services.begin_validate, resource_group, service, DEFAULT_NAME, acs_settings).result()
    except Exception as err:  # pylint: disable=broad-except
        raise ClientRequestError("{0}. You may raise a support ticket if needed by the following link: https://docs.microsoft.com/azure/spring-cloud/spring-cloud-faq?pivots=programming-language-java#how-can-i-provide-feedback-and-report-issues".format(err))

    if result is not None and result.git_property_validation_result is not None:
        git_result = result.git_property_validation_result
        if not git_result.is_valid:
            validation_result = git_result.git_repos_validation_result
            filter_result = [{'name': x.name, 'messages': x.messages} for x in validation_result if len(x.messages) > 0]
            raise ClientRequestError("Application Configuration Service settings contain errors.\n{}".format(json.dumps(filter_result, indent=2)))


def _get_show_configs_urls(cmd, client, service, resource_group, config_file_pattern):
    hostname = get_hostname(cmd.cli_ctx, client, resource_group, service)
    appName, profileName = _get_app_and_profile(config_file_pattern)
    url_template = "https://{}/api/applicationConfigurationService/configs/applications/{}/profiles/{}"
    url = url_template.format(hostname, appName, profileName)
    return url


def _get_app_and_profile(config_file_pattern):
    # The config file pattern should already be standardized with non-empty app name and profile name
    parts = config_file_pattern.split('/')
    return parts[0], parts[1]


def _handle_and_raise_get_acs_config_error(url, response):
    failure_reason = response.reason
    if response.content:
        if isinstance(response.content, bytes):
            failure_reason = f"{failure_reason}:{response.content.decode('utf-8')}"
        else:
            failure_reason = f"{failure_reason}:{response.content}"
    msg = f"Failed to access the url '{url}' with status code '{response.status_code}' and reason '{failure_reason}'"
    raise CLIError(msg)


def _split_config_lines(response_json):
    """
    The configs is subject to the implementation of Application Configuration Service (ACS).
    Currently, it only uses "application.properties" file. An exmaple of raw_configs is:
    {
      "configurationFiles": {
        "application.properties": "auth: ssh\nrepo: ado\nspring.cloud.config.enabled: false"
      }
    }
    The expected format is as follows:
    {
      "configurationFiles": {
        "application.properties": [
          "auth: ssh",
          "repo: ado",
          "spring.cloud.config.enabled: false"
        ]
      }
    }
    Note we don't continue parse each line, since there can be corner case like:
    {
        "application.properties": "p1: v1-\n-8976\np2: v2-\\n-5674"
    }
    It will be converted to below content in ACS:
    {
      "application": [
        "p1: v1-",
        "-8976",
        "p2: v2-\n-5674"
      ]
    }
    """
    configuration_files = response_json[CONFIGURATION_FILES]

    filename_to_multi_line_configs_dict = {}

    for key in configuration_files.keys():
        value = configuration_files[key]
        if key.endswith(".properties") and isinstance(value, str):
            filename_to_multi_line_configs_dict[key] = value.splitlines()
        else:
            filename_to_multi_line_configs_dict[key] = value

    if len(filename_to_multi_line_configs_dict) == 0:
        raise CLIError("No configuration files found.")

    return {
        CONFIGURATION_FILES: filename_to_multi_line_configs_dict
    }


def _export_configs_to_files(response_json, folder_path):
    absolute_folder_path = os.path.abspath(folder_path)

    if not os.path.exists(absolute_folder_path):
        logger.warning(f"Directory '{absolute_folder_path}' does not exist, creating it.")
        os.makedirs(absolute_folder_path)

    if not os.path.isdir(absolute_folder_path):
        raise CLIError(f"Path '{absolute_folder_path}' is not a directory.")

    for filename in response_json[CONFIGURATION_FILES].keys():
        absolute_file_path = os.path.join(absolute_folder_path, filename)
        if os.path.exists(absolute_file_path):
            logger.warning(f"File already exists: '{absolute_file_path}', overriding it.")
        with open(absolute_file_path, 'w', encoding="utf-8") as file:
            file.write(response_json[CONFIGURATION_FILES][filename])
        logger.warning(f"Exported configurations to file '{absolute_file_path}'.")
