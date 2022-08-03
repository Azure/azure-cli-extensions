# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
import json

from azure.cli.core.azclierror import ClientRequestError, ValidationError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger
from msrestazure.tools import resource_id

from .vendored_sdks.appplatform.v2022_01_01_preview import models

APPLICATION_CONFIGURATION_SERVICE_NAME = "applicationConfigurationService"
RESOURCE_ID = "resourceId"

RESOURCE_TYPE = "configurationServices"
DEFAULT_NAME = "default"

logger = get_logger(__name__)


def application_configuration_service_show(cmd, client, service, resource_group):
    return client.configuration_services.get(resource_group, service, DEFAULT_NAME)


def application_configuration_service_clear(cmd, client, service, resource_group):
    logger.warn("Please make sure no patterns are used in your apps.")
    properties = models.ConfigurationServiceGitProperty()
    acs_resource = models.ConfigurationServiceResource(properties=properties)
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
                                              no_wait=False):
    repo = models.ConfigurationServiceGitRepository(name=name, patterns=patterns, uri=uri, label=label)
    repo = _replace_repo_with_input(repo, patterns, uri, label, search_paths, username, password, host_key, host_key_algorithm, private_key, host_key_check)

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
                                                 no_wait=False):
    acs_resource = _get_or_default_acs_resource(client, resource_group, service)
    repo = _get_existing_repo(acs_resource.properties.settings.git_property.repositories, name)
    repo = _replace_repo_with_input(repo, patterns, uri, label, search_paths, username, password, host_key, host_key_algorithm, private_key, host_key_check)

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


def _replace_repo_with_input(repo, patterns, uri, label, search_paths, username, password, host_key, host_key_algorithm, private_key, strict_host_key_checking):
    if patterns:
        patterns = patterns.split(",")
    if search_paths:
        search_paths = search_paths.split(",")

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
