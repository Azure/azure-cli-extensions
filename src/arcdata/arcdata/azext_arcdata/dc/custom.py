# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

"""Command definitions for `data control`."""

from azext_arcdata.vendored_sdks.arm_sdk.azure.export_util import (
    ExportType,
    check_prompt_export_output_file,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.client import KubernetesClient
from azext_arcdata.vendored_sdks.kubernetes_sdk.arc_docker_image_service import (
    ArcDataImageService,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.json_serialization import ExtendedJsonEncoder

from azext_arcdata.core.prompt import (
    prompt_for_input,
    prompt_for_choice,
    prompt_assert,
    prompt_y_n,
)
from azext_arcdata.core.util import DeploymentConfigUtil
from knack.prompting import NoTTYException
from knack.log import get_logger
from knack.cli import CLIError
from colorama import Fore

import json
import os
import shutil

logger = get_logger(__name__)


def dc_create(
    client,
    connectivity_mode,
    name,
    resource_group,
    **kwargs
):
    try:
        stdout = client.stdout
        path = kwargs.get("path", None)
        profile_name = kwargs.get("profile_name", None)
        no_wait = kwargs.get("no_wait", None)

        if not path and not profile_name:
            # Prompt the user for a choice between configs
            stdout("Please choose a deployment configuration: ")
            stdout(
                "To see more information please exit and use command:\n "
                "az arcdata dc config list -c <config_profile>"
            )

            config_dir = client.services.dc.get_deployment_config_dir()
            choices = client.services.dc.list_configs()
            profile = prompt_for_choice(choices).lower()
            path = os.path.join(config_dir, profile)
            logger.debug("Profile path: %s", path)

        # -- Apply Subscription --
        subscription = client.subscription or prompt_assert("Subscription: ")
        stdout("\nUsing subscription '{}'.\n".format(subscription))

        # -- Apply Configuration Directory --
        cvo = client.args_to_command_value_object(
            {
                "connectivity_mode": connectivity_mode,
                "name": name,
                "resource_group": resource_group,
                "location": kwargs.get("location", None),
                "profile_name": profile_name,
                "path": path,
                "storage_class": kwargs.get("storage_class", None),
                "infrastructure": kwargs.get("infrastructure", None),
                "image_tag": kwargs.get("image_tag", None),
                "labels": kwargs.get("labels", None),
                "annotations": kwargs.get("annotations", None),
                "service_annotations": kwargs.get("service_annotations", None),
                "service_labels": kwargs.get("service_labels", None),
                "storage_labels": kwargs.get("storage_labels", None),
                "storage_annotations": kwargs.get("storage_annotations", None),
                "logs_ui_public_key_file": kwargs.get("logs_ui_public_key_file", None),
                "logs_ui_private_key_file": kwargs.get("logs_ui_private_key_file", None),
                "metrics_ui_public_key_file": kwargs.get("metrics_ui_public_key_file", None),
                "metrics_ui_private_key_file": kwargs.get("metrics_ui_private_key_file", None),
                "subscription": subscription,
                "custom_location": kwargs.get("custom_location", None),
                "auto_upload_metrics": kwargs.get("auto_upload_metrics", None),
                "auto_upload_logs": kwargs.get("auto_upload_logs", None),
                "cluster_name": kwargs.get("cluster_name", None),
                "least_privilege": kwargs.get("least_privilege", None),
                "namespace": kwargs.get("namespace", None),
                "no_wait": no_wait,
            }
        )

        dc = client.services.dc.create(cvo)
        if no_wait:
            stdout(
                f"The data controller '{name}' is being created in the "
                f"background, to check status run:\n\naz arcdata dc status "
                f"show -n {name} -g {resource_group} --query properties."
                f"k8SRaw.status"
            )
        return dc
    except (NoTTYException, ValueError, Exception) as e:
        raise CLIError(e)


def dc_update(
    client,
    **kwargs
):
    """
    Update data controller properties.
    """
    if kwargs.get("Name") is None:
        raise CLIError("Data controller name is required for update.")

    try:
        cvo = client.args_to_command_value_object()
        return client.services.dc.update(cvo)
    except Exception as e:
        raise CLIError(e)


def dc_upgrade(
    client,
    namespace=None,
    desired_version=None,
    dry_run=None,
    resource_group=None,
    name=None,
    no_wait=False,
):
    try:
        cvo = client.args_to_command_value_object(
            {
                "namespace": namespace,
                "target": desired_version,
                "dry_run": dry_run,
                "no_wait": no_wait,
                "name": name,
                "resource_group": resource_group,
            }
        )
        client.services.dc.upgrade(cvo)
    except Exception as e:
        raise CLIError(e)


def mw_update(
    client,
    **kwargs
):
    """
    Pass-through maintenance window update command
    """
    if not kwargs:
        raise CLIError("At least one maintenance window property is required.")

    try:
        cvo = client.args_to_command_value_object()
        client.services.dc.update_maintenance_window(cvo)
    except Exception as e:
        raise CLIError(e)


def dc_list_upgrade(client, namespace, use_k8s=None):
    stdout = client.stdout
    try:
        cvo = client.args_to_command_value_object(
            {"namespace": namespace, "use_k8s": use_k8s}
        )
        current_version, versions = client.services.dc.list_upgrades(cvo)
        # - Only current version + later versions are valid
        valid_versions = [
            version
            for version in versions
            if ArcDataImageService.compare_version_tag(
                version, current_version, ignore_label=True
            )
            >= 0
        ]

        stdout(
            "Found {0} valid versions.  The current datacontroller version is "
            "{1}.".format(len(valid_versions), current_version)
        )

        for version in valid_versions:
            if version == current_version:
                stdout(
                    "{0} << current version".format(version),
                    color=Fore.LIGHTGREEN_EX,
                )
            else:
                stdout(version)
    except Exception as e:
        raise CLIError(e)


def dc_endpoint_list(client, namespace, endpoint_name=None):
    """
    Retrieves the endpoints of the cluster
    """
    try:
        cvo = client.args_to_command_value_object(
            {"namespace": namespace, "endpoint_name": endpoint_name}
        )
        return client.services.dc.list_endpoints(cvo)
    except Exception as e:
        raise CLIError(e)


def dc_status_show(
    client, name=None, resource_group=None, namespace=None, use_k8s=None
):
    """
    Return the status of the data controller custom resource.
    """
    try:
        cvo = client.args_to_command_value_object(
            {
                "name": name,
                "resource_group": resource_group,
                "namespace": namespace,
            }
        )
        state = client.services.dc.get_status(cvo)

        if use_k8s:
            client.stdout(state.lower().capitalize())
        else:
            return state
    except (ValueError, Exception) as e:
        raise CLIError(e)


def dc_config_show(client, namespace=None):
    """
    Return the config of the data controller custom resource.
    """
    try:
        cvo = client.args_to_command_value_object({"namespace": namespace})
        return client.services.dc.get_config(cvo)
    except Exception as e:
        raise CLIError(e)


def dc_delete(
    client,
    name,
    namespace=None,
    resource_group=None,
    force=None,
    yes=None,
    no_wait=False,
):
    """
    Deletes the data controller.
    """
    try:
        stdout = client.stdout

        if not yes:
            stdout("")
            stdout(
                "This operation will delete everything inside of data "
                "controller `{}` which includes the Kubernetes "
                "secrets and services, etc.".format(name)
            )
            stdout(
                "Data stored on persistent volumes will get deleted if the "
                "storage class reclaim policy is set to "
                "delete/recycle."
            )
            stdout("")

            yes = prompt_y_n(
                "Do you want to continue with deleting "
                "the data controller `{}`?".format(name)
            )

        if yes != "yes" and yes is not True:
            stdout("Data controller not deleted. Exiting...")
            return

        cvo = client.args_to_command_value_object(
            {
                "name": name,
                "resource_group": resource_group,
                "namespace": namespace,
                "force": force,
                "no_wait": no_wait,
            }
        )
        client.services.dc.delete(cvo)

        stdout("Data controller `{}` deleted successfully.".format(name))
    except NoTTYException:
        raise CLIError("Please specify `--yes` in non-interactive mode.")
    except Exception as e:
        raise CLIError(e)


def dc_list(
    client,
    resource_group=None,
):
    """
    Lists all the data controllers in the subscription or in the resource group.
    """
    try:
        cvo = client.args_to_command_value_object(
            {
                "resource_group": resource_group,
            }
        )
        return client.services.dc.list(cvo)
    except Exception as e:
        raise CLIError(e)


def dc_config_list(client, config_profile=None):
    """
    Lists available configuration file choices.
    """
    try:
        return client.services.dc.list_configs(config_profile)
    except (ValueError, Exception) as e:
        raise CLIError(e)


def dc_config_init(client, path=None, source=None, force=None):
    """
    Initializes a cluster configuration file for the user.
    """
    try:
        stdout = client.stdout
        config_dir = client.services.dc.get_deployment_config_dir()
        config_files = client.services.dc.get_deployment_config_files()

        try:
            if not path:
                path = prompt_for_input(
                    "Custom Config Profile Path:", "custom", False, False
                )
        except NoTTYException:
            # If non-interactive, default to custom directory
            path = "custom"

        # Read the available configs by name
        config_map = DeploymentConfigUtil.get_config_map(config_dir)

        if source:
            if not config_map.get(source, None):
                raise ValueError(
                    "Invalid config source, please consult [dc "
                    "config list] for available sources"
                )
        elif not source:
            choices = DeploymentConfigUtil.get_config_display_names(config_map)

            # Filter out test profiles
            filtered_choices = list(filter(lambda c: "test" not in c, choices))

            # Prompt the user for a choice between configs
            stdout("Please choose a config:")
            source = prompt_for_choice(filtered_choices, choices[8])

        if os.path.isfile(path):
            raise FileExistsError(
                "Please specify a directory path. Path is a file: {0}".format(
                    path
                )
            )

        result = DeploymentConfigUtil.save_config_profile(
            path, source, config_dir, config_files, config_map, force
        )

        client.stdout("Created configuration profile in {}".format(result))
    except NoTTYException:
        raise CLIError("Please specify path and source in non-interactive mode")
    except (ValueError, Exception) as e:
        raise CLIError(e)


def dc_config_add(client, config_file, json_values):
    """
    Add new key and value to the given config file
    """
    _ = client  # pylint: disable=unused-argument

    try:
        config_object = DeploymentConfigUtil.config_add(
            config_file, json_values
        )
        DeploymentConfigUtil.write_config_file(config_file, config_object)
    except Exception as e:
        raise CLIError(e)


def dc_config_replace(client, config_file, json_values):
    """
    Replace the value of a given key in the given config file
    """
    _ = client  # pylint: disable=unused-argument

    try:
        config_object = DeploymentConfigUtil.config_replace(
            config_file, json_values
        )
        DeploymentConfigUtil.write_config_file(config_file, config_object)
    except Exception as e:
        raise CLIError(e)


def dc_config_remove(client, config_file, json_path):
    """
    Remove a key from the given config file
    """
    _ = client  # pylint: disable=unused-argument

    try:
        config_object = DeploymentConfigUtil.config_remove(
            config_file, json_path
        )
        DeploymentConfigUtil.write_config_file(config_file, config_object)
    except Exception as e:
        raise CLIError(e)


def dc_config_patch(client, config_file, patch_file):
    """
    Patch a given file against the given config file
    """
    _ = client  # pylint: disable=unused-argument

    try:
        config_object = DeploymentConfigUtil.config_patch(
            config_file, patch_file
        )
        DeploymentConfigUtil.write_config_file(config_file, config_object)
    except Exception as e:
        raise CLIError(e)


def dc_debug_copy_logs(
    client,
    namespace,
    container=None,
    target_folder=None,
    pod=None,
    resource_kind=None,
    resource_name=None,
    timeout=0,
    skip_compress=False,
    exclude_dumps=False,
    exclude_arcdata_logs=False,
    exclude_system_logs=False,
    exclude_controldb=False,
    exclude_cluster_info=False,
):
    """
    Copy Logs commands - requires kube config
    """
    try:
        client.services.dc.copy_logs(
            namespace,
            target_folder=target_folder,
            pod=pod,
            container=container,
            resource_kind=resource_kind,
            resource_name=resource_name,
            timeout=timeout,
            skip_compress=skip_compress,
            exclude_dumps=exclude_dumps,
            exclude_arcdata_logs=exclude_arcdata_logs,
            exclude_system_logs=exclude_system_logs,
            exclude_controldb=exclude_controldb,
            exclude_cluster_info=exclude_cluster_info,
        )
    except Exception as e:
        raise CLIError(e)


def dc_debug_dump(
    client,
    namespace,
    container="controller",
    target_folder="./output/dump",
):
    """
    Trigger dump for given container and copy out the dump file to given
    output folder
    """
    try:
        client.services.dc.capture_debug_dump(
            namespace, container, target_folder
        )
    except (NotImplementedError, Exception) as e:
        raise CLIError(e)


def dc_debug_restore_controldb_snapshot(
    client,
    namespace,
    backup_file,
):
    """
    Restores ControlDB from existing backup file under a unique database name - requires kube config
    """
    try:
        client.services.dc.restore_controldb_snapshot(
            namespace,
            backup_file,
        )
    except Exception as e:
        raise CLIError(e)


def dc_debug_controldb_cdc(
    client,
    namespace,
    enable=None,
    retention_hours=None,
):
    """
    Enables or Disables Change Data Capture for 'controller' Database and supported system tables - requires kube config
    """
    try:
        client.services.dc.controldb_cdc(
            namespace,
            enable,
            retention_hours,
        )
    except Exception as e:
        raise CLIError(e)


def dc_export(client, export_type, path, namespace, force=None):
    """
    Export metrics, logs or usage to a file.
    """
    try:
        if export_type.lower() not in ExportType.list():
            raise ValueError(
                "{} is not a supported type. "
                "Please specify one of the following: {}".format(
                    export_type, ExportType.list()
                )
            )

        path = check_prompt_export_output_file(path, force)

        client.services.dc.export(namespace, export_type, path)
    except NoTTYException:
        raise CLIError("Please specify `--force` in non-interactive mode.")
    except Exception as e:
        raise CLIError(e)


def arc_resource_kind_list(client):
    """
    Returns the list of available arc resource kinds which can be created in
    the cluster.
    """
    try:
        return list(client.services.dc.get_crd_dict().keys())
    except Exception as e:
        raise CLIError(e)


def arc_resource_kind_get(client, kind, dest="template"):
    """
    Returns a package of crd.json and spec-template.json based on the given
    kind.
    """
    try:
        if not os.path.isdir(dest):
            os.makedirs(dest, exist_ok=True)

        crd_dict = client.services.dc.get_crd_dict()
        spec_file_dict = client.services.dc.get_spec_file_dict()

        # Make the resource name case insensitive
        local_crd_dict = {k.lower(): v for k, v in crd_dict.items()}
        local_spec_file_dict = {k.lower(): v for k, v in spec_file_dict.items()}
        kind_lower_case = kind.lower()

        if (
            kind_lower_case not in local_crd_dict
            or kind_lower_case not in local_spec_file_dict
        ):
            raise ValueError(
                "Invalid input kind. Please check resource kind list."
            )

        # Create the control plane CRD for the input kind.
        crd_name = local_crd_dict[kind_lower_case]
        crd = KubernetesClient.get_crd(crd_name).to_dict()

        # clean up fields not needed
        crd["metadata"].pop("managed_fields", None)
        crd.pop("status", None)

        with open(os.path.join(dest, "crd.json"), "w") as output:
            json.dump(
                crd,
                output,
                check_circular=False,
                cls=ExtendedJsonEncoder,
                indent=4,
            )

        # Copy spec.json template to the new path
        spec_file_path = local_spec_file_dict[kind_lower_case]
        shutil.copy(spec_file_path, os.path.join(dest, "spec.json"))

        client.stdout(
            "{0} template created in directory: {1}".format(kind, dest)
        )

    except (ValueError, Exception) as e:
        raise CLIError(e)


def dc_upload(client, path):
    """
    Upload data file exported from a data controller to Azure (indirect only).
    """
    try:
        cvo = client.args_to_command_value_object(path=path)
        return client.services.dc.export_upload_log_and_metrics(cvo)
    except ValueError as e:
        raise CLIError(e)
    except Exception as e:
        raise CLIError(e)
