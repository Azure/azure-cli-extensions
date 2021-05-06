# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

from binascii import hexlify
from os import urandom
import json
import ssl
import sys
import platform

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # pylint: disable=import-error

from knack.util import CLIError
from knack.log import get_logger

from azure.cli.command_modules.appservice.custom import (
    list_webapp,
    _rename_server_farm_props,
    _generic_settings_operation,
    _build_app_settings_output,
    get_site_configs,
    get_webapp,
    _get_site_credential,
    _mask_creds_related_appsettings,
    _format_fx_version,
    _get_extension_version_functionapp,
    _validate_app_service_environment_id,
    _get_location_from_webapp,
    validate_and_convert_to_int,
    validate_range_of_int_flag,
    get_app_settings,
    get_app_insights_key,
    _update_webapp_current_stack_property_if_needed,
    validate_container_app_create_options,
    parse_docker_image_name,
    list_consumption_locations,
    is_plan_elastic_premium,
    enable_local_git,
    _validate_and_get_connection_string,
    _get_acr_cred,
    _get_linux_multicontainer_encoded_config_from_file,
    _filter_for_container_settings,
    _get_url,
    _StackRuntimeHelper,
    upload_zip_to_storage,
    is_plan_consumption)

from azure.cli.command_modules.appservice.utils import retryable_method

from azure.cli.core.util import sdk_no_wait, shell_safe_json_parse, get_json_object, in_cloud_console
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.commands import LongRunningOperation

from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient

from azure.cli.core.util import get_az_user_agent
from azure.cli.core.azclierror import (ResourceNotFoundError, RequiredArgumentMissingError, ValidationError,
                                       CLIInternalError, UnclassifiedUserFault, AzureResponseError,
                                       ArgumentUsageError, MutuallyExclusiveArgumentError)

from msrestazure.tools import is_valid_resource_id, parse_resource_id

from six.moves.urllib.request import urlopen

from ._constants import (FUNCTIONS_VERSION_TO_DEFAULT_RUNTIME_VERSION, FUNCTIONS_VERSION_TO_DEFAULT_NODE_VERSION,
                         FUNCTIONS_VERSION_TO_SUPPORTED_RUNTIME_VERSIONS, NODE_VERSION_DEFAULT, NODE_EXACT_VERSION_DEFAULT,
                         DOTNET_RUNTIME_VERSION_TO_DOTNET_LINUX_FX_VERSION, KUBE_DEFAULT_SKU,
                         KUBE_ASP_KIND, KUBE_APP_KIND, KUBE_FUNCTION_APP_KIND, KUBE_FUNCTION_CONTAINER_APP_KIND, KUBE_CONTAINER_APP_KIND,
                         LINUX_RUNTIMES, WINDOWS_RUNTIMES, MULTI_CONTAINER_TYPES,CONTAINER_APPSETTING_NAMES, APPSETTINGS_TO_MASK)

from ._utils import (_normalize_sku, get_sku_name, validate_subnet_id, _generic_site_operation,
                     _get_location_from_resource_group, validate_aks_id)
from ._create_util import (zip_contents_from_dir, get_runtime_version_details, create_resource_group, get_app_details,
                           should_create_new_rg, set_location, get_site_availability, does_app_already_exist, get_profile_username,
                           get_plan_to_use,get_kube_plan_to_use, get_lang_from_content, get_rg_to_use, get_sku_to_use,
                           detect_os_form_src, get_current_stack_from_runtime, generate_default_app_service_plan_name)
from ._client_factory import web_client_factory, cf_kube_environments, ex_handler_factory
from .vsts_cd_provider import VstsContinuousDeliveryProvider

import subprocess
from subprocess import PIPE
import tempfile
import shutil
import os

logger = get_logger(__name__)


# pylint: disable=too-many-locals,too-many-lines

def create_kube_environment(cmd, client, name, resource_group_name, custom_location, static_ip,
                              location=None, tags=None, no_wait=False):
    KubeEnvironment, ExtendedLocation, ArcConfiguration, FrontEndConfiguration = cmd.get_models('KubeEnvironment',
        'ExtendedLocation', 'ArcConfiguration', 'FrontEndConfiguration')

    if not is_valid_resource_id(custom_location):
        raise CLIError('Invalid custom location')

    parsed_custom_location = parse_resource_id(custom_location)
    if parsed_custom_location['resource_type'].lower() != 'customlocations':
        raise CLIError('Invalid custom location')

    if not location:
        location = _get_location_from_resource_group(cmd.cli_ctx, parsed_custom_location['resource_group'])
    front_end_configuration = FrontEndConfiguration(kind="LoadBalancer")
    extended_location = ExtendedLocation(custom_location=custom_location)
    arc_configuration = ArcConfiguration(
        artifacts_storage_type="NetworkFileSystem", artifact_storage_class_name="default", front_end_service_configuration=front_end_configuration)
    kube_environment = KubeEnvironment(
        name=name,
        location=location,
        kind="null",
        tags=tags,
        plan=None,
        extended_location=extended_location,
        static_ip=static_ip,
        arc_configuration=arc_configuration)

    return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, name=name, kube_environment_envelope=kube_environment)


def list_kube_environments(client, resource_group_name=None):
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def update_kube_environment(cmd,
                            kube_name,
                            resource_group_name,
                            tags=None,
                            no_wait=False):
    raise CLIError("Update is not yet supported for Kubernetes Environments.")


def list_app_service_plans(cmd, resource_group_name=None):
    client = web_client_factory(cmd.cli_ctx)
    if resource_group_name is None:
        plans = list(client.app_service_plans.list())
    else:
        plans = list(client.app_service_plans.list_by_resource_group(resource_group_name))
    for plan in plans:
        # prune a few useless fields
        del plan.geo_region
        del plan.subscription
    return plans


def _validate_asp_sku(app_service_environment, custom_location, sku):
    # Isolated SKU is supported only for ASE
    if sku.upper() not in ['F1', 'FREE', 'D1', 'SHARED', 'B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1V2', 'P2V2', 'P3V2', 'PC2', 'PC3', 'PC4', 'I1', 'I2', 'I3', 'K1']:
        raise CLIError('Invalid sku entered: {}'.format(sku))

    if sku.upper() in ['I1', 'I2', 'I3', 'I1V2', 'I2V2', 'I3V2']:
        if not app_service_environment:
            raise CLIError("The pricing tier 'Isolated' is not allowed for this app service plan. Use this link to "
                           "learn more: https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans")
    elif app_service_environment:
        raise CLIError("Only pricing tier 'Isolated' is allowed in this app service plan. Use this link to "
                        "learn more: https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans")
    elif custom_location:
        # Custom Location only supports K1
        if sku.upper() != 'K1':
            raise CLIError("Only pricing tier 'K1' is allowed for this type of app service plan.")


def create_app_service_plan(cmd, resource_group_name, name, is_linux, hyper_v, per_site_scaling=False, custom_location=None,
                            app_service_environment=None, sku=None,
                            number_of_workers=None, location=None, tags=None, no_wait=False):
    if not sku:
        sku = 'B1' if not custom_location else KUBE_DEFAULT_SKU

    if custom_location:
        if not per_site_scaling:
            raise ArgumentUsageError('Per Site Scaling must be true when using Custom Location. Please re-run with --per-site-scaling flag')
        if app_service_environment:
            raise ArgumentUsageError('App Service Environment is not supported with using Custom Location')
        if hyper_v:
            raise ArgumentUsageError('Hyper V is not supported with using Custom Location')
        if not is_linux:
            raise ArgumentUsageError('Only Linux is supported with using Custom Location. Please re-run with --is-linux flag.')

    return create_app_service_plan_inner(cmd, resource_group_name, name, is_linux, hyper_v, per_site_scaling, custom_location,
        app_service_environment, sku, number_of_workers, location, tags, no_wait)


def get_vm_sizes(cli_ctx, location):
    from ._client_factory import cf_compute_service

    return cf_compute_service(cli_ctx).virtual_machine_sizes.list(location)


def _get_kube_env_from_custom_location(cmd, custom_location):
    kube_environment_id = ""

    if is_valid_resource_id(custom_location):
        parsed_custom_location = parse_resource_id(custom_location)
        custom_location = parsed_custom_location.get("name")

    kube_envs = cf_kube_environments(cmd.cli_ctx).list_by_subscription()
    for kube in kube_envs:
        if kube.extended_location and kube.extended_location.custom_location:
            parsed_custom_location_2 = parse_resource_id(kube.extended_location.custom_location)
            if parsed_custom_location_2.get("name").lower() == custom_location.lower():
                kube_environment_id = kube.id
                break

    if not kube_environment_id:
        raise ResourceNotFoundError('Unable to find Kube Environment associated to the Custom Location')

    return kube_environment_id


def create_app_service_plan_inner(cmd, resource_group_name, name, is_linux, hyper_v, per_site_scaling=False, custom_location=None,
                            app_service_environment=None, sku=None,
                            number_of_workers=None, location=None, tags=None, no_wait=False):
    HostingEnvironmentProfile, SkuDescription, AppServicePlan, KubeEnvironmentProfile = cmd.get_models(
        'HostingEnvironmentProfile', 'SkuDescription', 'AppServicePlan', 'KubeEnvironmentProfile')
    sku = _normalize_sku(sku)
    _validate_asp_sku(app_service_environment, custom_location, sku)

    if is_linux and hyper_v:
        raise MutuallyExclusiveArgumentError('Usage error: --is-linux and --hyper-v cannot be used together.')

    kube_environment = None
    kind = None

    client = web_client_factory(cmd.cli_ctx)

    if custom_location:
        kube_environment = _get_kube_env_from_custom_location(cmd, custom_location)

    if app_service_environment:
        if hyper_v:
            raise ArgumentUsageError('Windows containers is not yet supported in app service environment')
        ase_id = _validate_app_service_environment_id(cmd.cli_ctx, app_service_environment, resource_group_name)
        ase_def = HostingEnvironmentProfile(id=ase_id)
        ase_list = client.app_service_environments.list()
        ase_found = False
        for ase in ase_list:
            if ase.name.lower() == app_service_environment.lower() or ase.id.lower() == ase_id.lower():
                location = ase.location
                ase_found = True
                break
        if not ase_found:
            raise CLIError("App service environment '{}' not found in subscription.".format(ase_id))
    else:  # Non-ASE
        ase_def = None

    if kube_environment and ase_def is None:
        kube_id = _resolve_kube_environment_id(cmd.cli_ctx, kube_environment, resource_group_name)
        kube_def = KubeEnvironmentProfile(id=kube_id)
        kind = KUBE_ASP_KIND
        parsed_id = parse_resource_id(kube_id)
        kube_name = parsed_id.get("name")
        kube_rg = parsed_id.get("resource_group")
        if kube_name is not None and kube_rg is not None:
            kube_env = cf_kube_environments(cmd.cli_ctx).get(kube_rg, kube_name)
            if kube_env is not None:
                location = kube_env.location
            else:
                raise CLIError("Kube Environment '{}' not found in subscription.".format(kube_id))
    else:
        kube_def = None

    if location is None:
        location = _get_location_from_resource_group(cmd.cli_ctx, resource_group_name)

    # the api is odd on parameter naming, have to live with it for now
    sku_def = SkuDescription(tier=get_sku_name(sku), name=sku, capacity=number_of_workers)

    plan_def = AppServicePlan(location=location, tags=tags, sku=sku_def, kind=kind,
                              reserved=(is_linux or None), hyper_v=(hyper_v or None), name=name,
                              per_site_scaling=per_site_scaling, hosting_environment_profile=ase_def,
                              kube_environment_profile=kube_def)
    return sdk_no_wait(no_wait, client.app_service_plans.create_or_update, name=name,
                       resource_group_name=resource_group_name, app_service_plan=plan_def)


def update_app_service_plan(instance, sku=None, number_of_workers=None):
    if number_of_workers is None and sku is None:
        logger.warning(
            'No update is done. Specify --sku and/or --kube-sku and/or --number-of-workers.')
    sku_def = instance.sku
    if sku is not None:
        sku = _normalize_sku(sku)
        sku_def.tier = get_sku_name(sku)
        sku_def.name = sku

    if number_of_workers is not None:
        sku_def.capacity = number_of_workers
    instance.sku = sku_def
    return instance


def _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location, plan):
    client = web_client_factory(cmd.cli_ctx)
    if is_valid_resource_id(plan):
        parse_result = parse_resource_id(plan)
        plan_info = client.app_service_plans.get(parse_result['resource_group'], parse_result['name'])
    else:
        plan_info = client.app_service_plans.get(resource_group_name, plan)
    if not plan_info:
        raise CLIError("The plan '{}' doesn't exist in the resource group '{}".format(plan, resource_group_name))

    plan_kube_env_id = ""
    custom_location_kube_env_id = _get_kube_env_from_custom_location(cmd, custom_location)
    if plan_info.kube_environment_profile:
        plan_kube_env_id = plan_info.kube_environment_profile.id

    return plan_kube_env_id.lower() == custom_location_kube_env_id.lower()


def _should_create_new_appservice_plan_for_k8se(cmd, name, custom_location, plan, resource_group_name):
    if custom_location and plan:
        return False
    elif custom_location:
        existing_app_details = get_app_details(cmd, name, resource_group_name)
        if not existing_app_details:
            return True
        else:
            if _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location, existing_app_details.server_farm_id):  # existing app and kube environments match
                return False
            else:  # existing app but new custom location
                return True
    else:  # plan is not None
        return False


def create_webapp(cmd, resource_group_name, name, plan=None, runtime=None, custom_location=None, startup_file=None,  # pylint: disable=too-many-statements,too-many-branches
                  deployment_container_image_name=None, deployment_source_url=None, deployment_source_branch='master',
                  deployment_local_git=None, docker_registry_server_password=None, docker_registry_server_user=None,
                  multicontainer_config_type=None, multicontainer_config_file=None, tags=None,
                  using_webapp_up=False, language=None, assign_identities=None, role='Contributor', scope=None,
                  min_worker_count=None, max_worker_count=None):
    SiteConfig, SkuDescription, Site, NameValuePair = cmd.get_models(
        'SiteConfig', 'SkuDescription', 'Site', 'NameValuePair')
    if deployment_source_url and deployment_local_git:
        raise CLIError('usage error: --deployment-source-url <url> | --deployment-local-git')

    if not plan and not custom_location:
        raise RequiredArgumentMissingError("Either Plan or Custom Location must be specified")

    # This is to keep the existing appsettings for a newly created webapp on existing webapp name.
    name_validation = get_site_availability(cmd, name)
    if not name_validation.name_available:
        if name_validation.reason == 'Invalid':
            raise CLIError(name_validation.message)
        logger.warning("Webapp '%s' already exists. The command will use the existing app's settings.", name)
        app_details = get_app_details(cmd, name, resource_group_name)
        if app_details is None:
            raise CLIError("Unable to retrieve details of the existing app '{}'. Please check that "
                           "the app is a part of the current subscription".format(name))
        current_rg = app_details.resource_group
        if resource_group_name is not None and (resource_group_name.lower() != current_rg.lower()):
            raise CLIError("The webapp '{}' exists in resource group '{}' and does not "
                           "match the value entered '{}'. Please re-run command with the "
                           "correct parameters.". format(name, current_rg, resource_group_name))
        existing_app_settings = _generic_site_operation(cmd.cli_ctx, resource_group_name,
                                                        name, 'list_application_settings')
        settings = []
        for k, v in existing_app_settings.properties.items():
            settings.append(NameValuePair(name=k, value=v))
        site_config = SiteConfig(app_settings=settings)
    else:
        site_config = SiteConfig(app_settings=[])

    _should_create_new_plan = _should_create_new_appservice_plan_for_k8se(cmd, name, custom_location, plan, resource_group_name)
    if _should_create_new_plan:
        plan = generate_default_app_service_plan_name(name)
        logger.warning("Plan not specified. Creating Plan '%s' with sku '%s'", plan, KUBE_DEFAULT_SKU)
        create_app_service_plan(cmd=cmd, resource_group_name=resource_group_name,
            name=plan, is_linux=True, hyper_v=False, custom_location=custom_location, per_site_scaling=True, number_of_workers=1)

    if custom_location and plan:
        if not _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location, plan):
            raise ValidationError("Custom location's kube environment and App Service Plan's kube environment don't match")
    elif custom_location and not plan:
        app_details = get_app_details(cmd, name, resource_group_name)
        if app_details is not None:
            plan = app_details.server_farm_id

    docker_registry_server_url = parse_docker_image_name(deployment_container_image_name)

    client = web_client_factory(cmd.cli_ctx)
    if is_valid_resource_id(plan):
        parse_result = parse_resource_id(plan)
        plan_info = client.app_service_plans.get(parse_result['resource_group'], parse_result['name'])
    else:
        plan_info = client.app_service_plans.get(resource_group_name, plan)
    if not plan_info:
        raise CLIError("The plan '{}' doesn't exist in the resource group '{}".format(plan, resource_group_name))

    if custom_location:
        sku_tier = None
        if isinstance(plan_info.sku, SkuDescription):
            sku_tier = plan_info.sku.tier
        _validate_asp_sku(app_service_environment=None, custom_location=custom_location, sku=plan_info.sku.name)

    is_linux = plan_info.reserved
    node_default_version = NODE_EXACT_VERSION_DEFAULT
    location = plan_info.location

    if isinstance(plan_info.sku, SkuDescription) and plan_info.sku.name.upper() not in ['F1', 'FREE', 'SHARED', 'D1',
                                                                                        'B1', 'B2', 'B3', 'BASIC']:
        site_config.always_on = True
    webapp_def = Site(location=location, site_config=site_config, server_farm_id=plan_info.id, tags=tags,
                      https_only=using_webapp_up)

    is_kube = False
    if custom_location or plan_info.kind.upper() == KUBE_ASP_KIND.upper() or (isinstance(plan_info.sku, SkuDescription) and plan_info.sku.name.upper() == KUBE_DEFAULT_SKU):
        if deployment_container_image_name:
            webapp_def.kind = KUBE_CONTAINER_APP_KIND
        else:
            webapp_def.kind = KUBE_APP_KIND
        is_kube = True

    if is_kube:
        if min_worker_count is not None:
            site_config.number_of_workers = min_worker_count

        if max_worker_count is not None:
            site_config.app_settings.append(NameValuePair(name='K8SE_APP_MAX_INSTANCE_COUNT', value=max_worker_count))

        if deployment_container_image_name:    
            site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_URL', value=docker_registry_server_url))
            if docker_registry_server_user is not None and docker_registry_server_password is not None:
                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_USERNAME', value=docker_registry_server_user))
                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_PASSWORD', value=docker_registry_server_password))
    helper = _StackRuntimeHelper(cmd, client, linux=(is_linux or is_kube))
    if runtime:
        runtime = helper.remove_delimiters(runtime)

    current_stack = None
    if is_linux or is_kube:
        if not validate_container_app_create_options(runtime, deployment_container_image_name,
                                                     multicontainer_config_type, multicontainer_config_file):
            raise CLIError("usage error: --runtime | --deployment-container-image-name |"
                           " --multicontainer-config-type TYPE --multicontainer-config-file FILE")
        if startup_file:
            site_config.app_command_line = startup_file

        if runtime:
            site_config.linux_fx_version = runtime
            match = helper.resolve(runtime)
            if not match:
                raise CLIError("Linux Runtime '{}' is not supported."
                               "Please invoke 'list-runtimes' to cross check".format(runtime))
            match['setter'](cmd=cmd, stack=match, site_config=site_config)
        elif deployment_container_image_name:
            site_config.linux_fx_version = _format_fx_version(deployment_container_image_name)
            if name_validation.name_available:
                site_config.app_settings.append(NameValuePair(name="WEBSITES_ENABLE_APP_SERVICE_STORAGE",
                                                              value="false"))
        elif multicontainer_config_type and multicontainer_config_file:
            encoded_config_file = _get_linux_multicontainer_encoded_config_from_file(multicontainer_config_file)
            site_config.linux_fx_version = _format_fx_version(encoded_config_file, multicontainer_config_type)

    elif plan_info.is_xenon:  # windows container webapp
        if deployment_container_image_name:
            site_config.windows_fx_version = _format_fx_version(deployment_container_image_name)
        # set the needed app settings for container image validation
        if name_validation.name_available:
            site_config.app_settings.append(NameValuePair(name="DOCKER_REGISTRY_SERVER_USERNAME",
                                                          value=docker_registry_server_user))
            site_config.app_settings.append(NameValuePair(name="DOCKER_REGISTRY_SERVER_PASSWORD",
                                                          value=docker_registry_server_password))
            site_config.app_settings.append(NameValuePair(name="DOCKER_REGISTRY_SERVER_URL",
                                                          value=docker_registry_server_url))

    elif runtime:  # windows webapp with runtime specified
        if any([startup_file, deployment_container_image_name, multicontainer_config_file, multicontainer_config_type]):
            raise CLIError("usage error: --startup-file or --deployment-container-image-name or "
                           "--multicontainer-config-type and --multicontainer-config-file is "
                           "only appliable on linux webapp")
        match = helper.resolve(runtime)
        if not match:
            raise CLIError("Windows runtime '{}' is not supported. "
                           "Please invoke 'az webapp list-runtimes' to cross check".format(runtime))
        match['setter'](cmd=cmd, stack=match, site_config=site_config)

        # portal uses the current_stack propety in metadata to display stack for windows apps
        current_stack = get_current_stack_from_runtime(runtime)

    else:  # windows webapp without runtime specified
        if name_validation.name_available:  # If creating new webapp
            site_config.app_settings.append(NameValuePair(name="WEBSITE_NODE_DEFAULT_VERSION",
                                                          value=node_default_version))

    if site_config.app_settings:
        for setting in site_config.app_settings:
            logger.info('Will set appsetting %s', setting)
    if using_webapp_up:  # when the routine is invoked as a help method for webapp up
        if name_validation.name_available:
            logger.info("will set appsetting for enabling build")
            site_config.app_settings.append(NameValuePair(name="SCM_DO_BUILD_DURING_DEPLOYMENT", value=True))
    if language is not None and language.lower() == 'dotnetcore':
        if name_validation.name_available:
            site_config.app_settings.append(NameValuePair(name='ANCM_ADDITIONAL_ERROR_PAGE_LINK',
                                                          value='https://{}.scm.azurewebsites.net/detectors'
                                                          .format(name)))

    poller = client.web_apps.create_or_update(resource_group_name, name, webapp_def)
    webapp = LongRunningOperation(cmd.cli_ctx)(poller)

    if deployment_container_image_name:
        update_container_settings(cmd, resource_group_name, name, docker_registry_server_url,
                                  deployment_container_image_name, docker_registry_server_user,
                                  docker_registry_server_password=docker_registry_server_password)

    if is_kube:
        return webapp

    if current_stack:
        _update_webapp_current_stack_property_if_needed(cmd, resource_group_name, name, current_stack)

    # Ensure SCC operations follow right after the 'create', no precedent appsetting update commands
    _set_remote_or_local_git(cmd, webapp, resource_group_name, name, deployment_source_url,
                             deployment_source_branch, deployment_local_git)

    _fill_ftp_publishing_url(cmd, webapp, resource_group_name, name)

    if assign_identities is not None:
        identity = assign_identity(cmd, resource_group_name, name, assign_identities,
                                   role, None, scope)
        webapp.identity = identity

    return webapp

def scale_webapp(cmd, resource_group_name, name, number_of_workers, slot=None):
    return update_site_configs(cmd, resource_group_name, name,
                               number_of_workers=number_of_workers, slot=slot)

def webapp_up(cmd, name, resource_group_name=None, plan=None, location=None, sku=None, dryrun=False, logs=False,  # pylint: disable=too-many-statements,
        launch_browser=False, html=False, environment=None):
    import os
    is_kube = False
    kube_sku=KUBE_DEFAULT_SKU
    KubeEnvironmentProfile = cmd.get_models('KubeEnvironmentProfile')
    if environment is not None:
        if resource_group_name is None:
            raise CLIError("Must provide a resource group where Kube Environment '{}' exists".format(kube_environment))
        kube_id = _resolve_kube_environment_id(cmd.cli_ctx, environment, resource_group_name)
        is_kube = True
        kube_def = KubeEnvironmentProfile(id=kube_id)
        parsed_id = parse_resource_id(kube_id)
        kube_name = parsed_id.get("name")
        kube_rg = parsed_id.get("resource_group")
        if kube_name is not None and kube_rg is not None:
            kube_env = cf_kube_environments(cmd.cli_ctx).get(kube_rg, kube_name)
            if kube_env is not None and  kube_env.location is not None:
                location = kube_env.location.replace(" ", "")
            else:
                raise CLIError("Kube Environment '{}' not found in subscription.".format(kube_id))
    AppServicePlan = cmd.get_models('AppServicePlan')
    src_dir = os.getcwd()
    _src_path_escaped = "{}".format(src_dir.replace(os.sep, os.sep + os.sep))
    client = web_client_factory(cmd.cli_ctx)
    user = get_profile_username()
    _create_new_rg = False
    _create_new_app = does_app_already_exist(cmd, name)
    os_name = detect_os_form_src(src_dir, html)
    lang_details = get_lang_from_content(src_dir, html)
    language = lang_details.get('language')
    # detect the version
    data = get_runtime_version_details(lang_details.get('file_loc'), language, is_kube)
    version_used_create = data.get('to_create')
    detected_version = data.get('detected')
    runtime_version = "{}|{}".format(language, version_used_create) if \
        version_used_create != "-" else version_used_create
    site_config = None
    if not _create_new_app:  # App exists
        # Get the ASP & RG info, if the ASP & RG parameters are provided we use those else we need to find those
        logger.warning("Webapp %s already exists. The command will deploy contents to the existing app.", name)
        app_details = get_app_details(cmd, name, resource_group_name)
        if app_details is None:
            raise CLIError("Unable to retrieve details of the existing app {}. Please check that the app is a part of "
                           "the current subscription".format(name))
        current_rg = app_details.resource_group
        if resource_group_name is not None and (resource_group_name.lower() != current_rg.lower()):
            raise CLIError("The webapp {} exists in ResourceGroup {} and does not match the value entered {}. Please "
                           "re-run command with the correct parameters.". format(name, current_rg, resource_group_name))
        rg_name = resource_group_name or current_rg
        if location is None:
            loc = app_details.location.replace(" ", "").lower()
        else:
            loc = location.replace(" ", "").lower()
        plan_details = parse_resource_id(app_details.server_farm_id)
        current_plan = plan_details['name']
        if plan is not None and current_plan.lower() != plan.lower():
            raise CLIError("The plan name entered {} does not match the plan name that the webapp is hosted in {}."
                           "Please check if you have configured defaults for plan name and re-run command."
                           .format(plan, current_plan))
        plan = plan or plan_details['name']
        plan_info = client.app_service_plans.get(rg_name, plan)
        sku = plan_info.sku.name if isinstance(plan_info, AppServicePlan) else 'Free'
        current_os = 'Linux' if plan_info.reserved else 'Windows'
        # Raise error if current OS of the app is different from the current one
        if current_os.lower() != os_name.lower():
            raise CLIError("The webapp {} is a {} app. The code detected at '{}' will default to "
                           "'{}'. "
                           "Please create a new app to continue this operation.".format(name, current_os, src_dir, os))
        _is_linux = plan_info.reserved
        # for an existing app check if the runtime version needs to be updated
        # Get site config to check the runtime version
        site_config = client.web_apps.get_configuration(rg_name, name)
    else:  # need to create new app, check if we need to use default RG or use user entered values
        logger.warning("webapp %s doesn't exist", name)
        sku = ""
        if is_kube:
            sku = kube_sku
            loc = location
            rg_name = kube_rg
            _create_new_rg = False
            _is_linux = False
            plan = get_kube_plan_to_use(cmd, environment, loc, sku, rg_name, _create_new_rg, plan)
            sku_name = kube_sku
        else:
            sku = get_sku_to_use(src_dir, html, sku)
            loc = set_location(cmd, sku, location)
            rg_name = get_rg_to_use(cmd, user, loc, os_name, resource_group_name)
            _is_linux = os_name.lower() == 'linux'
            _create_new_rg = should_create_new_rg(cmd, rg_name, _is_linux)
            sku_name = get_sku_name(sku)
            plan = get_plan_to_use(cmd, user, os_name, loc, sku_name, rg_name, _create_new_rg, plan)
    dry_run_str = r""" {
                "name" : "%s",
                "appserviceplan" : "%s",
                "resourcegroup" : "%s",
                "sku": "%s",
                "os": "%s",
                "location" : "%s",
                "src_path" : "%s",
                "runtime_version_detected": "%s",
                "runtime_version": "%s"
                }
                """ % (name, plan, rg_name, sku_name, os_name, loc, _src_path_escaped, detected_version,
                       runtime_version)
    create_json = json.loads(dry_run_str)

    if dryrun:
        logger.warning("Web app will be created with the below configuration,re-run command "
                       "without the --dryrun flag to create & deploy a new app")
        return create_json
    if _create_new_rg:
        logger.warning("Creating Resource group '%s' ...", rg_name)
        create_resource_group(cmd, rg_name, location)
        logger.warning("Resource group creation complete")
        # create ASP
        logger.warning("Creating AppServicePlan '%s' ...", plan)
    if is_kube:
        logger.warning("Creating AppServicePlan '%s' with 1 instance count on kube cluster '%s' ...", plan, environment)
    else:
        logger.warning("Creating AppServicePlan '%s' ...", plan)
    # we will always call the ASP create or update API so that in case of re-deployment, if the SKU or plan setting are
    # updated we update those
    create_app_service_plan(cmd, rg_name, plan, _is_linux, hyper_v=False, per_site_scaling=False, sku=sku,
                            number_of_workers=1 if _is_linux else None, location=location, kube_environment=environment)
    logger.warning("Successfully AppServicePlan '%s' ...", plan)
    if _create_new_app:
        logger.warning("Creating webapp '%s' ...", name)
        create_webapp(cmd, rg_name, name, plan, runtime_version if _is_linux or is_kube else None,
                      using_webapp_up=True, language=language)
        if not is_kube:
            _configure_default_logging(cmd, rg_name, name)
        else:
            logger.warning("Successfully App '%s' on Kube Cluster '%s'...", plan, environment)
    else:  # for existing app if we might need to update the stack runtime settings
        if os_name.lower() == 'linux' and site_config.linux_fx_version != runtime_version:
            logger.warning('Updating runtime version from %s to %s',
                           site_config.linux_fx_version, runtime_version)
            update_site_configs(cmd, rg_name, name, linux_fx_version=runtime_version)
        elif os_name.lower() == 'windows' and site_config.windows_fx_version != runtime_version:
            logger.warning('Updating runtime version from %s to %s',
                           site_config.windows_fx_version, runtime_version)
            update_site_configs(cmd, rg_name, name, windows_fx_version=runtime_version)
        create_json['runtime_version'] = runtime_version
    # Zip contents & Deploy
    logger.warning("Creating zip with contents of dir %s ...", src_dir)
    # zip contents & deploy
    zip_file_path = zip_contents_from_dir(src_dir, language, is_kube)
    enable_zip_deploy(cmd, rg_name, name, zip_file_path, is_kube=is_kube)
    # Remove the file after deployment, handling exception if user removed the file manually
    try:
        os.remove(zip_file_path)
    except OSError:
        pass

    if launch_browser:
        logger.warning("Launching app using default browser")
        view_in_browser(cmd, rg_name, name, None, logs)
    else:
        _url = _get_url(cmd, rg_name, name)
        logger.warning("You can launch the app at %s", _url)
        create_json.update({'URL': _url})
    if logs:
        if not is_kube:
            _configure_default_logging(cmd, rg_name, name)
            return get_streaming_log(cmd, rg_name, name)
    if not is_kube:
        with ConfiguredDefaultSetter(cmd.cli_ctx.config, True):
            cmd.cli_ctx.config.set_value('defaults', 'group', rg_name)
            cmd.cli_ctx.config.set_value('defaults', 'sku', sku)
            cmd.cli_ctx.config.set_value('defaults', 'appserviceplan', plan)
            cmd.cli_ctx.config.set_value('defaults', 'location', loc)
            cmd.cli_ctx.config.set_value('defaults', 'web', name)
    return create_json


def show_webapp(cmd, resource_group_name, name, slot=None, app_instance=None):
    webapp = app_instance
    if not app_instance:  # when the routine is invoked as a help method, not through commands
        webapp = _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'get', slot)
    if not webapp:
        raise CLIError("'{}' app doesn't exist".format(name))
    webapp.site_config = _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'get_configuration', slot)
    _rename_server_farm_props(webapp)

    # TODO: get rid of this conditional once the api's are implemented for kubapps
    if KUBE_APP_KIND.lower() not in webapp.kind.lower():
        _fill_ftp_publishing_url(cmd, webapp, resource_group_name, name, slot)

    return webapp


def create_function(cmd, resource_group_name, name, storage_account, plan=None, custom_location=None,
                    os_type=None, functions_version=None, runtime=None, runtime_version=None,
                    consumption_plan_location=None, app_insights=None, app_insights_key=None,
                    disable_app_insights=None, deployment_source_url=None,
                    deployment_source_branch='master', deployment_local_git=None,
                    docker_registry_server_password=None, docker_registry_server_user=None,
                    deployment_container_image_name=None, tags=None,
                    min_worker_count=None, max_worker_count=None):
    # pylint: disable=too-many-statements, too-many-branches
    SkuDescription = cmd.get_models('SkuDescription')
    if functions_version is None:
        logger.warning("No functions version specified so defaulting to 2. In the future, specifying a version will "
                       "be required. To create a 2.x function you would pass in the flag `--functions-version 2`")
        functions_version = '2'
    if deployment_source_url and deployment_local_git:
        raise CLIError('usage error: --deployment-source-url <url> | --deployment-local-git')

    if not plan and not consumption_plan_location and not custom_location:
        raise RequiredArgumentMissingError("Either Plan, Consumption Plan or Custom Location must be specified")

    if consumption_plan_location and custom_location:
        raise MutuallyExclusiveArgumentError("Consumption Plan and Custom Location cannot be used together")

    if consumption_plan_location and plan:
        raise MutuallyExclusiveArgumentError("Consumption Plan and Plan cannot be used together")

    SiteConfig, Site, NameValuePair = cmd.get_models('SiteConfig', 'Site', 'NameValuePair')
    docker_registry_server_url = parse_docker_image_name(deployment_container_image_name)

    site_config = SiteConfig(app_settings=[])
    functionapp_def = Site(location=None, site_config=site_config, tags=tags)
    client = web_client_factory(cmd.cli_ctx)
    plan_info = None
    if runtime is not None:
        runtime = runtime.lower()

    if consumption_plan_location:
        locations = list_consumption_locations(cmd)
        location = next((l for l in locations if l['name'].lower() == consumption_plan_location.lower()), None)
        if location is None:
            raise CLIError("Location is invalid. Use: az functionapp list-consumption-locations")
        functionapp_def.location = consumption_plan_location
        functionapp_def.kind = 'functionapp'
        # if os_type is None, the os type is windows
        is_linux = os_type and os_type.lower() == 'linux'

    else:  # apps with SKU based plan
        _should_create_new_plan = _should_create_new_appservice_plan_for_k8se(cmd, name, custom_location, plan, resource_group_name)
        if _should_create_new_plan:
            plan = generate_default_app_service_plan_name(name)
            logger.warning("Plan not specified. Creating Plan '%s' with sku '%s'", plan, KUBE_DEFAULT_SKU)
            create_app_service_plan(cmd=cmd, resource_group_name=resource_group_name,
                name=plan, is_linux=True, hyper_v=False, custom_location=custom_location, per_site_scaling=True, number_of_workers=1)

        if custom_location and plan:
            if not _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location, plan):
                raise ValidationError("Custom location's kube environment and App Service Plan's kube environment don't match")
        elif custom_location and not plan:
            app_details = get_app_details(cmd, name, resource_group_name)
            if app_details is not None:
                plan = app_details.server_farm_id

        if is_valid_resource_id(plan):
            parse_result = parse_resource_id(plan)
            plan_info = client.app_service_plans.get(parse_result['resource_group'], parse_result['name'])
        else:
            plan_info = client.app_service_plans.get(resource_group_name, plan)
        if not plan_info:
            raise CLIError("The plan '{}' doesn't exist".format(plan))
        location = plan_info.location
        is_linux = plan_info.reserved
        functionapp_def.server_farm_id = plan_info.id
        functionapp_def.location = location

    is_kube = False
    if custom_location or plan_info.kind.upper() == KUBE_ASP_KIND.upper() or (isinstance(plan_info.sku, SkuDescription) and plan_info.sku.name.upper() == KUBE_DEFAULT_SKU):
        is_kube = True

    if is_kube:
        if min_worker_count is not None:
            site_config.number_of_workers = min_worker_count

        if max_worker_count is not None:
            site_config.app_settings.append(NameValuePair(name='K8SE_APP_MAX_INSTANCE_COUNT', value=max_worker_count))

    if is_linux and not runtime and (consumption_plan_location or not deployment_container_image_name):
        raise CLIError(
            "usage error: --runtime RUNTIME required for linux functions apps without custom image.")

    if runtime:
        if is_linux and runtime not in LINUX_RUNTIMES:
            raise CLIError("usage error: Currently supported runtimes (--runtime) in linux function apps are: {}."
                           .format(', '.join(LINUX_RUNTIMES)))
        if not is_linux and runtime not in WINDOWS_RUNTIMES:
            raise CLIError("usage error: Currently supported runtimes (--runtime) in windows function apps are: {}."
                           .format(', '.join(WINDOWS_RUNTIMES)))
        site_config.app_settings.append(NameValuePair(name='FUNCTIONS_WORKER_RUNTIME', value=runtime))

    if runtime_version is not None:
        if runtime is None:
            raise CLIError('Must specify --runtime to use --runtime-version')
        allowed_versions = FUNCTIONS_VERSION_TO_SUPPORTED_RUNTIME_VERSIONS[functions_version][runtime]
        if runtime_version not in allowed_versions:
            if runtime == 'dotnet':
                raise CLIError('--runtime-version is not supported for --runtime dotnet. Dotnet version is determined '
                               'by --functions-version. Dotnet version {} is not supported by Functions version {}.'
                               .format(runtime_version, functions_version))
            raise CLIError('--runtime-version {} is not supported for the selected --runtime {} and '
                           '--functions-version {}. Supported versions are: {}.'
                           .format(runtime_version, runtime, functions_version, ', '.join(allowed_versions)))
        if runtime == 'dotnet':
            logger.warning('--runtime-version is not supported for --runtime dotnet. Dotnet version is determined by '
                           '--functions-version. Dotnet version will be %s for this function app.',
                           FUNCTIONS_VERSION_TO_DEFAULT_RUNTIME_VERSION[functions_version][runtime])

    con_string = _validate_and_get_connection_string(cmd.cli_ctx, resource_group_name, storage_account)

    if is_kube:
        functionapp_def.kind = KUBE_FUNCTION_APP_KIND
        functionapp_def.reserved = True
        site_config.app_settings.append(NameValuePair(name='WEBSITES_PORT', value='80'))
        site_config.app_settings.append(NameValuePair(name='MACHINEKEY_DecryptionKey',
                                                      value=str(hexlify(urandom(32)).decode()).upper()))
        if deployment_container_image_name:
            functionapp_def.kind = KUBE_FUNCTION_CONTAINER_APP_KIND
            site_config.app_settings.append(NameValuePair(name='DOCKER_CUSTOM_IMAGE_NAME',
                                                          value=deployment_container_image_name))
            site_config.app_settings.append(NameValuePair(name='FUNCTION_APP_EDIT_MODE', value='readOnly'))
            site_config.linux_fx_version = _format_fx_version(deployment_container_image_name)
            site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_URL', value=docker_registry_server_url))
            if docker_registry_server_user is not None and docker_registry_server_password is not None:
                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_USERNAME', value=docker_registry_server_user))
                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_PASSWORD', value=docker_registry_server_password))
        else:
            site_config.app_settings.append(NameValuePair(name='WEBSITES_ENABLE_APP_SERVICE_STORAGE', value='true'))
            site_config.linux_fx_version = _get_linux_fx_kube_functionapp(runtime, runtime_version)
    elif is_linux:
        functionapp_def.kind = 'functionapp,linux'
        functionapp_def.reserved = True
        is_consumption = consumption_plan_location is not None
        if not is_consumption:
            site_config.app_settings.append(NameValuePair(name='MACHINEKEY_DecryptionKey',
                                                          value=str(hexlify(urandom(32)).decode()).upper()))
            if deployment_container_image_name:
                functionapp_def.kind = 'functionapp,linux,container'
                site_config.app_settings.append(NameValuePair(name='DOCKER_CUSTOM_IMAGE_NAME',
                                                              value=deployment_container_image_name))
                site_config.app_settings.append(NameValuePair(name='FUNCTION_APP_EDIT_MODE', value='readOnly'))
                site_config.app_settings.append(NameValuePair(name='WEBSITES_ENABLE_APP_SERVICE_STORAGE',
                                                              value='false'))
                site_config.linux_fx_version = _format_fx_version(deployment_container_image_name)
            else:
                site_config.app_settings.append(NameValuePair(name='WEBSITES_ENABLE_APP_SERVICE_STORAGE',
                                                              value='true'))
                if runtime not in FUNCTIONS_VERSION_TO_SUPPORTED_RUNTIME_VERSIONS[functions_version]:
                    raise CLIError("An appropriate linux image for runtime:'{}', "
                                   "functions_version: '{}' was not found".format(runtime, functions_version))
        if deployment_container_image_name is None:
            site_config.linux_fx_version = _get_linux_fx_functionapp(functions_version, runtime, runtime_version)
    else:
        functionapp_def.kind = 'functionapp'
        if runtime == "java":
            site_config.java_version = _get_java_version_functionapp(functions_version, runtime_version)

    # adding appsetting to site to make it a function
    site_config.app_settings.append(NameValuePair(name='FUNCTIONS_EXTENSION_VERSION',
                                                  value=_get_extension_version_functionapp(functions_version)))
    site_config.app_settings.append(NameValuePair(name='AzureWebJobsStorage', value=con_string))
    site_config.app_settings.append(NameValuePair(name='AzureWebJobsDashboard', value=con_string))
    site_config.app_settings.append(NameValuePair(name='WEBSITE_NODE_DEFAULT_VERSION',
                                                  value=_get_website_node_version_functionapp(functions_version,
                                                                                              runtime,
                                                                                              runtime_version)))

    # If plan is not consumption or elastic premium, we need to set always on
    if consumption_plan_location is None and not is_plan_elastic_premium(cmd, plan_info):
        site_config.always_on = True

    # If plan is elastic premium or windows consumption, we need these app settings
    is_windows_consumption = consumption_plan_location is not None and not is_linux
    if is_plan_elastic_premium(cmd, plan_info) or is_windows_consumption:
        site_config.app_settings.append(NameValuePair(name='WEBSITE_CONTENTAZUREFILECONNECTIONSTRING',
                                                      value=con_string))
        site_config.app_settings.append(NameValuePair(name='WEBSITE_CONTENTSHARE', value=name.lower()))

    create_app_insights = False

    if app_insights_key is not None:
        site_config.app_settings.append(NameValuePair(name='APPINSIGHTS_INSTRUMENTATIONKEY',
                                                      value=app_insights_key))
    elif app_insights is not None:
        instrumentation_key = get_app_insights_key(cmd.cli_ctx, resource_group_name, app_insights)
        site_config.app_settings.append(NameValuePair(name='APPINSIGHTS_INSTRUMENTATIONKEY',
                                                      value=instrumentation_key))
    elif not disable_app_insights:
        create_app_insights = True

    poller = client.web_apps.create_or_update(resource_group_name, name, functionapp_def)
    functionapp = LongRunningOperation(cmd.cli_ctx)(poller)

    if consumption_plan_location and is_linux:
        logger.warning("Your Linux function app '%s', that uses a consumption plan has been successfully "
                       "created but is not active until content is published using "
                       "Azure Portal or the Functions Core Tools.", name)
    else:
        _set_remote_or_local_git(cmd, functionapp, resource_group_name, name, deployment_source_url,
                                 deployment_source_branch, deployment_local_git)

    if create_app_insights:
        try:
            try_create_application_insights(cmd, functionapp)
        except Exception:  # pylint: disable=broad-except
            logger.warning('Error while trying to create and configure an Application Insights for the Function App. '
                           'Please use the Azure Portal to create and configure the Application Insights, if needed.')

    if deployment_container_image_name:
        update_container_settings_functionapp(cmd, resource_group_name, name, docker_registry_server_url,
                                              deployment_container_image_name, docker_registry_server_user,
                                              docker_registry_server_password)

    return functionapp


def update_container_settings_functionapp(cmd, resource_group_name, name, docker_registry_server_url=None,
                                          docker_custom_image_name=None, docker_registry_server_user=None,
                                          docker_registry_server_password=None, slot=None):
    return update_container_settings(cmd, resource_group_name, name, docker_registry_server_url,
                                     docker_custom_image_name, docker_registry_server_user, None,
                                     docker_registry_server_password, multicontainer_config_type=None,
                                     multicontainer_config_file=None, slot=slot)


def update_container_settings(cmd, resource_group_name, name, docker_registry_server_url=None,
                              docker_custom_image_name=None, docker_registry_server_user=None,
                              websites_enable_app_service_storage=None, docker_registry_server_password=None,
                              multicontainer_config_type=None, multicontainer_config_file=None, slot=None):
    settings = []
    if docker_registry_server_url is not None:
        settings.append('DOCKER_REGISTRY_SERVER_URL=' + docker_registry_server_url)

    if (not docker_registry_server_user and not docker_registry_server_password and
            docker_registry_server_url and '.azurecr.io' in docker_registry_server_url):
        logger.warning('No credential was provided to access Azure Container Registry. Trying to look up...')
        parsed = urlparse(docker_registry_server_url)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]
        try:
            docker_registry_server_user, docker_registry_server_password = _get_acr_cred(cmd.cli_ctx, registry_name)
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Retrieving credentials failed with an exception:'%s'", ex)  # consider throw if needed

    if docker_registry_server_user is not None:
        settings.append('DOCKER_REGISTRY_SERVER_USERNAME=' + docker_registry_server_user)
    if docker_registry_server_password is not None:
        settings.append('DOCKER_REGISTRY_SERVER_PASSWORD=' + docker_registry_server_password)
    if docker_custom_image_name is not None:
        _add_fx_version(cmd, resource_group_name, name, docker_custom_image_name, slot)
    if websites_enable_app_service_storage:
        settings.append('WEBSITES_ENABLE_APP_SERVICE_STORAGE=' + websites_enable_app_service_storage)

    if docker_registry_server_user or docker_registry_server_password or docker_registry_server_url or websites_enable_app_service_storage:  # pylint: disable=line-too-long
        update_app_settings(cmd, resource_group_name, name, settings, slot)
    settings = get_app_settings(cmd, resource_group_name, name, slot)

    if multicontainer_config_file and multicontainer_config_type:
        encoded_config_file = _get_linux_multicontainer_encoded_config_from_file(multicontainer_config_file)
        linux_fx_version = _format_fx_version(encoded_config_file, multicontainer_config_type)
        update_site_configs(cmd, resource_group_name, name, linux_fx_version=linux_fx_version, slot=slot)
    elif multicontainer_config_file or multicontainer_config_type:
        logger.warning('Must change both settings --multicontainer-config-file FILE --multicontainer-config-type TYPE')

    return _mask_creds_related_appsettings(_filter_for_container_settings(cmd, resource_group_name, name, settings,
                                                                          slot=slot))


def try_create_application_insights(cmd, functionapp):
    creation_failed_warn = 'Unable to create the Application Insights for the Function App. ' \
                           'Please use the Azure Portal to manually create and configure the Application Insights, ' \
                           'if needed.'

    ai_resource_group_name = functionapp.resource_group
    ai_name = functionapp.name
    ai_location = functionapp.location

    app_insights_client = get_mgmt_service_client(cmd.cli_ctx, ApplicationInsightsManagementClient)
    ai_properties = {
        "name": ai_name,
        "location": ai_location,
        "kind": "web",
        "properties": {
            "Application_Type": "web"
        }
    }
    appinsights = app_insights_client.components.create_or_update(ai_resource_group_name, ai_name, ai_properties)
    if appinsights is None or appinsights.instrumentation_key is None:
        logger.warning(creation_failed_warn)
        return

    # We make this success message as a warning to no interfere with regular JSON output in stdout
    logger.warning('Application Insights \"%s\" was created for this Function App. '
                   'You can visit https://portal.azure.com/#resource%s/overview to view your '
                   'Application Insights component', appinsights.name, appinsights.id)

    update_app_settings(cmd, functionapp.resource_group, functionapp.name,
                        ['APPINSIGHTS_INSTRUMENTATIONKEY={}'.format(appinsights.instrumentation_key)])


def update_app_settings(cmd, resource_group_name, name, settings=None, slot=None, slot_settings=None):
    if not settings and not slot_settings:
        raise CLIError('Usage Error: --settings |--slot-settings')

    settings = settings or []
    slot_settings = slot_settings or []

    app_settings = _generic_site_operation(cmd.cli_ctx, resource_group_name, name,
                                           'list_application_settings', slot)
    result, slot_result = {}, {}
    # pylint: disable=too-many-nested-blocks
    for src, dest in [(settings, result), (slot_settings, slot_result)]:
        for s in src:
            try:
                temp = shell_safe_json_parse(s)
                if isinstance(temp, list):  # a bit messy, but we'd like accept the output of the "list" command
                    for t in temp:
                        if t.get('slotSetting', True):
                            slot_result[t['name']] = t['value']
                            # Mark each setting as the slot setting
                        else:
                            result[t['name']] = t['value']
                else:
                    dest.update(temp)
            except CLIError:
                setting_name, value = s.split('=', 1)
                dest[setting_name] = value

    result.update(slot_result)
    for setting_name, value in result.items():
        app_settings.properties[setting_name] = value
    client = web_client_factory(cmd.cli_ctx)

    result = _generic_settings_operation(cmd.cli_ctx, resource_group_name, name,
                                         'update_application_settings',
                                         app_settings.properties, slot, client)

    app_settings_slot_cfg_names = []
    if slot_result:
        new_slot_setting_names = slot_result.keys()
        slot_cfg_names = client.web_apps.list_slot_configuration_names(resource_group_name, name)
        slot_cfg_names.app_setting_names = slot_cfg_names.app_setting_names or []
        slot_cfg_names.app_setting_names += new_slot_setting_names
        app_settings_slot_cfg_names = slot_cfg_names.app_setting_names
        client.web_apps.update_slot_configuration_names(resource_group_name, name, slot_cfg_names)

    return _build_app_settings_output(result.properties, app_settings_slot_cfg_names)


# for any modifications to the non-optional parameters, adjust the reflection logic accordingly
# in the method
# pylint: disable=unused-argument
def update_site_configs(cmd, resource_group_name, name, slot=None, number_of_workers=None, linux_fx_version=None,
                        windows_fx_version=None, pre_warmed_instance_count=None, php_version=None,
                        python_version=None, net_framework_version=None,
                        java_version=None, java_container=None, java_container_version=None,
                        remote_debugging_enabled=None, web_sockets_enabled=None,
                        always_on=None, auto_heal_enabled=None,
                        use32_bit_worker_process=None,
                        min_tls_version=None,
                        http20_enabled=None,
                        app_command_line=None,
                        ftps_state=None,
                        generic_configurations=None):
    configs = get_site_configs(cmd, resource_group_name, name, slot)
    if number_of_workers is not None:
        number_of_workers = validate_range_of_int_flag('--number-of-workers', number_of_workers, min_val=0, max_val=20)
    if linux_fx_version:
        if linux_fx_version.strip().lower().startswith('docker|'):
            update_app_settings(cmd, resource_group_name, name, ["WEBSITES_ENABLE_APP_SERVICE_STORAGE=false"])
        else:
            delete_app_settings(cmd, resource_group_name, name, ["WEBSITES_ENABLE_APP_SERVICE_STORAGE"])

    if pre_warmed_instance_count is not None:
        pre_warmed_instance_count = validate_range_of_int_flag('--prewarmed-instance-count', pre_warmed_instance_count,
                                                               min_val=0, max_val=20)
    import inspect
    frame = inspect.currentframe()
    bool_flags = ['remote_debugging_enabled', 'web_sockets_enabled', 'always_on',
                  'auto_heal_enabled', 'use32_bit_worker_process', 'http20_enabled']
    int_flags = ['pre_warmed_instance_count', 'number_of_workers']
    # note: getargvalues is used already in azure.cli.core.commands.
    # and no simple functional replacement for this deprecating method for 3.5
    args, _, _, values = inspect.getargvalues(frame)  # pylint: disable=deprecated-method

    for arg in args[3:]:
        if arg in int_flags and values[arg] is not None:
            values[arg] = validate_and_convert_to_int(arg, values[arg])
        if arg != 'generic_configurations' and values.get(arg, None):
            setattr(configs, arg, values[arg] if arg not in bool_flags else values[arg] == 'true')

    generic_configurations = generic_configurations or []

    # https://github.com/Azure/azure-cli/issues/14857
    updating_ip_security_restrictions = False

    result = {}
    for s in generic_configurations:
        try:
            json_object = get_json_object(s)
            for config_name in json_object:
                if config_name.lower() == 'ip_security_restrictions':
                    updating_ip_security_restrictions = True
            result.update(json_object)
        except CLIError:
            config_name, value = s.split('=', 1)
            result[config_name] = value

    for config_name, value in result.items():
        if config_name.lower() == 'ip_security_restrictions':
            updating_ip_security_restrictions = True
        setattr(configs, config_name, value)

    if not updating_ip_security_restrictions:
        setattr(configs, 'ip_security_restrictions', None)

    return _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'update_configuration', slot, configs)


def delete_app_settings(cmd, resource_group_name, name, setting_names, slot=None):
    app_settings = _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'list_application_settings', slot)
    client = web_client_factory(cmd.cli_ctx)

    slot_cfg_names = client.web_apps.list_slot_configuration_names(resource_group_name, name)
    is_slot_settings = False
    for setting_name in setting_names:
        app_settings.properties.pop(setting_name, None)
        if slot_cfg_names.app_setting_names and setting_name in slot_cfg_names.app_setting_names:
            slot_cfg_names.app_setting_names.remove(setting_name)
            is_slot_settings = True

    if is_slot_settings:
        client.web_apps.update_slot_configuration_names(resource_group_name, name, slot_cfg_names)

    result = _generic_settings_operation(cmd.cli_ctx, resource_group_name, name,
                                         'update_application_settings',
                                         app_settings.properties, slot, client)

    return _build_app_settings_output(result.properties, slot_cfg_names.app_setting_names)


def config_source_control(cmd, resource_group_name, name, repo_url, repository_type='git', branch=None,  # pylint: disable=too-many-locals
                          manual_integration=None, git_token=None, slot=None, cd_app_type=None,
                          app_working_dir=None, nodejs_task_runner=None, python_framework=None,
                          python_version=None, cd_account_create=None, cd_project_url=None, test=None,
                          slot_swap=None, private_repo_username=None, private_repo_password=None):
    client = web_client_factory(cmd.cli_ctx)
    location = _get_location_from_webapp(client, resource_group_name, name)

    if cd_project_url:
        # Add default values
        cd_app_type = 'AspNet' if cd_app_type is None else cd_app_type
        python_framework = 'Django' if python_framework is None else python_framework
        python_version = 'Python 3.5.3 x86' if python_version is None else python_version

        webapp_list = None if test is None else list_webapp(resource_group_name)
        vsts_provider = VstsContinuousDeliveryProvider()
        cd_app_type_details = {
            'cd_app_type': cd_app_type,
            'app_working_dir': app_working_dir,
            'nodejs_task_runner': nodejs_task_runner,
            'python_framework': python_framework,
            'python_version': python_version
        }
        try:
            status = vsts_provider.setup_continuous_delivery(cmd.cli_ctx, resource_group_name, name, repo_url,
                                                             branch, git_token, slot_swap, cd_app_type_details,
                                                             cd_project_url, cd_account_create, location, test,
                                                             private_repo_username, private_repo_password, webapp_list)
        except RuntimeError as ex:
            raise CLIError(ex)
        logger.warning(status.status_message)
        return status
    non_vsts_params = [cd_app_type, app_working_dir, nodejs_task_runner, python_framework,
                       python_version, cd_account_create, test, slot_swap]
    if any(non_vsts_params):
        raise CLIError('Following parameters are of no use when cd_project_url is None: ' +
                       'cd_app_type, app_working_dir, nodejs_task_runner, python_framework,' +
                       'python_version, cd_account_create, test, slot_swap')
    from azure.mgmt.web.models import SiteSourceControl, SourceControl
    if git_token:
        sc = SourceControl(location=location, source_control_name='GitHub', token=git_token)
        client.update_source_control('GitHub', sc)

    source_control = SiteSourceControl(location=location, repo_url=repo_url, branch=branch,
                                       is_manual_integration=manual_integration,
                                       is_mercurial=(repository_type != 'git'))

    # SCC config can fail if previous commands caused SCMSite shutdown, so retry here.
    for i in range(5):
        try:
            poller = _generic_site_operation(cmd.cli_ctx, resource_group_name, name,
                                             'create_or_update_source_control',
                                             slot, source_control)
            return LongRunningOperation(cmd.cli_ctx)(poller)
        except Exception as ex:  # pylint: disable=broad-except
            import re
            ex = ex_handler_factory(no_throw=True)(ex)
            # for non server errors(50x), just throw; otherwise retry 4 times
            if i == 4 or not re.findall(r'\(50\d\)', str(ex)):
                raise
            logger.warning('retrying %s/4', i + 1)
            time.sleep(5)   # retry in a moment


def list_publish_profiles(cmd, resource_group_name, name, slot=None, xml=False):
    import xmltodict

    content = _generic_site_operation(cmd.cli_ctx, resource_group_name, name,
                                      'list_publishing_profile_xml_with_secrets', slot)
    full_xml = ''
    for f in content:
        full_xml += f.decode()

    if not xml:
        profiles = xmltodict.parse(full_xml, xml_attribs=True)['publishData']['publishProfile']
        converted = []

        if not isinstance(profiles, list):
            profiles = [profiles]

        for profile in profiles:
            new = {}
            for key in profile:
                # strip the leading '@' xmltodict put in for attributes
                new[key.lstrip('@')] = profile[key]
            converted.append(new)
        return converted
    cmd.cli_ctx.invocation.data['output'] = 'tsv'
    return full_xml


# private helpers

def _resolve_kube_environment_id(cli_ctx, kube_environment, resource_group_name):
    if is_valid_resource_id(kube_environment):
        return kube_environment

    from msrestazure.tools import resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id
    return resource_id(
        subscription=get_subscription_id(cli_ctx),
        resource_group=resource_group_name,
        namespace='Microsoft.Web',
        type='kubeEnvironments',
        name=kube_environment)


def _get_linux_fx_functionapp(functions_version, runtime, runtime_version):
    if runtime_version is None:
        runtime_version = FUNCTIONS_VERSION_TO_DEFAULT_RUNTIME_VERSION[functions_version][runtime]
    if runtime == 'dotnet':
        runtime_version = DOTNET_RUNTIME_VERSION_TO_DOTNET_LINUX_FX_VERSION[runtime_version]
    else:
        runtime = runtime.upper()
    return '{}|{}'.format(runtime, runtime_version)


def _get_linux_fx_kube_functionapp(runtime, runtime_version):
    if runtime.upper() == "DOTNET":
        runtime = "DOTNETCORE"
    return '{}|{}'.format(runtime.upper(), runtime_version)


def _get_website_node_version_functionapp(functions_version, runtime, runtime_version):
    if runtime is None or runtime != 'node':
        return FUNCTIONS_VERSION_TO_DEFAULT_NODE_VERSION[functions_version]
    if runtime_version is not None:
        return '~{}'.format(runtime_version)
    return FUNCTIONS_VERSION_TO_DEFAULT_NODE_VERSION[functions_version]


def _get_java_version_functionapp(functions_version, runtime_version):
    if runtime_version is None:
        runtime_version = FUNCTIONS_VERSION_TO_DEFAULT_RUNTIME_VERSION[functions_version]['java']
    if runtime_version == '8':
        return '1.8'
    return runtime_version


def _set_remote_or_local_git(cmd, webapp, resource_group_name, name, deployment_source_url=None,
                             deployment_source_branch='master', deployment_local_git=None):
    if deployment_source_url:
        logger.warning("Linking to git repository '%s'", deployment_source_url)
        try:
            config_source_control(cmd, resource_group_name, name, deployment_source_url, 'git',
                                  deployment_source_branch, manual_integration=True)
        except Exception as ex:  # pylint: disable=broad-except
            ex = ex_handler_factory(no_throw=True)(ex)
            logger.warning("Link to git repository failed due to error '%s'", ex)

    if deployment_local_git:
        local_git_info = enable_local_git(cmd, resource_group_name, name)
        logger.warning("Local git is configured with url of '%s'", local_git_info['url'])
        setattr(webapp, 'deploymentLocalGitUrl', local_git_info['url'])


def _add_fx_version(cmd, resource_group_name, name, custom_image_name, slot=None):
    fx_version = _format_fx_version(custom_image_name)
    web_app = get_webapp(cmd, resource_group_name, name, slot)
    if not web_app:
        raise CLIError("'{}' app doesn't exist in resource group {}".format(name, resource_group_name))
    linux_fx = fx_version if (web_app.reserved or not web_app.is_xenon) else None
    windows_fx = fx_version if web_app.is_xenon else None
    return update_site_configs(cmd, resource_group_name, name,
                               linux_fx_version=linux_fx, windows_fx_version=windows_fx, slot=slot)


@retryable_method(3, 5)
def _get_app_settings_from_scm(cmd, resource_group_name, name, slot=None):
    scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    settings_url = '{}/api/settings'.format(scm_url)
    username, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    headers = {
        'Content-Type': 'application/octet-stream',
        'Cache-Control': 'no-cache',
        'User-Agent': get_az_user_agent()
    }

    import requests
    response = requests.get(settings_url, headers=headers, auth=(username, password), timeout=3)

    return response.json() or {}


# Check if the app setting is propagated to the Kudu site correctly by calling api/settings endpoint
# should_have [] is a list of app settings which are expected to be set
# should_not_have [] is a list of app settings which are expected to be absent
# should_contain {} is a dictionary of app settings which are expected to be set with precise values
# Return True if validation succeeded
def validate_app_settings_in_scm(cmd, resource_group_name, name, slot=None,
                                 should_have=None, should_not_have=None, should_contain=None):
    scm_settings = _get_app_settings_from_scm(cmd, resource_group_name, name, slot)
    scm_setting_keys = set(scm_settings.keys())

    if should_have and not set(should_have).issubset(scm_setting_keys):
        return False

    if should_not_have and set(should_not_have).intersection(scm_setting_keys):
        return False

    temp_setting = scm_settings.copy()
    temp_setting.update(should_contain or {})
    if temp_setting != scm_settings:
        return False

    return True


def remove_remote_build_app_settings(cmd, resource_group_name, name, slot):
    settings = get_app_settings(cmd, resource_group_name, name, slot)
    scm_do_build_during_deployment = None

    app_settings_should_contain = {}

    for keyval in settings:
        value = keyval['value'].lower()
        if keyval['name'] == 'SCM_DO_BUILD_DURING_DEPLOYMENT':
            scm_do_build_during_deployment = value in ('true', '1')

    if scm_do_build_during_deployment is not False:
        logger.warning("Setting SCM_DO_BUILD_DURING_DEPLOYMENT to false")
        update_app_settings(cmd, resource_group_name, name, [
            "SCM_DO_BUILD_DURING_DEPLOYMENT=false"
        ], slot)
        app_settings_should_contain['SCM_DO_BUILD_DURING_DEPLOYMENT'] = 'false'

    # Wait for scm site to get the latest app settings
    if app_settings_should_contain:
        logger.warning("Waiting SCM site to be updated with the latest app settings")
        scm_is_up_to_date = False
        retries = 10
        while not scm_is_up_to_date and retries >= 0:
            scm_is_up_to_date = validate_app_settings_in_scm(
                cmd, resource_group_name, name, slot,
                should_contain=app_settings_should_contain)
            retries -= 1
            time.sleep(5)

        if retries < 0:
            logger.warning("App settings may not be propagated to the SCM site")


def add_remote_build_app_settings(cmd, resource_group_name, name, slot):
    settings = get_app_settings(cmd, resource_group_name, name, slot)
    scm_do_build_during_deployment = None
    website_run_from_package = None
    enable_oryx_build = None

    app_settings_should_not_have = []
    app_settings_should_contain = {}

    for keyval in settings:
        value = keyval['value'].lower()
        if keyval['name'] == 'SCM_DO_BUILD_DURING_DEPLOYMENT':
            scm_do_build_during_deployment = value in ('true', '1')
        if keyval['name'] == 'WEBSITE_RUN_FROM_PACKAGE':
            website_run_from_package = value
        if keyval['name'] == 'ENABLE_ORYX_BUILD':
            enable_oryx_build = value

    if scm_do_build_during_deployment is not True:
        logger.warning("Setting SCM_DO_BUILD_DURING_DEPLOYMENT to true")
        update_app_settings(cmd, resource_group_name, name, [
            "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
        ], slot)
        app_settings_should_contain['SCM_DO_BUILD_DURING_DEPLOYMENT'] = 'true'

    if website_run_from_package:
        logger.warning("Removing WEBSITE_RUN_FROM_PACKAGE app setting")
        delete_app_settings(cmd, resource_group_name, name, [
            "WEBSITE_RUN_FROM_PACKAGE"
        ], slot)
        app_settings_should_not_have.append('WEBSITE_RUN_FROM_PACKAGE')

    if enable_oryx_build:
        logger.warning("Removing ENABLE_ORYX_BUILD app setting")
        delete_app_settings(cmd, resource_group_name, name, [
            "ENABLE_ORYX_BUILD"
        ], slot)
        app_settings_should_not_have.append('ENABLE_ORYX_BUILD')

    # Wait for scm site to get the latest app settings
    if app_settings_should_not_have or app_settings_should_contain:
        logger.warning("Waiting SCM site to be updated with the latest app settings")
        scm_is_up_to_date = False
        retries = 10
        while not scm_is_up_to_date and retries >= 0:
            scm_is_up_to_date = validate_app_settings_in_scm(
                cmd, resource_group_name, name, slot,
                should_contain=app_settings_should_contain,
                should_not_have=app_settings_should_not_have)
            retries -= 1
            time.sleep(5)

        if retries < 0:
            logger.warning("App settings may not be propagated to the SCM site.")


def enable_zip_deploy_functionapp(cmd, resource_group_name, name, src, build_remote=False, timeout=None, slot=None):
    client = web_client_factory(cmd.cli_ctx)
    app = client.web_apps.get(resource_group_name, name)
    if app is None:
        raise CLIError('The function app \'{}\' was not found in resource group \'{}\'. '
                       'Please make sure these values are correct.'.format(name, resource_group_name))
    parse_plan_id = parse_resource_id(app.server_farm_id)
    plan_info = None
    retry_delay = 10  # seconds
    # We need to retry getting the plan because sometimes if the plan is created as part of function app,
    # it can take a couple of tries before it gets the plan
    for _ in range(5):
        plan_info = client.app_service_plans.get(parse_plan_id['resource_group'],
                                                 parse_plan_id['name'])
        if plan_info is not None:
            break
        time.sleep(retry_delay)

    if build_remote and not app.reserved:
        raise CLIError('Remote build is only available on Linux function apps')

    is_consumption = is_plan_consumption(cmd, plan_info)
    if (not build_remote) and is_consumption and app.reserved:
        return upload_zip_to_storage(cmd, resource_group_name, name, src, slot)
    if build_remote:
        add_remote_build_app_settings(cmd, resource_group_name, name, slot)
    else:
        remove_remote_build_app_settings(cmd, resource_group_name, name, slot)

    return enable_zip_deploy(cmd, resource_group_name, name, src, timeout, slot)


def enable_zip_deploy_webapp(cmd, resource_group_name, name, src, timeout=None, slot=None, is_kube=False):
    return enable_zip_deploy(cmd, resource_group_name, name, src, timeout=timeout, slot=slot, is_kube=is_kube)


def enable_zip_deploy(cmd, resource_group_name, name, src, timeout=None, slot=None, is_kube=False):
    logger.warning("Getting scm site credentials for zip deployment")
    user_name, password = _get_site_credential(cmd.cli_ctx, resource_group_name, name, slot)
    # Wait for a few seconds for envoy changes to propogate, for a kube app
    if is_kube:
        time.sleep(7)
    try:
        scm_url = _get_scm_url(cmd, resource_group_name, name, slot)
    except ValueError:
        raise CLIError('Failed to fetch scm url for function app')

    zip_url = scm_url + '/api/zipdeploy?isAsync=true'
    deployment_status_url = scm_url + '/api/deployments/latest'

    import urllib3
    authorization = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(user_name, password))
    headers = authorization
    headers['Content-Type'] = 'application/octet-stream'
    headers['Cache-Control'] = 'no-cache'
    headers['User-Agent'] = get_az_user_agent()

    import requests
    import os
    from azure.cli.core.util import should_disable_connection_verify
    # Read file content
    with open(os.path.realpath(os.path.expanduser(src)), 'rb') as fs:
        zip_content = fs.read()
        logger.warning("Starting zip deployment. This operation can take a while to complete ...")
        res = requests.post(zip_url, data=zip_content, headers=headers, verify=not should_disable_connection_verify())
        logger.warning("Deployment endpoint responded with status code %d", res.status_code)

        if is_kube and res.status_code != 202 and res.status_code != 409:
            logger.warning('Something went wrong. It may take a few seconds for a new deployment to reflect on kube cluster. Retrying deployment...')
            time.sleep(10)   # retry in a moment 
            res = requests.post(zip_url, data=zip_content, headers=headers, verify=not should_disable_connection_verify())
            logger.warning("Deployment endpoint responded with status code %d", res.status_code)

    # check if there's an ongoing process
    if res.status_code == 409:
        raise CLIError("There may be an ongoing deployment or your app setting has WEBSITE_RUN_FROM_PACKAGE. "
                       "Please track your deployment in {} and ensure the WEBSITE_RUN_FROM_PACKAGE app setting "
                       "is removed.".format(deployment_status_url))


    # check the status of async deployment
    response = _check_zip_deployment_status(cmd, resource_group_name, name, deployment_status_url,
                                            authorization, timeout)
    return response


def _get_scm_url(cmd, resource_group_name, name, slot=None):
    from azure.mgmt.web.models import HostType
    webapp = show_webapp(cmd, resource_group_name, name, slot=slot)
    for host in webapp.host_name_ssl_states or []:
        if host.host_type == HostType.repository:
            return "https://{}".format(host.name)

    # this should not happen, but throw anyway
    raise ValueError('Failed to retrieve Scm Uri')


def _check_zip_deployment_status(cmd, rg_name, name, deployment_status_url, authorization, timeout=None):
    import requests
    from azure.cli.core.util import should_disable_connection_verify
    total_trials = (int(timeout) // 2) if timeout else 450
    num_trials = 0
    while num_trials < total_trials:
        time.sleep(2)
        response = requests.get(deployment_status_url, headers=authorization,
                                verify=not should_disable_connection_verify())
        try:
            res_dict = response.json()
        except json.decoder.JSONDecodeError:
            logger.warning("Deployment status endpoint %s returns malformed data. Retrying...", deployment_status_url)
            res_dict = {}
        finally:
            num_trials = num_trials + 1

        if res_dict.get('status', 0) == 3:
            _configure_default_logging(cmd, rg_name, name)
            raise CLIError("""Zip deployment failed. {}. Please run the command az webapp log tail
                           -n {} -g {}""".format(res_dict, name, rg_name))
        if res_dict.get('status', 0) == 4:
            break
        if 'progress' in res_dict:
            logger.info(res_dict['progress'])  # show only in debug mode, customers seem to find this confusing
    # if the deployment is taking longer than expected
    if res_dict.get('status', 0) != 4:
        _configure_default_logging(cmd, rg_name, name)
        raise CLIError("""Timeout reached by the command, however, the deployment operation
                       is still on-going. Navigate to your scm site to check the deployment status""")
    return res_dict


def _fill_ftp_publishing_url(cmd, webapp, resource_group_name, name, slot=None):
    profiles = list_publish_profiles(cmd, resource_group_name, name, slot)
    try:
        url = next((p['publishUrl'] for p in profiles if p['publishMethod'] == 'FTP'), None)
        setattr(webapp, 'ftpPublishingUrl', url)
    except StopIteration as e:
        pass

    return webapp
