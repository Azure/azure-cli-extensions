# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, broad-except, pointless-statement, bare-except
import platform
import subprocess
import stat
import io
import os
import tarfile
import zipfile
import hashlib
import re
import requests
import packaging.version as SemVer

from urllib.request import urlopen

from azure.cli.command_modules.containerapp._utils import safe_get, _ensure_location_allowed
from azure.cli.command_modules.containerapp._client_factory import handle_raw_exception
from azure.cli.core._profile import Profile
from azure.cli.core.azclierror import (ValidationError, ResourceNotFoundError, CLIError, InvalidArgumentValueError)
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.servicelinker import ServiceLinkerManagementClient

from knack.log import get_logger
from msrestazure.tools import parse_resource_id, is_valid_resource_id

from ._managed_service_utils import ManagedRedisUtils, ManagedCosmosDBUtils, ManagedPostgreSQLFlexibleUtils, ManagedMySQLFlexibleUtils
from ._clients import ConnectedEnvCertificateClient, ContainerAppPreviewClient
from ._client_factory import custom_location_client_factory, k8s_extension_client_factory, providers_client_factory
from ._models import OryxRunImageTagProperty
from ._constants import (CONTAINER_APP_EXTENSION_TYPE,
                         CONNECTED_ENV_CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE, DEV_SERVICE_LIST,
                         MANAGED_ENVIRONMENT_RESOURCE_TYPE, CONTAINER_APPS_RP)

logger = get_logger(__name__)


def process_service(cmd, resource_list, service_name, arg_dict, subscription_id, resource_group_name, name,
                    binding_name, service_connector_def_list, service_bindings_def_list):
    # Check if the service exists in the list of dict
    for service in resource_list:
        if service["name"] == service_name:
            if service["type"] == "Microsoft.Cache/Redis":
                service_connector_def_list.append(
                    ManagedRedisUtils.build_redis_service_connector_def(subscription_id, resource_group_name,
                                                                        service_name, arg_dict,
                                                                        name, binding_name))
            elif service["type"] == "Microsoft.DocumentDb/databaseAccounts":
                service_connector_def_list.append(
                    ManagedCosmosDBUtils.build_cosmosdb_service_connector_def(subscription_id, resource_group_name,
                                                                              service_name, arg_dict,
                                                                              name, binding_name))
            elif service["type"] == "Microsoft.DBforPostgreSQL/flexibleServers":
                service_connector_def_list.append(
                    ManagedPostgreSQLFlexibleUtils.build_postgresql_service_connector_def(subscription_id, resource_group_name,
                                                                                          service_name, arg_dict,
                                                                                          name, binding_name))
            elif service["type"] == "Microsoft.DBforMySQL/flexibleServers":
                service_connector_def_list.append(
                    ManagedMySQLFlexibleUtils.build_mysql_service_connector_def(subscription_id, resource_group_name,
                                                                                service_name, arg_dict,
                                                                                name, binding_name))
            elif service["type"] == "Microsoft.App/containerApps":
                containerapp_def = ContainerAppPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name, name=service_name)

                if not containerapp_def:
                    raise ResourceNotFoundError(f"The service '{service_name}' does not exist")

                service_type = safe_get(containerapp_def, "properties", "configuration", "service", "type")

                if service_type is None or service_type not in DEV_SERVICE_LIST:
                    raise ResourceNotFoundError(f"The service '{service_name}' does not exist")

                service_bindings_def_list.append({
                    "serviceId": containerapp_def["id"],
                    "name": binding_name
                })

            else:
                raise ValidationError("Service not supported")
            break
    else:
        raise ResourceNotFoundError("Service with the given name does not exist")


def get_linker_client(cmd):
    resource = cmd.cli_ctx.cloud.endpoints.active_directory_resource_id
    profile = Profile(cli_ctx=cmd.cli_ctx)
    credential, subscription_id, _ = profile.get_login_credentials(
        subscription_id=get_subscription_id(cmd.cli_ctx), resource=resource)
    linker_client = ServiceLinkerManagementClient(credential)
    return linker_client


def validate_binding_name(binding_name):
    pattern = r'^(?=.{1,60}$)[a-zA-Z0-9._]+$'
    return bool(re.match(pattern, binding_name))


def check_unique_bindings(cmd, service_connectors_def_list, service_bindings_def_list, resource_group_name, name):
    linker_client = get_linker_client(cmd)
    containerapp_def = None

    try:
        containerapp_def = ContainerAppPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:  # pylint: disable=bare-except
        pass
    all_bindings = []

    if containerapp_def:
        managed_bindings = linker_client.linker.list(resource_uri=containerapp_def["id"])
        service_binds = containerapp_def["properties"].get("template", {}).get("serviceBinds", [])

        if managed_bindings:
            all_bindings.extend([item.name for item in managed_bindings])
        if service_binds:
            all_bindings.extend([item["name"] for item in service_binds])

    service_binding_names = [service_bind["name"] for service_bind in service_bindings_def_list]
    linker_names = [connector["linker_name"] for connector in service_connectors_def_list]

    all_bindings_set = set(all_bindings)
    service_binding_names_set = set(service_binding_names)
    linker_names_set = set(linker_names)

    if len(all_bindings_set | service_binding_names_set | linker_names_set) != len(all_bindings_set) + len(
            service_binding_names_set) + len(linker_names_set):
        # There are duplicate elements across the lists
        return False
    elif len(all_bindings_set) + len(service_binding_names_set) + len(linker_names_set) != len(all_bindings) + len(
            service_binding_names) + len(linker_names):
        # There are duplicate elements within one or more of the lists
        return False
    else:
        # There are no duplicate elements among the lists or within any of the lists
        return True


def parse_service_bindings(cmd, service_bindings_list, resource_group_name, name):
    # Make it return both managed and dev bindings
    service_bindings_def_list = []
    service_connector_def_list = []

    for service_binding_str in service_bindings_list:
        parts = service_binding_str.split(",")
        arg_dict = {}

        for part in parts:
            key_value = part.split("=")

            if len(key_value) == 1:
                # This means we don't have comma separated args
                pass
            else:
                arg_dict[key_value[0]] = key_value[1]

        service_binding = parts[0].split(':')
        service_name = service_binding[0]

        if len(service_binding) == 1:
            binding_name = service_name
        else:
            binding_name = service_binding[1]

        if not validate_binding_name(binding_name):
            raise InvalidArgumentValueError("The Binding Name can only contain letters, numbers (0-9), periods ('.'), "
                                            "and underscores ('_'). The length must not be more than 60 characters. "
                                            "By default, the binding name is the same as the service name you specified "
                                            "[my-aca-pgaddon], but you can override the default and specify your own "
                                            "compliant binding name like this --bind my-aca-pgaddon[:my_aca_pgaddon].")

        resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceManagementClient)

        if "resourcegroup" in arg_dict:
            # Search in target rg
            resources = resource_client.resources.list_by_resource_group(
                arg_dict["resourcegroup"])
            resource_group_name = arg_dict["resourcegroup"]
        else:
            # Search in current rg
            resources = resource_client.resources.list_by_resource_group(
                resource_group_name)

        # Create a list with required items
        resource_list = []
        for item in resources:
            resource_list.append({"name": item.name, "type": item.type, "id": item.id})

        subscription_id = get_subscription_id(cmd.cli_ctx)

        # Will work for both create and update
        process_service(cmd, resource_list, service_name, arg_dict, subscription_id, resource_group_name,
                        name, binding_name, service_connector_def_list, service_bindings_def_list)

    return service_connector_def_list, service_bindings_def_list


def connected_env_check_cert_name_availability(cmd, resource_group_name, name, cert_name):
    name_availability_request = {}
    name_availability_request["name"] = cert_name
    name_availability_request["type"] = CONNECTED_ENV_CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE
    try:
        r = ConnectedEnvCertificateClient.check_name_availability(cmd, resource_group_name, name, name_availability_request)
    except CLIError as e:
        handle_raw_exception(e)
    return r


def validate_environment_location(cmd, location, resource_type=MANAGED_ENVIRONMENT_RESOURCE_TYPE):
    res_locations = list_environment_locations(cmd, resource_type=resource_type)

    allowed_locs = ", ".join(res_locations)

    if location:
        try:
            _ensure_location_allowed(cmd, location, CONTAINER_APPS_RP, resource_type)

            return location
        except Exception as e:  # pylint: disable=broad-except
            raise ValidationError("You cannot create a Containerapp environment in location {}. List of eligible locations: {}.".format(location, allowed_locs)) from e
    else:
        return res_locations[0]


def list_environment_locations(cmd, resource_type=MANAGED_ENVIRONMENT_RESOURCE_TYPE):
    providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
    resource_types = getattr(providers_client.get(CONTAINER_APPS_RP), 'resource_types', [])
    res_locations = []
    for res in resource_types:
        if res and getattr(res, 'resource_type', "") == resource_type:
            res_locations = getattr(res, 'locations', [])

    res_locations = [res_loc.lower().replace(" ", "").replace("(", "").replace(")", "") for res_loc in res_locations if res_loc.strip()]

    return res_locations


def is_docker_running():
    try:
        # Run a simple 'docker stats --no-stream' command to check if the Docker daemon is running
        command = ["docker", "stats", "--no-stream"]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            _, _ = process.communicate()
            return process.returncode == 0
    except Exception:
        return False


def get_pack_exec_path():
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bin_folder = os.path.join(dir_path, "bin")
        if not os.path.exists(bin_folder):
            os.makedirs(bin_folder)

        pack_cli_version = "v0.31.0"
        exec_zip_name = "pack"
        exec_local_name = f"pack-{pack_cli_version}"
        compressed_download_file_name = f"pack-{pack_cli_version}"
        host_os = platform.system()
        if host_os == "Windows":
            compressed_download_file_name = f"{compressed_download_file_name}-windows.zip"
            exec_zip_name = f"{exec_zip_name}.exe"
            exec_local_name = f"{exec_local_name}.exe"
        elif host_os == "Linux":
            compressed_download_file_name = f"{compressed_download_file_name}-linux.tgz"
        elif host_os == "Darwin":
            compressed_download_file_name = f"{compressed_download_file_name}-macos.tgz"
        else:
            raise Exception(f"Unsupported host OS: {host_os}")

        exec_zip_path = os.path.join(bin_folder, exec_zip_name)
        exec_local_path = os.path.join(bin_folder, exec_local_name)
        if os.path.exists(exec_local_path):
            return exec_local_path

        # Attempt to install the pack CLI
        url = f"https://github.com/buildpacks/pack/releases/download/{pack_cli_version}/{compressed_download_file_name}"
        with urlopen(url) as req:
            compressed_file = io.BytesIO(req.read())
            if host_os == "Windows":
                with zipfile.ZipFile(compressed_file) as zip_file:
                    for file in zip_file.namelist():
                        if file.endswith(exec_zip_name):
                            with open(exec_zip_path, "wb") as f:
                                f.write(zip_file.read(file))
            else:
                with tarfile.open(fileobj=compressed_file, mode="r:gz") as tar:
                    for tar_info in tar:
                        if tar_info.isfile() and tar_info.name.endswith(exec_zip_name):
                            with open(exec_zip_path, "wb") as f:
                                f.write(tar.extractfile(tar_info).read())

        # Rename the executable to include the pack CLI version (to ensure future pack CLI versions are installed and consumed)
        os.rename(exec_zip_path, exec_local_path)

        # Add executable permissions for the current user if they don't exist
        if not os.access(exec_local_path, os.X_OK):
            st = os.stat(exec_local_path)
            os.chmod(exec_local_path, st.st_mode | stat.S_IXUSR)

        # Ensure that experimental features are enabled for the pack CLI
        command = [exec_local_path, "config", "experimental", "true"]
        logger.debug(f"Calling '{' '.join(command)}'")
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise CLIError(f"Error thrown when running 'pack config experimental true': {stderr.decode('utf-8')}")
            logger.debug("Successfully enabled experimental features for the installed pack CLI.")

        return exec_local_path
    except Exception as e:
        # Swallow any exceptions thrown when attempting to install pack CLI
        logger.warning(f"Failed to install pack CLI: {e}\n")

    return None


def patchable_check(base_run_image_name, oryx_run_images, inspect_result):
    # (1) Check if the base run image is based from a supported MCR repository.
    # (2) Fetch all of the supported Oryx run image tags from MCR and compare the version
    # of the provided base run image with the latest version of a compatible Oryx run image from MCR.
    MCR_PREFIX = "mcr.microsoft.com/"
    result = {
        "targetContainerAppName": inspect_result["targetContainerAppName"],
        "targetContainerName": inspect_result["targetContainerName"],
        "targetContainerAppEnvironmentName": inspect_result["targetContainerAppEnvironmentName"],
        "targetResourceGroup": inspect_result["targetResourceGroup"],
        "targetImageName": inspect_result["image_name"],
        "oldRunImage": base_run_image_name,
        "newRunImage": None,
        "id": None,
    }

    # Check if the provided base run image is based from a supported MCR repository
    if not base_run_image_name.startswith(MCR_PREFIX):
        return result.update(reason="Image is not based from an MCR repository.")

    base_run_image_split = base_run_image_name.split(":")
    base_run_image_no_tag = base_run_image_split[0]                         # e.g., "mcr.microsoft.com/oryx/dotnetcore"
    base_run_image_repository = base_run_image_no_tag.split(MCR_PREFIX)[1]  # e.g., "oryx/dotnetcore"
    base_run_image_framework = base_run_image_repository.split("/")[1]      # e.g., "dotnetcore"
    base_run_image_tag = base_run_image_split[1]                            # e.g., "7.0.9-debian-buster"

    # Parse the provided base run image to pull properties from the tag
    tag_prop = parse_oryx_run_image(base_run_image_repository, base_run_image_tag)

    # Check if the provided base run image has at least a patch version specified in the tag
    if len(str(tag_prop["version"]).split(".")) < 3:
        return result.update(reason="Image is based from a version of its run image that does not contain at least a patch identifier.")

    version_key = _get_oryx_run_image_version_key(tag_prop, base_run_image_framework)

    # Fetch the latest version of the provided base run image's framework from the MCR tag dictionary
    matching_version_info = oryx_run_images[tag_prop["framework"]][version_key][tag_prop["support"]][tag_prop["os"]]

    # Check if any MCR versions were found for the given tag
    if matching_version_info is None:
        return result.update(reason="No existing MCR version found for the base run image.")

    # Check if the current image can be patched by the latest MCR version of the same version key (major or minor version)
    if tag_prop["version"] < matching_version_info[0]["version"]:
        current_minor_ver = tag_prop["version"].minor
        current_patch_ver = tag_prop["version"].micro
        current_post_ver = tag_prop["version"].post
        latest_minor_ver = matching_version_info[0]["version"].minor
        latest_patch_ver = matching_version_info[0]["version"].micro
        latest_post_ver = matching_version_info[0]["version"].post

        # Check if the current image can be updated to the latest image available on MCR for the given version key
        if current_minor_ver < latest_minor_ver or (current_minor_ver == latest_minor_ver and current_patch_ver < latest_patch_ver) or (current_patch_ver == latest_patch_ver and current_post_ver < latest_post_ver):
            result["newRunImage"] = "{}:{}".format(base_run_image_no_tag, matching_version_info[0]["fullTag"])
            result["id"] = hashlib.md5(str(result["oldRunImage"] + result["targetContainerName"] + result["targetContainerAppName"] + result["targetResourceGroup"] + result["newRunImage"]).encode()).hexdigest()
            result["reason"] = "New security patch released for your current run image."
        else:
            result["reason"] = "The image is not patchable. Please check for major or minor version upgrade."
    # If the image latest image isn't newer than the current image, then the image is not patchable
    else:
        result["reason"] = "The image is already up to date."
    return result


def get_oryx_run_image_tags() -> dict:
    result = {}
    result.update(_get_oryx_run_image_tags("https://mcr.microsoft.com/v2/oryx/dotnetcore/tags/list", parse_oryx_run_image))
    result.update(_get_oryx_run_image_tags("https://mcr.microsoft.com/v2/oryx/node/tags/list", parse_oryx_run_image))
    result.update(_get_oryx_run_image_tags("https://mcr.microsoft.com/v2/oryx/python/tags/list", parse_oryx_run_image))
    result.update(_get_oryx_run_image_tags("https://mcr.microsoft.com/v2/azure-buildpacks/java/tags/list", parse_oryx_run_image))

    # Return the merged result of all Oryx-supported platform tags
    return result


def _get_oryx_run_image_tags(tags_list_url, tag_parse_func) -> dict:
    r = requests.get(tags_list_url, timeout=30)
    response = r.json()
    image_repository = response["name"]  # e.g., "oryx/dotnetcore" for "https://mcr.microsoft.com/v2/oryx/dotnetcore/tags/list"
    tag_dict = {}

    tags = list(response["tags"])
    for tag in tags:
        tag_obj = tag_parse_func(image_repository, tag)
        if tag_obj:
            support = tag_obj["support"]
            framework = tag_obj["framework"]
            os_prop = tag_obj["os"]
            version_key = _get_oryx_run_image_version_key(tag_obj, framework)
            if framework not in tag_dict:
                tag_dict[framework] = {version_key: {support: {os_prop: [tag_obj]}}}
            elif version_key not in tag_dict[framework]:
                tag_dict[framework][version_key] = {support: {os_prop: [tag_obj]}}
            elif support not in tag_dict[framework][version_key]:
                tag_dict[framework][version_key][support] = {os_prop: [tag_obj]}
            elif os_prop not in tag_dict[framework][version_key][support]:
                tag_dict[framework][version_key][support][os_prop] = [tag_obj]
            else:
                tag_dict[framework][version_key][support][os_prop].append(tag_obj)
                tag_dict[framework][version_key][support][os_prop].sort(reverse=True, key=lambda x: x["version"])
    return tag_dict


def _get_oryx_run_image_version_key(tag_obj, framework):
    # Updates within a single Node "ecosystem" can be done at both a minor and patch version level
    # e.g., patching from 18.16.1 --> 18.17.1 is valid
    if framework == "node":
        return str(tag_obj["version"].major)

    # Other platforms, such as .NET and Python, have their updates only at a patch version level
    # e.g., patching from .NET 7.0.9 --> 7.0.12 or Python 3.10.4 --> 3.10.8 is valid
    return str(tag_obj["version"].major) + "." + str(tag_obj["version"].minor)


def parse_oryx_run_image(image_repository, tag) -> OryxRunImageTagProperty:
    # Example Oryx run image: mcr.microsoft.com/oryx/<platform>:<version>-<os>
    # Note: image_repository should NOT include the "mcr.microsoft.com/" prefix; it should ONLY be the repository
    re_matches = re.findall(r"(oryx|azure-buildpacks)/([A-Za-z]*):([0-9.]*)-([A-Za-z-]*)",
                            "{}:{}".format(image_repository, tag))
    if len(re_matches) == 0 or len(re_matches[0]) < 4:
        return None
    return dict(fullTag=tag, framework=re_matches[0][1], version=SemVer.parse(re_matches[0][2]), os=re_matches[0][3], architectures=None, support="lts")


def get_custom_location(cmd, custom_location_id):
    parsed_custom_loc = parse_resource_id(custom_location_id)
    subscription_id = parsed_custom_loc.get("subscription")
    custom_loc_name = parsed_custom_loc.get("name")
    custom_loc_rg = parsed_custom_loc.get("resource_group")
    custom_location = None
    try:
        custom_location = custom_location_client_factory(cmd.cli_ctx, subscription_id=subscription_id).get(resource_group_name=custom_loc_rg, resource_name=custom_loc_name)
    except ResourceNotFoundError:
        pass
    return custom_location


def get_cluster_extension(cmd, cluster_extension_id=None):
    parsed_extension = parse_resource_id(cluster_extension_id)
    subscription_id = parsed_extension.get("subscription")
    cluster_rg = parsed_extension.get("resource_group")
    cluster_rp = parsed_extension.get("namespace")
    cluster_type = parsed_extension.get("type")
    cluster_name = parsed_extension.get("name")
    resource_name = parsed_extension.get("resource_name")

    return k8s_extension_client_factory(cmd.cli_ctx, subscription_id=subscription_id).get(
        resource_group_name=cluster_rg,
        cluster_rp=cluster_rp,
        cluster_resource_name=cluster_type,
        cluster_name=cluster_name,
        extension_name=resource_name)


def validate_custom_location(cmd, custom_location=None):
    if not is_valid_resource_id(custom_location):
        raise ValidationError('{} is not a valid Azure resource ID.'.format(custom_location))

    r = get_custom_location(cmd=cmd, custom_location_id=custom_location)
    if r is None:
        raise ResourceNotFoundError("Cannot find custom location with custom location ID {}".format(custom_location))

    # check extension type
    extension_existing = False
    for extension_id in r.cluster_extension_ids:
        extension = get_cluster_extension(cmd, extension_id)
        if extension.extension_type.lower() == CONTAINER_APP_EXTENSION_TYPE.lower():
            extension_existing = True
            break
    if not extension_existing:
        raise ValidationError('There is no Microsoft.App.Environment extension found associated with custom location {}'.format(custom_location))
    return r.location


def log_in_file(log_text, opened_file, no_print=False):
    if not no_print:
        print(log_text)

    cleaned_log_text = remove_ansi_characters(log_text.strip())
    opened_file.write(f"{cleaned_log_text}\n")


def remove_ansi_characters(text):
    regular_expression = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return regular_expression.sub("", text)
