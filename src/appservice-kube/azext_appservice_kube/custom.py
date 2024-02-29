# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import time

from binascii import hexlify
from os import urandom
import json

from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.util import send_raw_request, sdk_no_wait, get_json_object, get_file_json
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.appservice.custom import (
    list_runtimes,
    update_container_settings,
    _rename_server_farm_props,
    get_site_configs,
    _get_site_credential,
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
    _get_linux_multicontainer_encoded_config_from_file,
    _StackRuntimeHelper,
    _FunctionAppStackRuntimeHelper,
    upload_zip_to_storage,
    is_plan_consumption,
    _configure_default_logging,
    assign_identity,
    delete_app_settings,
    update_app_settings,
    list_hostnames,
    _convert_camel_to_snake_case,
    _get_content_share_name,
    get_app_service_plan_from_webapp)
from azure.cli.command_modules.appservice._constants import LINUX_OS_NAME, FUNCTIONS_NO_V2_REGIONS
from azure.cli.command_modules.appservice.utils import retryable_method, get_sku_tier
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.commands import LongRunningOperation
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.cli.core.util import get_az_user_agent
from azure.cli.core.azclierror import (ResourceNotFoundError, RequiredArgumentMissingError, ValidationError,
                                       ArgumentUsageError, MutuallyExclusiveArgumentError)

from msrestazure.tools import is_valid_resource_id, parse_resource_id

from ._constants import (KUBE_DEFAULT_SKU, KUBE_ASP_KIND, KUBE_APP_KIND, KUBE_FUNCTION_APP_KIND,
                         KUBE_FUNCTION_CONTAINER_APP_KIND, KUBE_CONTAINER_APP_KIND)

from ._utils import (_normalize_sku, get_sku_name, _generic_site_operation,
                     _get_location_from_resource_group, _validate_asp_sku)
from ._create_util import (get_app_details, get_site_availability, get_current_stack_from_runtime,
                           generate_default_app_service_plan_name)
from ._client_factory import web_client_factory, ex_handler_factory, customlocation_client_factory

logger = get_logger(__name__)


# pylint: disable=too-many-locals,too-many-lines,consider-using-f-string


# TODO remove and replace with calls to KubeEnvironmentsOperations once the SDK gets updated
class KubeEnvironmentClient():
    @classmethod
    def create(cls, cmd, resource_group_name, name, kube_environment_envelope):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/kubeEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(kube_environment_envelope))
        return r.json()

    @classmethod
    def update(cls, cmd, name, resource_group_name, kube_environment_envelope):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/kubeEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(kube_environment_envelope))
        return r.json()

    @classmethod
    def show(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/kubeEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/kubeEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        send_raw_request(cmd.cli_ctx, "DELETE", request_url)  # API doesn't return JSON for some reason

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        kube_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.Web/kubeEnvironments?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for kube in j["value"]:
            formatted = formatter(kube)
            kube_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for kube in j["value"]:
                formatted = formatter(kube)
                kube_list.append(formatted)

        return kube_list

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name, formatter=lambda x: x):
        kube_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/kubeEnvironments?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for kube in j["value"]:
            formatted = formatter(kube)
            kube_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for kube in j["value"]:
                formatted = formatter(kube)
                kube_list.append(formatted)

        return kube_list


class AppServiceClient():
    @classmethod
    def create(cls, cmd, name, resource_group_name, appservice_json):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)

        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/serverfarms/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(appservice_json))
        return r.json()

    @classmethod
    def update(cls, cmd, name, resource_group_name, appservice_json):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)

        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/serverfarms/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(appservice_json))
        return r.json()

    @classmethod
    def show(cls, cmd, name, resource_group_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)

        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/serverfarms/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()


class WebAppClient:
    @classmethod
    def create(cls, cmd, name, resource_group_name, webapp_json):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)

        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(webapp_json))
        return r.json()

    @classmethod
    def restart(cls, cmd, resource_group_name, name, slot=None):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2020-12-01"
        sub_id = get_subscription_id(cmd.cli_ctx)

        if slot is not None:
            url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/"\
                      "Microsoft.Web/sites/{}/slots/{}/restart?api-version={}"
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                slot,
                api_version)
        else:
            url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/restart?api-version={}"
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                api_version)

        send_raw_request(cmd.cli_ctx, "POST", request_url)


def _get_kube_client(cmd):
    client = web_client_factory(cmd.cli_ctx)
    return client.kube_environments


def show_kube_environments(cmd, name, resource_group_name):
    client = _get_kube_client(cmd)
    return client.get(name=name, resource_group_name=resource_group_name)


def delete_kube_environment(cmd, name, resource_group_name):
    # Raises an exception if the kube environment doesn't exist
    KubeEnvironmentClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)

    return KubeEnvironmentClient.delete(cmd=cmd, name=name, resource_group_name=resource_group_name)


def create_kube_environment(cmd, name, resource_group_name, custom_location, static_ip=None, location=None,
                            tags=None, no_wait=False):
    # pylint: disable=broad-except,no-member,protected-access

    custom_location_client = customlocation_client_factory(cmd.cli_ctx)
    custom_location_object = None

    if is_valid_resource_id(custom_location):
        parsed_custom_location = parse_resource_id(custom_location)
        if parsed_custom_location['resource_type'].lower() != 'customlocations':
            raise ValidationError('Invalid custom location')
        custom_location_object = custom_location_client.custom_locations.get(
            parsed_custom_location['resource_group'],
            parsed_custom_location['name'])
    else:
        custom_location_object = custom_location_client.custom_locations.get(resource_group_name, custom_location)
        custom_location = custom_location_object.id

    if not location:
        location = custom_location_object.location

    front_end_configuration = {"kind": "LoadBalancer"}

    extended_location = {"customLocation": custom_location}

    arc_configuration = {
        "artifactsStorageType": "NetworkFileSystem",
        "artifactStorageClassName": "default",
        "frontEndServiceConfiguration": front_end_configuration
    }

    kube_environment = {
        "kind": None,
        "location": location,
        "tags": tags,
        "properties": {
            "extendedLocation": extended_location,
            "staticIp": static_ip,
            "arcConfiguration": arc_configuration
        }
    }

    try:
        return sdk_no_wait(no_wait, KubeEnvironmentClient.create,
                           cmd=cmd, resource_group_name=resource_group_name,
                           name=name, kube_environment_envelope=kube_environment)
    except Exception as e:
        msg = ""
        try:
            msg = json.loads(e.response._content)['Message']
        except Exception as e2:
            raise e from e2
        if msg != "":
            raise ValidationError(msg) from e
        raise e


def list_kube_environments(cmd, resource_group_name=None):
    client = _get_kube_client(cmd)
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


# TODO should be able to update staticIp and tags -- remove exception once API fixed
def update_kube_environment(cmd, name, resource_group_name, custom_location=None, static_ip=None,
                            tags=None, no_wait=False):
    raise CLIError("Update is not yet supported for Kubernetes Environments.")

    # Raises an exception if the kube environment doesn't exist
    # KubeEnvironmentClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)

    # front_end_configuration = {"kind": "LoadBalancer"}

    # extended_location = {"customLocation": custom_location}

    # arc_configuration = {
    #     "artifactsStorageType": "NetworkFileSystem",
    #     "artifactStorageClassName": "default",
    #     "frontEndServiceConfiguration": front_end_configuration
    # }

    # kube_environment = {
    #     "kind": None,
    #     "location": location,
    #     "properties": {
    #         "extendedLocation": extended_location,
    #         "staticIp": static_ip,
    #         "arcConfiguration": arc_configuration
    #     }
    # }

    # if tags is not None:
    #     kube_environment["tags"] = tags

    # return sdk_no_wait(no_wait, KubeEnvironmentClient.update, cmd=cmd, resource_group_name=resource_group_name,
    #                    name=name, kube_environment_envelope=kube_environment)


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


def create_app_service_plan(cmd, resource_group_name, name, is_linux, hyper_v, per_site_scaling=False,
                            custom_location=None,
                            app_service_environment=None, sku=None,
                            number_of_workers=None, location=None, tags=None, no_wait=False):
    custom_location = _get_custom_location_id(cmd, custom_location, resource_group_name)

    if not sku:
        sku = 'B1' if not custom_location else KUBE_DEFAULT_SKU

    if custom_location:
        if not per_site_scaling:
            raise ArgumentUsageError('Per Site Scaling must be true when using Custom Location. '
                                     'Please re-run with --per-site-scaling flag')
        if app_service_environment:
            raise ArgumentUsageError('App Service Environment is not supported with using Custom Location')
        if hyper_v:
            raise ArgumentUsageError('Hyper V is not supported with using Custom Location')
        if not is_linux:
            raise ArgumentUsageError('Only Linux is supported with using Custom Location. '
                                     'Please re-run with --is-linux flag.')

    return create_app_service_plan_inner(cmd, resource_group_name, name, is_linux, hyper_v, per_site_scaling,
                                         custom_location, app_service_environment, sku, number_of_workers, location,
                                         tags, no_wait)


def get_vm_sizes(cli_ctx, location):
    from ._client_factory import cf_compute_service

    return cf_compute_service(cli_ctx).virtual_machine_sizes.list(location)


def _get_kube_env_from_custom_location(cmd, custom_location, resource_group):
    kube_environment_id = ""
    custom_location_name = custom_location

    if is_valid_resource_id(custom_location):
        parsed_custom_location = parse_resource_id(custom_location)
        custom_location_name = parsed_custom_location.get("name")
        resource_group = parsed_custom_location.get("resource_group")

    _check_custom_location_exists(cmd, custom_location_name, resource_group)

    client = _get_kube_client(cmd)
    kube_envs = client.list_by_subscription()

    for kube in kube_envs:
        if kube.extended_location and kube.extended_location.type == "CustomLocation":
            if is_valid_resource_id(kube.extended_location.name):
                candidate_custom_location = parse_resource_id(kube.extended_location.name)
                matched_name = candidate_custom_location.get("name", "").lower() == custom_location_name.lower()
                matched_rg = candidate_custom_location.get("resource_group", "").lower() == resource_group.lower()
                if matched_name and matched_rg:
                    kube_environment_id = kube.id
                    break

    if not kube_environment_id:
        raise ResourceNotFoundError('Unable to find Kube Environment associated to the Custom Location')

    return kube_environment_id


def _check_custom_location_exists(cmd, name, resource_group):
    from azure.core.exceptions import ResourceNotFoundError as E
    custom_location_client = customlocation_client_factory(cmd.cli_ctx)
    try:
        custom_location_client.custom_locations.get(resource_name=name, resource_group_name=resource_group)
    except E as e:
        custom_locations = [cl.id for cl in custom_location_client.custom_locations.list_by_subscription()]
        logger.warning("\nPlease choose a custom location from your subscription: \n%s\n", custom_locations)
        raise e


def _get_custom_location_id_from_custom_location(cmd, custom_location_name, resource_group_name):
    if is_valid_resource_id(custom_location_name):
        return custom_location_name

    kube_envs = KubeEnvironmentClient.list_by_resource_group(cmd=cmd, resource_group_name=resource_group_name)

    for kube in kube_envs:
        parsed_custom_location = None
        custom_location_id = None

        if kube.additional_properties and 'extendedLocation' in kube.additional_properties:
            custom_location_id = kube.additional_properties['extendedLocation'].get('name')
            parsed_custom_location = parse_resource_id(custom_location_id)
        elif kube.extended_location and kube.extended_location.custom_location:
            custom_location_id = kube.extended_location.custom_location
            parsed_custom_location = parse_resource_id(custom_location_id)

        if parsed_custom_location and parsed_custom_location.get("name").lower() == custom_location_name.lower():
            return custom_location_id
    return None


def _get_custom_location_id_from_kube_env(kube):
    if kube.get("properties") and kube["properties"].get("extendedLocation"):
        return kube["properties"]['extendedLocation'].get('customLocation')
    if kube.get("extendedLocation") and kube["extendedLocation"].get("type") == "CustomLocation":
        return kube["extendedLocation"]["name"]
    raise ResourceNotFoundError("Could not get custom location from kube environment")


def _ensure_kube_settings_in_json(appservice_plan_json, extended_location=None, kube_env=None):
    if appservice_plan_json.get("properties") and (appservice_plan_json["properties"].get("kubeEnvironmentProfile")
                                                   is None and kube_env is not None):
        appservice_plan_json["properties"]["kubeEnvironmentProfile"] = kube_env.serialize()

    if appservice_plan_json.get("extendedLocation") is None and extended_location is not None:
        appservice_plan_json["extendedLocation"] = extended_location.serialize()

    appservice_plan_json['type'] = 'Microsoft.Web/serverfarms'
    if appservice_plan_json.get("extendedLocation") is not None:
        appservice_plan_json["extendedLocation"]["type"] = "CustomLocation"


def create_app_service_plan_inner(cmd, resource_group_name, name, is_linux, hyper_v, per_site_scaling=False,
                                  custom_location=None, app_service_environment=None, sku=None,
                                  number_of_workers=None, location=None, tags=None, no_wait=False):
    HostingEnvironmentProfile, SkuDescription, AppServicePlan, ExtendedLocation, KubeEnvironmentProfile = cmd.get_models('HostingEnvironmentProfile', 'SkuDescription', 'AppServicePlan', 'ExtendedLocation', 'KubeEnvironmentProfile')  # pylint: disable=line-too-long

    sku = _normalize_sku(sku)
    _validate_asp_sku(app_service_environment, custom_location, sku)

    if is_linux and hyper_v:
        raise MutuallyExclusiveArgumentError('Usage error: --is-linux and --hyper-v cannot be used together.')

    kube_environment = None
    kind = None

    client = web_client_factory(cmd.cli_ctx)

    if custom_location:
        kube_environment = _get_kube_env_from_custom_location(cmd, custom_location, resource_group_name)

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
            raise ResourceNotFoundError("App service environment '{}' not found in subscription.".format(ase_id))
    else:  # Non-ASE
        ase_def = None

    extended_location_envelope = None
    if kube_environment and (ase_def is None):
        kube_id = _resolve_kube_environment_id(cmd.cli_ctx, kube_environment, resource_group_name)
        kube_def = KubeEnvironmentProfile(id=kube_id)
        kind = KUBE_ASP_KIND
        parsed_id = parse_resource_id(kube_id)
        kube_name = parsed_id.get("name")
        kube_rg = parsed_id.get("resource_group")
        if kube_name is not None and kube_rg is not None:
            kube_env = KubeEnvironmentClient.show(cmd=cmd, resource_group_name=kube_rg, name=kube_name)
            extended_location_envelope = ExtendedLocation(name=_get_custom_location_id_from_kube_env(kube_env),
                                                          type="CustomLocation")

            if kube_env is not None:
                location = kube_env["location"]
            else:
                raise ResourceNotFoundError("Kube Environment '{}' not found in subscription.".format(kube_id))
    else:
        kube_def = None

    if location is None:
        location = _get_location_from_resource_group(cmd.cli_ctx, resource_group_name)

    # the api is odd on parameter naming, have to live with it for now
    sku_def = SkuDescription(tier=get_sku_name(sku), name=sku, capacity=number_of_workers)

    plan_def = AppServicePlan(location=location, tags=tags, sku=sku_def, kind=kind,
                              reserved=(is_linux or None), hyper_v=(hyper_v or None), name=name,
                              per_site_scaling=per_site_scaling, hosting_environment_profile=ase_def,
                              kube_environment_profile=kube_def, extended_location=extended_location_envelope)
    plan_json = plan_def.serialize()
    _ensure_kube_settings_in_json(appservice_plan_json=plan_json,
                                  extended_location=extended_location_envelope, kube_env=kube_def)

    return sdk_no_wait(no_wait, AppServiceClient.create, cmd=cmd, name=name,
                       resource_group_name=resource_group_name, appservice_json=plan_json)


def update_app_service_plan(cmd, resource_group_name, name, sku=None, number_of_workers=None, no_wait=False):
    client = web_client_factory(cmd.cli_ctx)
    plan = client.app_service_plans.get(resource_group_name, name).serialize()
    plan_with_kube_env = AppServiceClient.show(cmd=cmd, name=name, resource_group_name=resource_group_name)

    if number_of_workers is None and sku is None:
        logger.warning('No update is done. Specify --sku and/or --number-of-workers.')
    sku_def = plan["sku"]
    if sku is not None:
        sku = _normalize_sku(sku)
        sku_def["tier"] = get_sku_name(sku)
        sku_def["name"] = sku

    if number_of_workers is not None:
        sku_def["capacity"] = number_of_workers

    plan["sku"] = sku_def

    _ensure_kube_settings_in_json(appservice_plan_json=plan,
                                  extended_location=plan_with_kube_env.get("extendedLocation"),
                                  kube_env=plan_with_kube_env["properties"].get("kubeEnvironmentProfile"))

    return sdk_no_wait(no_wait, AppServiceClient.update, cmd=cmd, name=name,
                       resource_group_name=resource_group_name, appservice_json=plan)


def _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location, plan):
    if is_valid_resource_id(plan):
        parse_result = parse_resource_id(plan)
        plan_info = AppServiceClient.show(cmd=cmd, name=parse_result['name'],
                                          resource_group_name=parse_result["resource_group"])
    else:
        plan_info = AppServiceClient.show(cmd=cmd, name=plan, resource_group_name=resource_group_name)
    if not plan_info:
        raise CLIError("The plan '{}' doesn't exist in the resource group '{}".format(plan, resource_group_name))

    plan_kube_env_id = ""
    custom_location_kube_env_id = _get_kube_env_from_custom_location(cmd, custom_location, resource_group_name)
    if plan_info["properties"].get("kubeEnvironmentProfile"):
        plan_kube_env_id = plan_info["properties"]["kubeEnvironmentProfile"]["id"]

    return plan_kube_env_id.lower() == custom_location_kube_env_id.lower()


def _should_create_new_appservice_plan_for_k8se(cmd, name, custom_location, plan, resource_group_name):
    if custom_location and plan:
        return False
    if custom_location:
        existing_app_details = get_app_details(cmd, name, resource_group_name)
        if not existing_app_details:
            return True
        if _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location,
                                                             existing_app_details.server_farm_id):
            return False  # existing app and kube environments match
        return True  # existing app but new custom location
    return False  # plan is not None


def _is_webapp_kube(custom_location, plan_info, SkuDescription):
    return custom_location or plan_info.kind.upper() == KUBE_ASP_KIND.upper() or (
        isinstance(plan_info.sku, SkuDescription) and plan_info.sku.name.upper() == KUBE_DEFAULT_SKU)


def _get_custom_location_id(cmd, custom_location, resource_group_name):
    from msrestazure.tools import resource_id

    if custom_location is None:
        return None
    if is_valid_resource_id(custom_location):
        return custom_location

    return resource_id(
        subscription=get_subscription_id(cmd.cli_ctx),
        resource_group=resource_group_name,
        namespace='microsoft.extendedlocation',
        type='customlocations',
        name=custom_location)


def list_runtimes_kube(cmd, os_type=None, linux=False, is_kube=False):
    if is_kube:
        runtime_helper = _AppOnArcStackRuntimeHelper(cmd=cmd, linux=True, windows=False)
        return runtime_helper.get_stack_names_only(delimiter=":")

    return list_runtimes(cmd, os_type, linux)


def create_webapp(cmd, resource_group_name, name, plan=None, runtime=None, custom_location=None, startup_file=None,  # pylint: disable=too-many-statements,too-many-branches
                  deployment_container_image_name=None, deployment_source_url=None, deployment_source_branch='master',
                  deployment_local_git=None, docker_registry_server_password=None, docker_registry_server_user=None,
                  multicontainer_config_type=None, multicontainer_config_file=None, tags=None,
                  using_webapp_up=False, language=None, assign_identities=None, role='Contributor', scope=None,
                  min_worker_count=None, max_worker_count=None):
    SiteConfig, SkuDescription, Site, NameValuePair, AppServicePlan = cmd.get_models(
        'SiteConfig', 'SkuDescription', 'Site', 'NameValuePair', "AppServicePlan")
    if deployment_source_url and deployment_local_git:
        raise CLIError('usage error: --deployment-source-url <url> | --deployment-local-git')

    custom_location = _get_custom_location_id(cmd, custom_location, resource_group_name)

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
                           "correct parameters.".format(name, current_rg, resource_group_name))
        existing_app_settings = _generic_site_operation(cmd.cli_ctx, resource_group_name,
                                                        name, 'list_application_settings')
        settings = []
        for k, v in existing_app_settings.properties.items():
            settings.append(NameValuePair(name=k, value=v))
        site_config = SiteConfig(app_settings=settings)
    else:
        site_config = SiteConfig(app_settings=[])

    _should_create_new_plan = _should_create_new_appservice_plan_for_k8se(cmd,
                                                                          name, custom_location,
                                                                          plan, resource_group_name)
    if _should_create_new_plan:
        plan = generate_default_app_service_plan_name(name)
        logger.warning("Plan not specified. Creating Plan '%s' with sku '%s'", plan, KUBE_DEFAULT_SKU)
        create_app_service_plan(cmd=cmd, resource_group_name=resource_group_name,
                                name=plan, is_linux=True, hyper_v=False, custom_location=custom_location,
                                per_site_scaling=True, number_of_workers=1)

    if custom_location and plan:
        if not _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location, plan):
            raise ValidationError("Custom location's kube environment and App Service Plan's "
                                  "kube environment don't match")
    elif custom_location and not plan:
        app_details = get_app_details(cmd, name, resource_group_name)
        if app_details is not None:
            plan = app_details.server_farm_id

    docker_registry_server_url = parse_docker_image_name(deployment_container_image_name)

    client = web_client_factory(cmd.cli_ctx)
    if is_valid_resource_id(plan):
        parse_result = parse_resource_id(plan)
        plan_info = AppServicePlan.from_dict(AppServiceClient.show(cmd=cmd, name=parse_result['name'],
                                                                   resource_group_name=parse_result["resource_group"]))
    else:
        plan_info = AppServicePlan.from_dict(AppServiceClient.show(cmd=cmd,
                                                                   name=plan, resource_group_name=resource_group_name))
    if not plan_info:
        raise CLIError("The plan '{}' doesn't exist in the resource group '{}".format(plan, resource_group_name))

    if custom_location:
        _validate_asp_sku(app_service_environment=None, custom_location=custom_location, sku=plan_info.sku.name)

    is_linux = plan_info.reserved
    location = plan_info.location

    if isinstance(plan_info.sku, SkuDescription) and plan_info.sku.name.upper() not in ['F1', 'FREE', 'SHARED', 'D1',
                                                                                        'B1', 'B2', 'B3', 'BASIC']:
        site_config.always_on = True
    webapp_def = Site(location=location, site_config=site_config, server_farm_id=plan_info.id, tags=tags,
                      https_only=using_webapp_up)

    is_kube = _is_webapp_kube(custom_location, plan_info, SkuDescription)
    if is_kube:
        if deployment_container_image_name:
            webapp_def.kind = KUBE_CONTAINER_APP_KIND
        else:
            webapp_def.kind = KUBE_APP_KIND

        # if Custom Location provided, use that for Extended Location Envelope. Otherwise, get Custom Location from ASP
        if custom_location:
            webapp_def.enable_additional_properties_sending()
            custom_location_id = _get_custom_location_id_from_custom_location(cmd, custom_location, resource_group_name)
            if custom_location_id:
                extended_loc = {'name': custom_location_id, 'type': 'CustomLocation'}
                webapp_def.additional_properties["extendedLocation"] = extended_loc
        else:
            extended_loc = plan_info.additional_properties["extendedLocation"]
            webapp_def.additional_properties["extendedLocation"] = extended_loc

    if is_kube:
        if min_worker_count is not None:
            site_config.number_of_workers = min_worker_count

        if max_worker_count is not None:
            site_config.app_settings.append(NameValuePair(name='K8SE_APP_MAX_INSTANCE_COUNT', value=max_worker_count))

        if deployment_container_image_name:
            site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_URL',
                                                          value=docker_registry_server_url))

            if docker_registry_server_user is not None and docker_registry_server_password is not None:
                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_USERNAME',
                                                              value=docker_registry_server_user))

                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_PASSWORD',
                                                              value=docker_registry_server_password))
    helper = _StackRuntimeHelper(cmd, linux=bool(is_linux or is_kube), windows=not bool(is_linux or is_kube))
    if is_kube:
        helper = _AppOnArcStackRuntimeHelper(cmd, linux=bool(is_linux or is_kube), windows=not bool(is_linux or is_kube))

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
            match = helper.resolve(runtime, linux=True)
            if not match:
                raise CLIError("Linux Runtime '{}' is not supported."
                               "Please invoke 'list-runtimes --kube' to cross check".format(runtime))
            helper.get_site_config_setter(match, linux=True)(cmd=cmd, stack=match, site_config=site_config)
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
        match = helper.resolve(runtime, linux=False)
        if not match:
            raise CLIError("Windows runtime '{}' is not supported. "
                           "Please invoke 'az webapp list-runtimes' to cross check".format(runtime))
        helper.get_site_config_setter(match, linux=is_linux)(cmd=cmd, stack=match, site_config=site_config)

        # portal uses the current_stack propety in metadata to display stack for windows apps
        current_stack = get_current_stack_from_runtime(runtime)

    else:  # windows webapp without runtime specified
        if name_validation.name_available:  # If creating new webapp
            node_default_version = helper.get_default_version("node", is_linux, get_windows_config_version=True)
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

    poller = client.web_apps.begin_create_or_update(resource_group_name, name, webapp_def)
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


def update_webapp(cmd, instance, client_affinity_enabled=None, https_only=None, minimum_elastic_instance_count=None,
                  prewarmed_instance_count=None):
    if 'function' in instance.kind:
        raise ValidationError("please use 'az functionapp update' to update this function app")
    if minimum_elastic_instance_count or prewarmed_instance_count:
        args = ["--minimum-elastic-instance-count", "--prewarmed-instance-count"]
        plan = get_app_service_plan_from_webapp(cmd, instance)
        sku = _normalize_sku(plan.sku.name)
        if get_sku_tier(sku) not in ["PREMIUMV2", "PREMIUMV3"]:
            raise ValidationError("{} are only supported for elastic premium V2/V3 SKUs".format(str(args)))
        if not plan.elastic_scale_enabled:
            raise ValidationError("Elastic scale is not enabled on the App Service Plan. Please update the plan ")
        if (minimum_elastic_instance_count or 0) > plan.maximum_elastic_worker_count:
            raise ValidationError("--minimum-elastic-instance-count: Minimum elastic instance count is greater than "
                                  "the app service plan's maximum Elastic worker count. "
                                  "Please choose a lower count or update the plan's maximum ")
        if (prewarmed_instance_count or 0) > plan.maximum_elastic_worker_count:
            raise ValidationError("--prewarmed-instance-count: Prewarmed instance count is greater than "
                                  "the app service plan's maximum Elastic worker count. "
                                  "Please choose a lower count or update the plan's maximum ")
    from azure.mgmt.web.models import SkuDescription

    if client_affinity_enabled is not None:
        instance.client_affinity_enabled = client_affinity_enabled == 'true'
    if https_only is not None:
        instance.https_only = https_only == 'true'

    if minimum_elastic_instance_count is not None:
        from azure.mgmt.web.models import SiteConfig
        # Need to create a new SiteConfig object to ensure that the new property is included in request body
        conf = SiteConfig(**instance.site_config.as_dict())
        conf.minimum_elastic_instance_count = minimum_elastic_instance_count
        instance.site_config = conf

    if prewarmed_instance_count is not None:
        instance.site_config.pre_warmed_instance_count = prewarmed_instance_count

    client = web_client_factory(cmd.cli_ctx)
    plan_parsed = parse_resource_id(instance.server_farm_id)
    plan_info = client.app_service_plans.get(plan_parsed['resource_group'], plan_parsed['name'])

    is_kube = _is_webapp_kube(instance.extended_location, plan_info, SkuDescription)
    has_custom_location_id = instance.extended_location and is_valid_resource_id(instance.extended_location.name)
    if is_kube and has_custom_location_id:
        custom_location_id = instance.extended_location.name
        instance.enable_additional_properties_sending()
        extended_loc = {'name': custom_location_id, 'type': 'CustomLocation'}
        instance.additional_properties["extendedLocation"] = extended_loc

    return instance


# for generic updater
def get_webapp(cmd, resource_group_name, name, slot=None):
    return _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'get', slot)


def set_webapp(cmd, resource_group_name, name, slot=None, **kwargs):  # pylint: disable=unused-argument
    instance = kwargs['parameters']
    client = web_client_factory(cmd.cli_ctx)
    updater = client.web_apps.begin_create_or_update_slot if slot else client.web_apps.begin_create_or_update
    kwargs = {"resource_group_name": resource_group_name, "name": name, "site_envelope": instance}
    if slot:
        kwargs['slot'] = slot

    return updater(**kwargs)


def scale_webapp(cmd, resource_group_name, name, instance_count, slot=None):
    client = web_client_factory(cmd.cli_ctx)
    webapp = client.web_apps.get(resource_group_name, name)
    if not webapp.extended_location:
        raise ValidationError("The web app {} is not on Arc enabled Kubernetes. Please use `az appservice plan update` to scale for non-arc enabled app service.".format(name))
    return update_site_configs(cmd, resource_group_name, name,
                               number_of_workers=instance_count, slot=slot)


def show_webapp(cmd, resource_group_name, name, slot=None, app_instance=None):
    webapp = app_instance
    if not app_instance:  # when the routine is invoked as a help method, not through commands
        webapp = _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'get', slot)
    if not webapp:
        raise ResourceNotFoundError("WebApp'{}', is not found on RG '{}'.".format(name, resource_group_name))
    webapp.site_config = _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'get_configuration', slot)
    _rename_server_farm_props(webapp)

    # TODO: get rid of this conditional once the api's are implemented for kubeapps
    if KUBE_APP_KIND.lower() not in webapp.kind.lower():
        _fill_ftp_publishing_url(cmd, webapp, resource_group_name, name, slot)

    return webapp


def _is_function_kube(custom_location, plan_info, SkuDescription):
    return custom_location or plan_info is not None and (
        plan_info.kind.upper() == KUBE_ASP_KIND.upper() or (
            isinstance(plan_info.sku, SkuDescription) and plan_info.sku.name.upper() == KUBE_DEFAULT_SKU))


def create_functionapp(cmd, resource_group_name, name, storage_account=None, plan=None,
                       os_type=None, functions_version=None, runtime=None, runtime_version=None,
                       consumption_plan_location=None, app_insights=None, app_insights_key=None,
                       disable_app_insights=None, deployment_source_url=None,
                       deployment_source_branch='master', deployment_local_git=None,
                       docker_registry_server_password=None, docker_registry_server_user=None,
                       deployment_container_image_name=None, tags=None, assign_identities=None,
                       role='Contributor', scope=None,
                       custom_location=None, min_worker_count=None, max_worker_count=None):
    # pylint: disable=too-many-statements, too-many-branches
    if functions_version is None:
        logger.warning("No functions version specified so defaulting to 3. In the future, specifying a version will "
                       "be required. To create a 3.x function you would pass in the flag `--functions-version 3`")
        functions_version = '3'

    if deployment_source_url and deployment_local_git:
        raise MutuallyExclusiveArgumentError('usage error: --deployment-source-url <url> | --deployment-local-git')
    if not plan and not consumption_plan_location and not custom_location:
        raise RequiredArgumentMissingError("Either Plan, Consumption Plan or Custom Location must be specified")
    if consumption_plan_location and custom_location:
        raise MutuallyExclusiveArgumentError("Consumption Plan and Custom Location cannot be used together")
    if consumption_plan_location and plan:
        raise MutuallyExclusiveArgumentError("Consumption Plan and Plan cannot be used together")

    from azure.mgmt.web.models import Site
    SiteConfig, NameValuePair, SkuDescription = cmd.get_models('SiteConfig', 'NameValuePair', 'SkuDescription')
    docker_registry_server_url = parse_docker_image_name(deployment_container_image_name)
    disable_app_insights = disable_app_insights == "true"

    custom_location = _get_custom_location_id(cmd, custom_location, resource_group_name)

    site_config = SiteConfig(app_settings=[])
    client = web_client_factory(cmd.cli_ctx)

    functionapp_def = Site(location=None, site_config=site_config, tags=tags)

    plan_info = None
    if runtime is not None:
        runtime = runtime.lower()

    if consumption_plan_location:
        locations = list_consumption_locations(cmd)
        location = next((loc for loc in locations if loc['name'].lower() == consumption_plan_location.lower()), None)
        if location is None:
            raise ValidationError("Location is invalid. Use: az functionapp list-consumption-locations")
        functionapp_def.location = consumption_plan_location
        functionapp_def.kind = 'functionapp'
        # if os_type is None, the os type is windows
        is_linux = bool(os_type and os_type.lower() == LINUX_OS_NAME)

    else:  # apps with SKU based plan
        _should_create_new_plan = _should_create_new_appservice_plan_for_k8se(cmd,
                                                                              name, custom_location,
                                                                              plan, resource_group_name)
        if _should_create_new_plan:
            plan = generate_default_app_service_plan_name(name)
            logger.warning("Plan not specified. Creating Plan '%s' with sku '%s'", plan, KUBE_DEFAULT_SKU)
            create_app_service_plan(cmd=cmd, resource_group_name=resource_group_name,
                                    name=plan, is_linux=True, hyper_v=False, custom_location=custom_location,
                                    per_site_scaling=True, number_of_workers=1)
        if custom_location and plan:
            if not _validate_asp_and_custom_location_kube_envs_match(cmd, resource_group_name, custom_location, plan):
                raise ValidationError("Custom location's kube environment "
                                      "and App Service Plan's kube environment don't match")
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
            raise ResourceNotFoundError("The plan '{}' doesn't exist".format(plan))

        location = plan_info.location
        is_linux = bool(plan_info.reserved)
        functionapp_def.server_farm_id = plan
        functionapp_def.location = location

    if functions_version == '2' and functionapp_def.location in FUNCTIONS_NO_V2_REGIONS:
        raise ValidationError("2.x functions are not supported in this region. To create a 3.x function, "
                              "pass in the flag '--functions-version 3'")

    if is_linux and not runtime and (consumption_plan_location or not deployment_container_image_name):
        raise ArgumentUsageError(
            "usage error: --runtime RUNTIME required for linux functions apps without custom image.")

    if runtime is None and runtime_version is not None:
        raise ArgumentUsageError('Must specify --runtime to use --runtime-version')

    is_kube = _is_function_kube(custom_location, plan_info, SkuDescription)
    if not storage_account and not is_kube:
        raise ValidationError("--storage-account required for non-kubernetes function apps")

    runtime_helper = _FunctionAppStackRuntimeHelper(cmd, linux=is_linux, windows=not is_linux)
    matched_runtime = runtime_helper.resolve("dotnet" if not runtime else runtime,
                                             runtime_version, functions_version, is_linux)

    if is_kube:
        if min_worker_count is not None:
            site_config.number_of_workers = min_worker_count

        if max_worker_count is not None:
            site_config.app_settings.append(NameValuePair(name='K8SE_APP_MAX_INSTANCE_COUNT', value=max_worker_count))

    site_config_dict = matched_runtime.site_config_dict
    app_settings_dict = matched_runtime.app_settings_dict

    con_string = None
    if storage_account:
        con_string = _validate_and_get_connection_string(cmd.cli_ctx, resource_group_name, storage_account)

    if is_kube:
        functionapp_def.enable_additional_properties_sending()
        # if Custom Location provided, use that for Extended Location Envelope. Otherwise, get Custom Location from ASP
        if custom_location:
            custom_location_id = _get_custom_location_id_from_custom_location(cmd, custom_location, resource_group_name)
            if custom_location_id:
                extended_loc = {'name': custom_location_id, 'type': 'CustomLocation'}
                functionapp_def.additional_properties["extendedLocation"] = extended_loc
        else:
            extended_loc = plan_info.additional_properties["extendedLocation"]
            functionapp_def.additional_properties["extendedLocation"] = extended_loc

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
            site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_URL',
                                                          value=docker_registry_server_url))
            if docker_registry_server_user is not None and docker_registry_server_password is not None:
                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_USERNAME',
                                                              value=docker_registry_server_user))
                site_config.app_settings.append(NameValuePair(name='DOCKER_REGISTRY_SERVER_PASSWORD',
                                                              value=docker_registry_server_password))
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

                # clear all runtime specific configs and settings
                site_config_dict.use32_bit_worker_process = False
                app_settings_dict = {}

                # ensure that app insights is created if not disabled
                matched_runtime.app_insights = True
            else:
                site_config.app_settings.append(NameValuePair(name='WEBSITES_ENABLE_APP_SERVICE_STORAGE',
                                                              value='true'))
    else:
        functionapp_def.kind = 'functionapp'

    # set site configs
    for prop, value in site_config_dict.as_dict().items():
        snake_case_prop = _convert_camel_to_snake_case(prop)
        setattr(site_config, snake_case_prop, value)

    # temporary workaround for dotnet-isolated linux consumption apps
    if is_linux and consumption_plan_location is not None and runtime == 'dotnet-isolated':
        site_config.linux_fx_version = ''

    # adding app settings
    for app_setting, value in app_settings_dict.items():
        site_config.app_settings.append(NameValuePair(name=app_setting, value=value))

    site_config.app_settings.append(NameValuePair(name='FUNCTIONS_EXTENSION_VERSION',
                                                  value=_get_extension_version_functionapp(functions_version)))
    if con_string:
        site_config.app_settings.append(NameValuePair(name='AzureWebJobsStorage', value=con_string))

    # If plan is not consumption or elastic premium, we need to set always on
    if consumption_plan_location is None and not is_plan_elastic_premium(cmd, plan_info):
        site_config.always_on = True

    # If plan is elastic premium or consumption, we need these app settings
    if is_plan_elastic_premium(cmd, plan_info) or consumption_plan_location is not None:
        if con_string:
            site_config.app_settings.append(NameValuePair(name='WEBSITE_CONTENTAZUREFILECONNECTIONSTRING',
                                                          value=con_string))
        site_config.app_settings.append(NameValuePair(name='WEBSITE_CONTENTSHARE', value=_get_content_share_name(name)))

    create_app_insights = False

    if app_insights_key is not None:
        site_config.app_settings.append(NameValuePair(name='APPINSIGHTS_INSTRUMENTATIONKEY',
                                                      value=app_insights_key))
    elif app_insights is not None:
        instrumentation_key = get_app_insights_key(cmd.cli_ctx, resource_group_name, app_insights)
        site_config.app_settings.append(NameValuePair(name='APPINSIGHTS_INSTRUMENTATIONKEY',
                                                      value=instrumentation_key))
    elif disable_app_insights or not matched_runtime.app_insights:
        # set up dashboard if no app insights
        if con_string:
            site_config.app_settings.append(NameValuePair(name='AzureWebJobsDashboard', value=con_string))
    elif not disable_app_insights and matched_runtime.app_insights:
        create_app_insights = True

    poller = client.web_apps.begin_create_or_update(resource_group_name, name, functionapp_def)
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
            if con_string:
                update_app_settings(cmd, functionapp.resource_group, functionapp.name,
                                    ['AzureWebJobsDashboard={}'.format(con_string)])

    if deployment_container_image_name:
        update_container_settings_functionapp(cmd, resource_group_name, name, docker_registry_server_url,
                                              deployment_container_image_name, docker_registry_server_user,
                                              docker_registry_server_password)

    if assign_identities is not None:
        identity = assign_identity(cmd, resource_group_name, name, assign_identities,
                                   role, None, scope)
        functionapp.identity = identity

    return functionapp


def update_container_settings_functionapp(cmd, resource_group_name, name, docker_registry_server_url=None,
                                          docker_custom_image_name=None, docker_registry_server_user=None,
                                          docker_registry_server_password=None, slot=None):
    return update_container_settings(cmd, resource_group_name, name, docker_registry_server_url,
                                     docker_custom_image_name, docker_registry_server_user, None,
                                     docker_registry_server_password, multicontainer_config_type=None,
                                     multicontainer_config_file=None, slot=slot)


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


def config_source_control(cmd, resource_group_name, name, repo_url, repository_type='git', branch=None,  # pylint: disable=too-many-locals
                          manual_integration=None, git_token=None, slot=None):
    client = web_client_factory(cmd.cli_ctx)
    location = _get_location_from_webapp(client, resource_group_name, name)

    from azure.mgmt.web.models import SiteSourceControl, SourceControl
    if git_token:
        sc = SourceControl(location=location, source_control_name='GitHub', token=git_token)
        client.update_source_control('GitHub', sc)

    source_control = SiteSourceControl(location=location, repo_url=repo_url, branch=branch,
                                       is_manual_integration=manual_integration,
                                       is_mercurial=repository_type != 'git')

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
    return None


def list_publish_profiles(cmd, resource_group_name, name, slot=None, xml=False):
    import xmltodict

    content = _generic_site_operation(cmd.cli_ctx, resource_group_name, name,
                                      'list_publishing_profile_xml_with_secrets', slot, {"format": "WebDeploy"})
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
    return resource_id(
        subscription=get_subscription_id(cli_ctx),
        resource_group=resource_group_name,
        namespace='Microsoft.Web',
        type='kubeEnvironments',
        name=kube_environment)


def _get_linux_fx_kube_functionapp(runtime, runtime_version):
    if runtime.upper() == "DOTNET":
        runtime = "DOTNETCORE"
    return '{}|{}'.format(runtime.upper(), runtime_version)


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
        raise ResourceNotFoundError('The function app \'{}\' was not found in resource group \'{}\'. '
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
        raise ValidationError('Remote build is only available on Linux function apps')

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
    except ValueError as e:
        raise CLIError('Failed to fetch scm url for function app') from e

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
            logger.warning('Something went wrong. It may take a few seconds for a new deployment to reflect'
                           'on kube cluster. Retrying deployment...')
            time.sleep(10)   # retry in a moment
            res = requests.post(zip_url, data=zip_content, headers=headers,
                                verify=not should_disable_connection_verify())
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


def restart_webapp(cmd, resource_group_name, name, slot=None):
    return WebAppClient.restart(cmd=cmd, resource_group_name=resource_group_name, name=name, slot=slot)


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
    except StopIteration:
        pass

    return webapp


def _update_host_name_ssl_state(cmd, resource_group_name, webapp_name, webapp,
                                host_name, ssl_state, thumbprint, slot=None):
    from azure.mgmt.web.models import HostNameSslState

    webapp.host_name_ssl_states = [HostNameSslState(name=host_name,
                                                    ssl_state=ssl_state,
                                                    thumbprint=thumbprint,
                                                    to_update=True)]

    webapp_dict = webapp.serialize()

    if webapp.extended_location is not None:
        webapp_dict["extendedLocation"]["type"] = "customLocation"

    management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
    api_version = "2020-12-01"
    sub_id = get_subscription_id(cmd.cli_ctx)
    if slot is None:
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            webapp_name,
            api_version)
    else:
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/slots/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            webapp_name,
            slot,
            api_version)

    return send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(webapp_dict))


def _match_host_names_from_cert(hostnames_from_cert, hostnames_in_webapp):
    # the goal is to match '*.foo.com' with host name like 'admin.foo.com', 'logs.foo.com', etc
    matched = set()
    for hostname in hostnames_from_cert:
        if hostname.startswith('*'):
            for h in hostnames_in_webapp:
                if hostname[hostname.find('.'):] == h[h.find('.'):]:
                    matched.add(h)
        elif hostname in hostnames_in_webapp:
            matched.add(hostname)
    return matched


def _update_ssl_binding(cmd, resource_group_name, name, certificate_thumbprint, ssl_type, slot=None):
    client = web_client_factory(cmd.cli_ctx, api_version="2021-01-01")
    webapp = client.web_apps.get(resource_group_name, name)
    if not webapp:
        raise ResourceNotFoundError("'{}' app doesn't exist".format(name))

    cert_resource_group_name = parse_resource_id(webapp.server_farm_id)['resource_group']
    webapp_certs = client.certificates.list_by_resource_group(cert_resource_group_name)

    found_cert = None
    for webapp_cert in webapp_certs:
        if webapp_cert.thumbprint == certificate_thumbprint:
            found_cert = webapp_cert
    if not found_cert:
        webapp_certs = client.certificates.list_by_resource_group(resource_group_name)
        for webapp_cert in webapp_certs:
            if webapp_cert.thumbprint == certificate_thumbprint:
                found_cert = webapp_cert
    if found_cert:
        if len(found_cert.host_names) == 1 and not found_cert.host_names[0].startswith('*'):
            _update_host_name_ssl_state(cmd, resource_group_name, name, webapp,
                                        found_cert.host_names[0], ssl_type,
                                        certificate_thumbprint, slot)
            return show_webapp(cmd, resource_group_name, name, slot)

        query_result = list_hostnames(cmd, resource_group_name, name, slot)
        hostnames_in_webapp = [x.name.split('/')[-1] for x in query_result]
        to_update = _match_host_names_from_cert(found_cert.host_names, hostnames_in_webapp)
        for h in to_update:
            _update_host_name_ssl_state(cmd, resource_group_name, name, webapp,
                                        h, ssl_type, certificate_thumbprint, slot)

        return show_webapp(cmd, resource_group_name, name, slot)

    raise ResourceNotFoundError("Certificate for thumbprint '{}' not found.".format(certificate_thumbprint))


def bind_ssl_cert(cmd, resource_group_name, name, certificate_thumbprint, ssl_type, slot=None):
    SslState = cmd.get_models('SslState')
    return _update_ssl_binding(cmd, resource_group_name, name, certificate_thumbprint,
                               SslState.sni_enabled if ssl_type == 'SNI' else SslState.ip_based_enabled, slot)


def unbind_ssl_cert(cmd, resource_group_name, name, certificate_thumbprint, slot=None):
    SslState = cmd.get_models('SslState')
    return _update_ssl_binding(cmd, resource_group_name, name,
                               certificate_thumbprint, SslState.disabled, slot)


# WebApps stack class
class _AppOnArcStackRuntimeHelper(_StackRuntimeHelper):

    def __init__(self, cmd, linux=False, windows=False):
        super().__init__(cmd, linux=linux, windows=windows)

    def _load_stacks(self):
        if self._stacks:
            return
        self._load_stacks_hardcoded()

    # override _load_stacks() to call this method to use hardcoded stacks
    def _load_stacks_hardcoded(self):
        import os
        stacks_file = os.path.abspath(os.path.join(os.path.abspath(__file__), '../resources/WebappRuntimeStacks.json'))
        if self._stacks:
            return
        stacks = []
        if self._linux:
            stacks_json = get_file_json(stacks_file)['linux']
            for r in stacks_json:
                stacks.append(self.Runtime(display_name=r.get("displayName"),
                                           configs=r.get("configs"),
                                           github_actions_properties=r.get("github_actions_properties"),
                                           linux=True))
        self._stacks = stacks
