# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
import tempfile
from datetime import datetime

from knack.log import get_logger
from knack.util import CLIError

from azure.cli.command_modules.acr._archive_utils import upload_source_code
from azure.cli.command_modules.acr._stream_utils import stream_logs
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.commands import LongRunningOperation

logger = get_logger(__name__)


def queue_acr_build(cmd, registry_rg, registry_name, img_name, src_dir):
    import os
    client_registries = get_acr_service_client(cmd.cli_ctx).registries

    if not os.path.isdir(src_dir):
        raise CLIError("Source directory should be a local directory path.")

    docker_file_path = os.path.join(src_dir, "Dockerfile")
    if not os.path.isfile(docker_file_path):
        raise CLIError("Unable to find '{}'.".format(docker_file_path))

    # NOTE: os.path.basename is unable to parse "\" in the file path
    original_docker_file_name = os.path.basename(
        docker_file_path.replace("\\", "/"))
    docker_file_in_tar = '{}_{}'.format(
        uuid.uuid4().hex, original_docker_file_name)
    tar_file_path = os.path.join(tempfile.gettempdir(), 'build_archive_{}.tar.gz'.format(uuid.uuid4().hex))

    source_location = upload_source_code(
        client_registries, registry_name, registry_rg,
        src_dir, tar_file_path,
        docker_file_path, docker_file_in_tar)
    # For local source, the docker file is added separately into tar as the new file name (docker_file_in_tar)
    # So we need to update the docker_file_path
    docker_file_path = docker_file_in_tar

    from azure.cli.core.profiles import ResourceType
    OS, Architecture = cmd.get_models('OS', 'Architecture', resource_type=ResourceType.MGMT_CONTAINERREGISTRY)
    # Default platform values
    platform_os = OS.linux.value
    platform_arch = Architecture.amd64.value
    platform_variant = None

    DockerBuildRequest, PlatformProperties = cmd.get_models('DockerBuildRequest', 'PlatformProperties',
                                                            resource_type=ResourceType.MGMT_CONTAINERREGISTRY)
    docker_build_request = DockerBuildRequest(
        image_names=[img_name],
        is_push_enabled=True,
        source_location=source_location,
        platform=PlatformProperties(
            os=platform_os,
            architecture=platform_arch,
            variant=platform_variant
        ),
        docker_file_path=docker_file_path,
        timeout=None,
        arguments=[])

    queued_build = LongRunningOperation(cmd.cli_ctx)(client_registries.schedule_run(
        resource_group_name=registry_rg,
        registry_name=registry_name,
        run_request=docker_build_request))

    run_id = queued_build.run_id
    logger.warning("Queued a build with ID: %s", run_id)
    logger.warning("Waiting for agent...")

    client_runs = get_acr_service_client(cmd.cli_ctx).runs

    return stream_logs(client_runs, run_id, registry_name, registry_rg, False, True)


def get_acr_service_client(cli_ctx, api_version=None):
    """Returns the client for managing container registries. """
    from azure.mgmt.containerregistry import ContainerRegistryManagementClient
    return get_mgmt_service_client(cli_ctx, ContainerRegistryManagementClient, api_version=api_version)


def generate_img_name(src_dir):
    import os
    img_name = os.path.basename(src_dir) + ':' + datetime.now().strftime('%Y%m%d_%H%M%S')
    return img_name
