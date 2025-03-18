# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import stat
import tarfile
import time
from glob import glob
from typing import List, Optional

import oras.client  # type: ignore[import-untyped]
from azure.cli.core import azclierror, telemetry
from azure.cli.core.style import Style, print_styled_text
from knack import log
from knack.commands import CLICommand

import azext_connectedk8s._constants as consts
import azext_connectedk8s._fileutils as file_utils

logger = log.get_logger(__name__)


# Downloads client side proxy to connect to Arc Connectivity Platform
def install_client_side_proxy(
    cmd: CLICommand,
    arc_proxy_folder: Optional[str], debug: bool = False
) -> str:
    client_operating_system = _get_client_operating_system()
    client_architecture = _get_client_architeture()
    install_dir = _get_proxy_install_dir(arc_proxy_folder)
    proxy_name = _get_proxy_filename(client_operating_system, client_architecture)
    install_location = os.path.join(install_dir, proxy_name)

    # Only download new proxy if it doesn't exist already
    try:
        if not os.path.isfile(install_location):
            if not os.path.isdir(install_dir):
                file_utils.create_directory(
                    install_dir,
                    f"Failed to create client proxy directory '{install_dir}'.",
                )
            # if directory exists, delete any older versions of the proxy
            else:
                older_version_location = _get_older_version_proxy_path(install_dir)
                older_version_files = glob(older_version_location)
                for f in older_version_files:
                    file_utils.delete_file(
                        f, f"failed to delete older version file {f}", warning=True
                    )

            _download_proxy_from_MCR(
                cmd, install_dir, proxy_name, client_operating_system, client_architecture
            )
            _check_proxy_installation(install_dir, proxy_name, debug)

    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Create_CSPExe_Fault_Type,
            summary="Unable to create proxy executable",
        )
        raise e

    return install_location


def _download_proxy_from_MCR(
    cmd: CLICommand, dest_dir: str, proxy_name: str, operating_system: str, architecture: str
) -> None:
    
    active_directory_array = cmd.cli_ctx.cloud.endpoints.active_directory.split(".")

    # default for public, mc, ff clouds
    mcr_postfix = active_directory_array[2]
    # special cases for USSec, exclude part of suffix
    if len(active_directory_array) == 4 and active_directory_array[2] == "microsoft":
        mcr_postfix = active_directory_array[3]
    # special case for USNat
    elif len(active_directory_array) == 5:
        mcr_postfix = active_directory_array[2] + "." + active_directory_array[3] + "." + active_directory_array[4]

    mcr_url = f"mcr.microsoft.{mcr_postfix}"

    mar_target = f"{mcr_url}/{consts.CLIENT_PROXY_MCR_TARGET}/{operating_system.lower()}/{architecture}/arc-proxy"
    logger.debug(
        "Downloading Arc Connectivity Proxy from %s in Microsoft Artifact Regristy.",
        mar_target,
    )

    client = oras.client.OrasClient()
    t0 = time.time()

    try:
        response = client.pull(
            target=f"{mar_target}:{consts.CLIENT_PROXY_VERSION}", outdir=dest_dir
        )
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Download_Exe_Fault_Type,
            summary="Unable to download clientproxy executable.",
        )
        raise azclierror.CLIInternalError(
            f"Failed to download Arc Connectivity proxy with error {e!s}. Please try again."
        )

    time_elapsed = time.time() - t0

    proxy_data = {
        "Context.Default.AzureCLI.ArcProxyDownloadTime": time_elapsed,
        "Context.Default.AzureCLI.ArcProxyVersion": consts.CLIENT_PROXY_VERSION,
    }
    telemetry.add_extension_event("connectedk8s", proxy_data)

    proxy_package_path = _get_proxy_package_path_from_oras_response(response)
    _extract_proxy_tar_files(proxy_package_path, dest_dir, proxy_name)
    file_utils.delete_file(
        proxy_package_path,
        f"Failed to delete {proxy_package_path}. Please delete manually.",
        True,
    )


def _get_proxy_package_path_from_oras_response(pull_response: List[str]) -> str:
    if not isinstance(pull_response, list):
        raise azclierror.CLIInternalError(
            "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again."
        )

    if len(pull_response) != 1:
        for r in pull_response:
            file_utils.delete_file(
                r, f"Failed to delete {r}. Please delete it manually.", True
            )
        raise azclierror.CLIInternalError(
            "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again."
        )

    proxy_package_path = pull_response[0]

    if not os.path.isfile(proxy_package_path):
        raise azclierror.CLIInternalError(
            "Unable to download Arc Connectivity Proxy. Please try again."
        )

    logger.debug("Proxy package downloaded to %s", proxy_package_path)

    return proxy_package_path


def _extract_proxy_tar_files(
    proxy_package_path: str, install_dir: str, proxy_name: str
) -> None:
    with tarfile.open(proxy_package_path, "r:gz") as tar:
        members = []
        for member in tar.getmembers():
            if member.isfile():
                filenames = member.name.split("/")

                if len(filenames) != 2:
                    tar.close()
                    file_utils.delete_file(
                        proxy_package_path,
                        f"Failed to delete {proxy_package_path}. Please delete it manually.",
                        True,
                    )
                    raise azclierror.CLIInternalError(
                        "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again."
                    )

                member.name = filenames[1]

                if member.name.startswith("arcproxy"):
                    member.name = proxy_name
                elif member.name.lower() not in ["license.txt", "thirdpartynotice.txt"]:
                    tar.close()
                    file_utils.delete_file(
                        proxy_package_path,
                        f"Failed to delete {proxy_package_path}. Please delete it manually.",
                        True,
                    )
                    raise azclierror.CLIInternalError(
                        "Attempt to download Arc Connectivity Proxy returned unnexpected result. Please try again."
                    )

                members.append(member)

        tar.extractall(members=members, path=install_dir)


def _check_proxy_installation(
    install_dir: str, proxy_name: str, debug: bool = False
) -> None:
    proxy_filepath = os.path.join(install_dir, proxy_name)
    os.chmod(proxy_filepath, os.stat(proxy_filepath).st_mode | stat.S_IXUSR)
    if os.path.isfile(proxy_filepath):
        if debug:
            print_styled_text(
                (
                    Style.SUCCESS,
                    f"Successfully installed Arc Connectivity Proxy file {proxy_filepath}",
                )
            )
    else:
        raise azclierror.CLIInternalError(
            "Failed to install required Arc Connectivity Proxy. "
            f"Couldn't find expected file {proxy_filepath}. Please try again."
        )

    license_files = ["LICENSE.txt", "ThirdPartyNotice.txt"]
    for file in license_files:
        file_location = os.path.join(install_dir, file)
        if os.path.isfile(file_location):
            if debug:
                print_styled_text(
                    (
                        Style.SUCCESS,
                        f"Successfully installed Arc Connectivity Proxy License file {file_location}",
                    )
                )
        else:
            logger.warning(
                "Failed to download Arc Connectivity Proxy license file %s. Couldn't find expected file %s. "
                "This won't affect your connection.",
                file,
                file_location,
            )


def _get_proxy_filename(operating_system: str, architecture: str) -> str:
    if operating_system.lower() == "darwin" and architecture == "386":
        raise azclierror.BadRequestError("Unsupported Darwin OS with 386 architecture.")
    proxy_filename = f"arcProxy_{operating_system.lower()}_{architecture}_{consts.CLIENT_PROXY_VERSION.replace('.', '_')}"
    if operating_system.lower() == "windows":
        proxy_filename += ".exe"
    return proxy_filename


def _get_older_version_proxy_path(
    install_dir: str,
) -> str:
    proxy_name = "arcProxy*"
    return os.path.join(install_dir, proxy_name)


def _get_proxy_install_dir(arc_proxy_folder: Optional[str]) -> str:
    if not arc_proxy_folder:
        return os.path.expanduser(os.path.join("~", consts.CLIENT_PROXY_FOLDER))
    return arc_proxy_folder


def _get_client_architeture() -> str:
    import platform

    machine = platform.machine()
    architecture = None

    logger.debug("Platform architecture: %s", machine)

    if "arm64" in machine.lower() or "aarch64" in machine.lower():
        architecture = "arm64"
    elif machine.endswith("64"):
        architecture = "amd64"
    elif machine.endswith("86"):
        architecture = "386"
    elif machine == "":
        raise azclierror.ClientRequestError(
            "Couldn't identify the platform architecture."
        )
    else:
        raise azclierror.ClientRequestError(
            f"Unsuported architecture: {machine} is not currently supported"
        )

    return architecture


def _get_client_operating_system() -> str:
    import platform

    operating_system = platform.system()

    if operating_system.lower() not in ("linux", "darwin", "windows"):
        telemetry.set_exception(
            exception="Unsupported OS",
            fault_type=consts.Unsupported_Fault_Type,
            summary=f"{operating_system} is not supported yet",
        )
        raise azclierror.ClientRequestError(
            f"The {operating_system} platform is not currently supported."
        )
    return operating_system
