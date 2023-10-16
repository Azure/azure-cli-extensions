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

from azure.cli.command_modules.containerapp._utils import safe_get
from azure.cli.command_modules.containerapp._client_factory import handle_raw_exception
from azure.cli.core.azclierror import (ValidationError, ResourceNotFoundError, CLIError, InvalidArgumentValueError)
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.mgmt.resource import ResourceManagementClient

from knack.log import get_logger
from msrestazure.tools import parse_resource_id, is_valid_resource_id

from ._managed_service_utils import ManagedRedisUtils, ManagedCosmosDBUtils, ManagedPostgreSQLFlexibleUtils, ManagedMySQLFlexibleUtils
from ._clients import ConnectedEnvCertificateClient, ContainerAppPreviewClient
from ._client_factory import custom_location_client_factory, k8s_extension_client_factory
from ._models import OryxMarinerRunImgTagProperty
from ._constants import (CONTAINER_APP_EXTENSION_TYPE,
                         CONNECTED_ENV_CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE, DEV_SERVICE_LIST)

logger = get_logger(__name__)


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

        pack_cli_version = "v0.29.0"
        exec_name = "pack"
        compressed_download_file_name = f"pack-{pack_cli_version}"
        host_os = platform.system()
        if host_os == "Windows":
            compressed_download_file_name = f"{compressed_download_file_name}-windows.zip"
            exec_name = "pack.exe"
        elif host_os == "Linux":
            compressed_download_file_name = f"{compressed_download_file_name}-linux.tgz"
        elif host_os == "Darwin":
            compressed_download_file_name = f"{compressed_download_file_name}-macos.tgz"
        else:
            raise Exception(f"Unsupported host OS: {host_os}")

        exec_path = os.path.join(bin_folder, exec_name)
        if os.path.exists(exec_path):
            return exec_path

        # Attempt to install the pack CLI
        url = f"https://github.com/buildpacks/pack/releases/download/{pack_cli_version}/{compressed_download_file_name}"
        with urlopen(url) as req:
            compressed_file = io.BytesIO(req.read())
            if host_os == "Windows":
                with zipfile.ZipFile(compressed_file) as zip_file:
                    for file in zip_file.namelist():
                        if file.endswith(exec_name):
                            with open(exec_path, "wb") as f:
                                f.write(zip_file.read(file))
            else:
                with tarfile.open(fileobj=compressed_file, mode="r:gz") as tar:
                    for tar_info in tar:
                        if tar_info.isfile() and tar_info.name.endswith(exec_name):
                            with open(exec_path, "wb") as f:
                                f.write(tar.extractfile(tar_info).read())

        # Add executable permissions for the current user if they don't exist
        if not os.access(exec_path, os.X_OK):
            st = os.stat(exec_path)
            os.chmod(exec_path, st.st_mode | stat.S_IXUSR)

        return exec_path
    except Exception as e:
        # Swallow any exceptions thrown when attempting to install pack CLI
        logger.warning(f"Failed to install pack CLI: {e}\n")

    return None


def patchable_check(repo_tag_split: str, oryx_builder_run_img_tags, inspect_result):
    # Check if the run image is based from a dotnet Mariner image in mcr.microsoft.com/oryx/builder
    # Get all the dotnet mariner run image tags from mcr.microsoft.com/oryx/builder and
    # compare the customer's run image with the latest patch version of the run image
    tag_prop = parse_oryx_mariner_tag(repo_tag_split)
    # Parsing the tag to a tag object
    result = {
        "targetContainerAppName": inspect_result["targetContainerAppName"],
        "targetContainerName": inspect_result["targetContainerName"],
        "targetContainerAppEnvironmentName": inspect_result["targetContainerAppEnvironmentName"],
        "targetResourceGroup": inspect_result["targetResourceGroup"],
        "targetImageName": inspect_result["image_name"],
        "oldRunImage": repo_tag_split,
        "newRunImage": None,
        "id": None,
    }
    if tag_prop is None:
        # If customer run image is not dotnet and tag doesn't match with oryx run image tag format,
        # return the result with the reason
        result["reason"] = "Image not based from a Mariner tag in mcr.microsoft.com/oryx/dotnet."
        return result
    elif len(str(tag_prop["version"]).split(".")) == 2:
        # If customer run image is dotnet, but the tag doesn't contain a patch version
        # e.g.: run-dontnet-aspnet-7.0-cbl-mariner2.0-xxxxxxx
        result["reason"] = "Image is using a run image version that doesn't contain a patch information."
        return result
    repo_tag_split = repo_tag_split.split("-")
    if repo_tag_split[1] == "dotnet":
        # If customer run image is dotnet, and successfully parsed, check if the run image is based from a dotnet Mariner image in mcr.microsoft.com/oryx/builder
        # Indexing to the correct framework, support, major and minor version, and mariner version
        # e.g.: run_img_tags -> framework -> support -> major.minor -> mariner version
        matching_version_info = oryx_builder_run_img_tags[repo_tag_split[2]][str(tag_prop["version"].major) + "." + str(tag_prop["version"].minor)][tag_prop["support"]][tag_prop["marinerVersion"]]
    # Check if the image minor version is less than the latest minor version
    if tag_prop["version"] < matching_version_info[0]["version"]:
        result["oldRunImage"] = tag_prop["fullTag"]
        if (tag_prop["version"].minor == matching_version_info[0]["version"].minor) and (tag_prop["version"].micro < matching_version_info[0]["version"].micro):
            # Patchable
            result["newRunImage"] = "mcr.microsoft.com/oryx/builder:" + matching_version_info[0]["fullTag"]
            result["id"] = hashlib.md5(str(result["oldRunImage"] + result["targetContainerName"] + result["targetContainerAppName"] + result["targetResourceGroup"] + result["newRunImage"]).encode()).hexdigest()
            result["reason"] = "New security patch released for your current run image."
        else:
            # Not patchable
            result["newRunImage"] = "mcr.microsoft.com/oryx/builder:" + matching_version_info[0]["fullTag"]
            result["id"] = None
            result["reason"] = "The image is not patchable. Please check for major or minor version upgrade."
    else:
        # Image is already up to date
        result["oldRunImage"] = tag_prop["fullTag"]
        result["reason"] = "The image is already up to date."
    return result


def get_current_mariner_tags() -> list(OryxMarinerRunImgTagProperty):
    r = requests.get("https://mcr.microsoft.com/v2/oryx/builder/tags/list", timeout=30)
    tags = r.json()
    tag_list = {}
    # only keep entries that contain keyword "mariner"
    tags = [tag for tag in tags["tags"] if "mariner" in tag]
    for tag in tags:
        tag_obj = parse_oryx_mariner_tag(tag)
        if tag_obj:
            major_minor_ver = str(tag_obj["version"].major) + "." + str(tag_obj["version"].minor)
            support = tag_obj["support"]
            framework = tag_obj["framework"]
            mariner_ver = tag_obj["marinerVersion"]
            if framework not in tag_list:
                tag_list[framework] = {major_minor_ver: {support: {mariner_ver: [tag_obj]}}}
            elif major_minor_ver not in tag_list[framework]:
                tag_list[framework][major_minor_ver] = {support: {mariner_ver: [tag_obj]}}
            elif support not in tag_list[framework][major_minor_ver]:
                tag_list[framework][major_minor_ver][support] = {mariner_ver: [tag_obj]}
            elif mariner_ver not in tag_list[framework][major_minor_ver][support]:
                tag_list[framework][major_minor_ver][support][mariner_ver] = [tag_obj]
            else:
                tag_list[framework][major_minor_ver][support][mariner_ver].append(tag_obj)
                tag_list[framework][major_minor_ver][support][mariner_ver].sort(reverse=True, key=lambda x: x["version"])
    return tag_list


def get_latest_buildpack_run_tag(framework, version, support="lts", mariner_version="cbl-mariner2.0"):
    tags = get_current_mariner_tags()
    try:
        return tags[framework][version][support][mariner_version][0]["fullTag"]
    except KeyError:
        return None


def parse_oryx_mariner_tag(tag: str) -> OryxMarinerRunImgTagProperty:
    tag_split = tag.split("-")
    if tag_split[0] == "run" and tag_split[1] == "dotnet":
        # Example: run-dotnet-aspnet-7.0.1-cbl-mariner2.0-20210415.1
        # Result: tag_obj = {
        #    "fullTag": "run-dotnet-aspnet-7.0.1-cbl-mariner2.0-20210415.1",
        #    "version": "7.0.1",
        #    "framework": "aspnet",
        #    "marinerVersion": "cbl-mariner2.0",
        #    "architectures": None,
        #    "support": "lts"}
        version_re = r"(\d+\.\d+(\.\d+)?).*?(cbl-mariner(\d+\.\d+))"
        re_matches = re.findall(version_re, tag)
        if len(re_matches) == 0:
            tag_obj = None
        else:
            tag_obj = dict(fullTag=tag, version=SemVer.parse(re_matches[0][0]), framework=tag_split[2], marinerVersion=re_matches[0][2], architectures=None, support="lts")
    else:
        tag_obj = None
    return tag_obj


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
                containerapp_def = ContainerAppPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name,
                                                           name=service_name)

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


def validate_binding_name(binding_name):
    pattern = r'^(?=.{1,60}$)[a-zA-Z0-9._]+$'
    return bool(re.match(pattern, binding_name))


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
