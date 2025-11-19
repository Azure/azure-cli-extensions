# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.vendored_sdks.arm_sdk.azure.constants import (
    INSTANCE_TYPE_DATA_CONTROLLER,
    RESOURCE_PROVIDER_NAMESPACE,
)
from azure.cli.core.commands.parameters import get_resource_name_completion_list
from azext_arcdata.core.util import DeploymentConfigUtil
from azext_arcdata.core.constants import (
    USE_K8S_TEXT,
    CLI_ARG_GROUP_DIRECT_TEXT,
    CLI_ARG_GROUP_INDIRECT_TEXT,
    CLI_ARG_RESOURCE_GROUP_TEXT,
    CLI_ARG_GROUP_USE_K8S,
)
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import CONFIG_DIR
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.common_util import (
    get_valid_dc_infrastructures,
)


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext
    from argparse import SUPPRESS

    with ArgumentsContext(self, "arcdata dc create") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name for the data controller.",
        )
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            help=CLI_ARG_RESOURCE_GROUP_TEXT,
        )
        arg_context.argument(
            "location",
            options_list=["--location", "-l"],
            help="The Azure location in which the data controller "
            "metadata will be stored (e.g. eastus).",
        )
        arg_context.argument(
            "connectivity_mode",
            options_list=["--connectivity-mode"],
            help="The connectivity to Azure - direct - in which the "
            "data controller should operate (indirect mode has been deprecated).",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace to deploy the data "
            "controller into. If it exists already it will be used. If it "
            "does not exist, an attempt will be made to create it first.",
        )
        arg_context.argument(
            "path",
            options_list=["--path", "-p"],
            help="The path to a directory containing a custom configuration "
            "profile to use. Run `az arcdata dc config init` to create "
            "a custom configuration profile.",
        )
        arg_context.argument(
            "profile_name",
            options_list=["--profile-name"],
            help="The name of an existing configuration profile. Run `az "
            "arcdata dc config list` to see available "
            "options. One of the following: {0}.".format(
                _get_release_profiles()
            ),
        ),
        arg_context.argument(
            "storage_class",
            options_list=["--storage-class"],
            help="The storage class to be used for all data and logs "
            "persistent volumes for all data controller pods that "
            "require them.",
        )
        arg_context.argument(
            "infrastructure",
            options_list=["--infrastructure"],
            help="The infrastructure on which the data controller will be "
            "running on. Allowed values: {}".format(
                get_valid_dc_infrastructures()
            ),
        )
        arg_context.argument(
            "image_tag",
            options_list=["--image-tag"],
            help="Arc data services image tag to use for the data controller.",
        )
        # -- indirect ----------------------------------------------------------
        arg_context.argument(
            "annotations",
            options_list=["--annotations"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Comma-separated list of annotations to apply all data "
            "controller resources.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        arg_context.argument(
            "labels",
            options_list=["--labels"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Comma-separated list of labels to apply to all data "
            "controller resources.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        arg_context.argument(
            "logs_ui_private_key_file",
            options_list=["--logs-ui-private-key-file"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Path to the file containing a PEM formatted certificate "
            "private key to be used for the Logs UI dashboard endpoint.",
            deprecate_info=arg_context.deprecate(hide=True),
        ),
        arg_context.argument(
            "logs_ui_public_key_file",
            options_list=["--logs-ui-public-key-file"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Path to the file containing a PEM formatted certificate "
            "to be used for the Logs UI dashboard endpoint.",
            deprecate_info=arg_context.deprecate(hide=True),
        ),
        arg_context.argument(
            "metrics_ui_private_key_file",
            options_list=["--metrics-ui-private-key-file"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Path to the file containing a PEM formatted certificate "
            "private key to be used for the Metrics UI dashboard endpoint.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        arg_context.argument(
            "metrics_ui_public_key_file",
            options_list=["--metrics-ui-public-key-file"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Path to the file containing a PEM formatted certificate "
            "to be used for the Metrics UI dashboard endpoint.",
            deprecate_info=arg_context.deprecate(hide=True),
        ),
        arg_context.argument(
            "service_annotations",
            options_list=["--service-annotations"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Comma-separated list of annotations to apply to all external "
            "data controller services.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        arg_context.argument(
            "service_labels",
            options_list=["--service-labels"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Comma-separated list of labels to apply to all external "
            "data controller services.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        arg_context.argument(
            "storage_annotations",
            options_list=["--storage-annotations"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Comma-separated list of annotations to apply to all PVCs "
            "created by the data controller.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        arg_context.argument(
            "storage_labels",
            options_list=["--storage-labels"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Comma-separated list of labels to apply to all PVCs created "
            "by the data controller.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help="Create data controller using local Kubernetes APIs.",
            deprecate_info=arg_context.deprecate(hide=True),
        )
        # -- direct ------------------------------------------------------------
        arg_context.argument(
            "auto_upload_logs",
            options_list=["--auto-upload-logs"],
            choices=["true", "false"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="Enable auto upload logs.",
        )
        arg_context.argument(
            "auto_upload_metrics",
            options_list=["--auto-upload-metrics"],
            choices=["true", "false"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="Enable auto upload metrics.",
        )
        arg_context.argument(
            "custom_location",
            options_list=["--custom-location"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the custom location.",
        )
        arg_context.argument(
            "cluster_name",
            options_list=["--cluster-name"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="Name of the Kubernetes cluster.",
        )
        arg_context.argument(
            "least_privilege",
            options_list=["--least-privilege"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            choices=["true", "false"],
            is_preview=True,
            # Suppress until Custom Location RP releases E2E support, ETA March '23
            help=SUPPRESS,
        )

    with ArgumentsContext(self, "arcdata dc update") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Data controller name.",
            completer=get_resource_name_completion_list(
                f"{RESOURCE_PROVIDER_NAMESPACE}/{INSTANCE_TYPE_DATA_CONTROLLER}"
            ),
        )
        arg_context.argument(
            "desired_version",
            options_list=["--desired-version", "-v"],
            help="The desired version tag to which the data controller will "
            "be upgraded, or empty to use the latest valid version.",
        )
        # -- direct ------------------------------------------------------------
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group in which the data controller exists.",
        )
        arg_context.argument(
            "auto_upload_logs",
            options_list=["--auto-upload-logs"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="Enable auto upload logs.",
            choices=["true", "false"],
        )
        arg_context.argument(
            "auto_upload_metrics",
            options_list=["--auto-upload-metrics"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="Enable auto upload metrics.",
            choices=["true", "false"],
        )
        # -- indirect ----------------------------------------------------------
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace with a deployed data controller.",
        )
        arg_context.argument(
            "maintenance_start",
            options_list=["--maintenance-start"],
            is_preview=True,
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Date time of the start of the first default maintenance window.",
        )
        arg_context.argument(
            "maintenance_duration",
            options_list=["--maintenance-duration"],
            is_preview=True,
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Duration of the default maintenance window.",
        )
        arg_context.argument(
            "maintenance_recurrence",
            options_list=["--maintenance-recurrence"],
            is_preview=True,
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Recurring interval for the default maintenance window.",
        )
        arg_context.argument(
            "maintenance_time_zone",
            options_list=["--maintenance-time-zone"],
            is_preview=True,
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Timezone used to calculate the default maintenance window.",
        )
        arg_context.argument(
            "maintenance_enabled",
            options_list=["--maintenance-enabled"],
            is_preview=True,
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Set the enabled flag on the default maintenance window.",
            choices=["true", "false"],
        )

    with ArgumentsContext(self, "arcdata dc delete") as arg_context:
        arg_context.argument(
            "name", options_list=["--name", "-n"], help="Data controller name."
        )
        arg_context.argument(
            "yes",
            options_list=["--yes", "-y"],
            action="store_true",
            help="Delete data controller without confirmation prompt.",
        )
        arg_context.argument(
            "force",
            options_list=["--force", "-f"],
            action="store_true",
            help="Force delete data controller and all of its data services.",
        )
        # -- indirect --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace in which the data controller exists.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group in which the data controller exists.",
        )

    with ArgumentsContext(self, "arcdata dc list") as c:
        # -- direct --
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group containing the Arc data controller(s).",
        )

    with ArgumentsContext(self, "arcdata dc status show") as arg_context:
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name for the data controller.",
        )
        # -- indirect --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace in which the data controller exists.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group in which the data controller exists.",
        )

    with ArgumentsContext(self, "arcdata dc endpoint list") as arg_context:
        arg_context.argument(
            "endpoint_name",
            options_list=["--endpoint-name", "-e"],
            help="Arc data controller endpoint name.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace in which the data controller "
            "exists.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(self, "arcdata dc config list") as arg_context:
        arg_context.argument(
            "config_profile",
            options_list=["--config-profile", "-c"],
            help="Default config profile: {0}".format(
                list(DeploymentConfigUtil.get_config_map(CONFIG_DIR).keys())
            ),
        )

        arg_context.argument(
            "config_type",
            options_list=["--type", "-t"],
            choices="control",
            help="What config type you would like to see.",
        )

    with ArgumentsContext(self, "arcdata dc config show") as arg_context:
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace in which the data controller "
            "exists.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(self, "arcdata dc config init") as arg_context:
        arg_context.argument(
            "source",
            options_list=["--source", "-s"],
            help="Config profile source: {0}".format(
                list(DeploymentConfigUtil.get_config_map(CONFIG_DIR).keys())
            ),
        )
        arg_context.argument(
            "path",
            options_list=[
                "--path",
                "-p",
                arg_context.deprecate(target="-t", redirect="-p", hide=False),
                arg_context.deprecate(
                    target="--target", redirect="--path", hide=False
                ),
            ],
            help="File path of where you would like the config profile placed, "
            "defaults to cwd/custom.",
        )
        arg_context.argument(
            "force",
            options_list=["--force", "-f"],
            action="store_true",
            help="Force overwrite of the target file.",
        )

    with ArgumentsContext(self, "arcdata dc config add") as arg_context:
        arg_context.argument(
            "config_file",
            options_list=[
                "--path",
                "-p",
                arg_context.deprecate(target="-c", redirect="-p", hide=False),
                arg_context.deprecate(
                    target="--config-file", redirect="--path", hide=False
                ),
            ],
            help="Data controller config file path of the config you would "
            "like to set, i.e. custom/control.json",
        )

        arg_context.argument(
            "json_values",
            options_list=("--json-values", "-j"),
            help="A key value pair list of json paths to values: key1.subkey1=value1,key2.subkey2=value2. "
            "You may provide inline json values such as: "
            'key=\'{"kind":"cluster","name":"test-cluster"}\' or provide a file path, such as'
            " key=./values.json. The add command does NOT support conditionals.  "
            "If the inline value you are providing is a key "
            'value pair itself with "=" and "," escape those characters.  '
            "See http://jsonpatch.com/ for "
            "examples of how your path should look.  If you would like to access an array, you must do so "
            "by indicating the index, such as key.0=value",
        )

    with ArgumentsContext(self, "arcdata dc config replace") as arg_context:
        arg_context.argument(
            "config_file",
            options_list=[
                "--path",
                "-p",
                arg_context.deprecate(target="-c", redirect="-p", hide=False),
                arg_context.deprecate(
                    target="--config-file", redirect="--path", hide=False
                ),
            ],
            help="Data controller config file path of the config you would "
            "like to set, i.e. custom/control.json",
        )

        arg_context.argument(
            "json_values",
            options_list=("--json-values", "-j"),
            help="A key value pair list of json paths to values: key1.subkey1=value1,key2.subkey2=value2. "
            "You may provide inline json values such as: "
            'key=\'{"kind":"cluster","name":"test-cluster"}\' or provide a file path, such as'
            " key=./values.json. The replace command supports conditionals through the jsonpath library.  To use this, "
            "start your path with a $. This will allow you to do a conditional "
            'such as -j $.key1.key2[?(@.key3=="someValue"].key4=value. '
            "If the inline value you are providing is a key "
            'value pair itself with "=" and "," escape those characters.  '
            "You may see examples below. "
            "For additional help, See: https://jsonpath.com/",
        )

    with ArgumentsContext(self, "arcdata dc config remove") as arg_context:
        arg_context.argument(
            "config_file",
            options_list=[
                "--path",
                "-p",
                arg_context.deprecate(target="-c", redirect="-p", hide=False),
                arg_context.deprecate(
                    target="--config-file", redirect="--path", hide=False
                ),
            ],
            help="Data controller config file path of the config you would "
            "like to set, i.e. custom/control.json",
        )

        arg_context.argument(
            "json_path",
            options_list=["--json-path", "-j"],
            help="A list of json paths based on the jsonpatch library that indicates which values you would like "
            "removed, such as: key1.subkey1,key2.subkey2. The remove command does NOT support conditionals. "
            "See http://jsonpatch.com/ for "
            "examples of how your path should look.  If you would like to access an array, you must do so "
            "by indicating the index, such as key.0=value",
        )

    with ArgumentsContext(self, "arcdata dc config patch") as arg_context:
        arg_context.argument(
            "config_file",
            options_list=[
                "--path",
                arg_context.deprecate(
                    target="-c", redirect="--path", hide=False
                ),
                arg_context.deprecate(
                    target="--config-file", redirect="--path", hide=False
                ),
            ],
            help="Data controller config file path of the config you would "
            "like to set, i.e. custom/control.json",
        )

        arg_context.argument(
            "patch_file",
            options_list=["--patch-file", "-p"],
            help="Path to a patch json file that is based off the jsonpatch library: http://jsonpatch.com/. "
            'You must start your patch json file with a key called "patch", whose value is an array '
            "of patch operations you intend to make. "
            "For the path of a patch operation, you may use dot notation, such as key1.key2 for most operations."
            " If you would like to do a replace operation, and you are replacing a value in an array that "
            "requires a conditional, please use the jsonpath notation by beginning your path with a $. "
            'This will allow you to do a conditional such as $.key1.key2[?(@.key3=="someValue"].key4. '
            "See the examples below. For additional help with conditionals, "
            "See: https://jsonpath.com/.",
        )

    with ArgumentsContext(self, "arcdata dc debug copy-logs") as arg_context:
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="Kubernetes namespace of the data controller.",
        )
        arg_context.argument(
            "target_folder",
            options_list=["--target-folder", "-d"],
            help="Target folder path to copy logs to. Optional, by default "
            "creates the result in the local folder.  Cannot be specified "
            "multiple times. If specified multiple times, last one will "
            "be used",
        )
        arg_context.argument(
            "pod",
            options_list=["--pod"],
            help="Copy the logs for the pods with similar name. Optional, by "
            "default copies logs for all pods. Cannot be specified "
            "multiple times. If specified multiple times, last one will "
            "be used",
        )
        arg_context.argument(
            "container",
            options_list=["--container", "-c"],
            help="Copy the logs for the containers with similar name, "
            "Optional, by default copies logs for all containers. Cannot "
            "be specified multiple times. If specified multiple times, "
            "last one will be used",
        )
        arg_context.argument(
            "resource_kind",
            options_list=["--resource-kind"],
            help="Copy the logs for the resource of a particular kind. "
            "Cannot specified multiple times. If specified multiple times, "
            "last one will be used. If specified, --resource-name should "
            "also be specified to identify the resource.",
        )
        arg_context.argument(
            "resource_name",
            options_list=["--resource-name"],
            help="Copy the logs for the resource of the specified name. "
            "Cannot be specified multiple times. If specified multiple times, "
            "last one will be used. If specified, --resource-kind should "
            "also be specified to identify the resource.",
        )
        arg_context.argument(
            "timeout",
            options_list=["--timeout", "-t"],
            type=int,
            default=0,
            help="The number of seconds to wait for the command to complete. "
            "The default value is 0 which is unlimited",
        )
        arg_context.argument(
            "skip_compress",
            options_list=["--skip-compress"],
            action="store_true",
            default=False,
            help="Whether or not to skip compressing the result folder. "
            "The default value is False which compresses the result folder.",
        )
        arg_context.argument(
            "exclude_dumps",
            options_list=["--exclude-dumps"],
            action="store_true",
            default=False,
            help="Whether or not to exclude dumps from result folder. "
            "The default value is False which includes dumps.",
        )
        arg_context.argument(
            "exclude_controldb",
            options_list=["--exclude-controldb"],
            action="store_true",
            default=False,
            help="Whether or not to exclude a backup of controldb from result folder. "
            "The default value is False which includes a controldb backup.",
        )
        arg_context.argument(
            "exclude_cluster_info",
            options_list=["--exclude-cluster-info"],
            action="store_true",
            default=False,
            help="Whether or not to exclude kubernetes resource info from result folder per namespace. "
            "The default value is False which includes namespaced resource info.",
        )
        arg_context.argument(
            "exclude_arcdata_logs",
            options_list=["--exclude-arcdata-logs"],
            action="store_true",
            default=False,
            help="Whether or not to exclude arc data services logs from result folder. "
            "The default value is False which includes all arc data services container logs.",
        )
        arg_context.argument(
            "exclude_system_logs",
            options_list=["--exclude-system-logs"],
            action="store_true",
            default=False,
            help="Whether or not to exclude kube-system and azure-arc namespace logs from collection. "
            "The default value is False which includes kube-system and connectedk8s logs, if accessible.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            # deprecate_info=arg_context.deprecate(hide=True),
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(self, "arcdata dc debug dump") as arg_context:
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="Kubernetes namespace of the data controller.",
        )

        arg_context.argument(
            "container",
            options_list=["--container", "-c"],
            choices=["controller"],
            default="controller",
            help="The target container to be triggered for dumping the running "
            "processes.",
        )

        arg_context.argument(
            "target_folder",
            options_list=["--target-folder", "-d"],
            default="./output/dump",
            help="Target folder to copy the dump out.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            # deprecate_info=arg_context.deprecate(hide=True),
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(
        self, "arcdata dc debug restore-controldb-snapshot"
    ) as arg_context:
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="Kubernetes namespace of the existing data controller.",
        )
        arg_context.argument(
            "backup_file",
            options_list=["--backup-file", "-f"],
            help="Existing Controller Database backup file - must end in '.bak', "
            "will be restored under a unique database name based on execution "
            "timestamp.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            # deprecate_info=arg_context.deprecate(hide=True),
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(
        self, "arcdata dc debug controldb-cdc"
    ) as arg_context:
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="Kubernetes namespace of the existing data controller.",
        )
        arg_context.argument(
            "enable",
            options_list=["--enable"],
            choices=["true", "false"],
            help="Enable or disable change data capture.",
        )
        arg_context.argument(
            "retention_hours",
            options_list=["--retention-hours"],
            type=int,
            default=8,
            help="CDC retention period, specified in hours. "
            "Allowed values are 1 to 24.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            # deprecate_info=arg_context.deprecate(hide=True),
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(self, "arcdata dc export") as arg_context:
        arg_context.argument(
            "export_type",
            options_list=["--type", "-t"],
            help="The type of data to be exported. Options: logs, metrics, "
            "and usage.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace in which the data controller exists.",
        )
        arg_context.argument(
            "path",
            options_list=["--path", "-p"],
            help="The full or relative path including the file name of the "
            "file to be exported.",
        )
        arg_context.argument(
            "force",
            options_list=["--force", "-f"],
            action="store_true",
            help="Force create output file. Overwrites any existing file at "
            "the same path.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            # deprecate_info=arg_context.deprecate(hide=True),
            action="store_true",
            help=USE_K8S_TEXT,
        )

    with ArgumentsContext(self, "arcdata dc upload") as arg_context:
        arg_context.argument(
            "path",
            options_list=["--path", "-p"],
            help="The full or relative path including the file name of the "
            "file to be uploaded.",
        )

    with ArgumentsContext(self, "arcdata resource-kind get") as arg_context:
        arg_context.argument(
            "kind",
            options_list=["--kind", "-k"],
            help="The kind of arc resource you want the template file for.",
        )
        arg_context.argument(
            "dest",
            options_list=["--dest", "-d"],
            help='The directory where you"d like to place the template files.',
        )

    with ArgumentsContext(self, "arc resource list") as arg_context:
        arg_context.argument(
            "kind",
            options_list=["--kind", "-k"],
            help="The kind of the Arc custom resource you would like to list.",
        )

    with ArgumentsContext(self, "arcdata dc upgrade") as arg_context:
        arg_context.argument(
            "desired_version",
            options_list=[
                "--desired-version",
                "-v",
                arg_context.deprecate(
                    target="--target", redirect="--desired-version", hide=False
                ),
            ],
            help="The desired version tag to which the data controller will "
            "be upgraded, or empty to use the latest valid version.",
        )
        arg_context.argument(
            "dry_run",
            options_list=["--dry-run", "-d"],
            action="store_true",
            help="Indicates which instance would be upgraded but does not "
            "actually upgrade the instances.",
        )
        arg_context.argument(
            "no_wait",
            options_list=["--no-wait"],
            action="store_true",
            help="If given, the command will start the upgrade, but will not "
            "wait for the entire upgrade to complete. Upgrade will "
            "continue in the background.",
        )
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the data controller.",
        )
        # -- native --
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The Kubernetes namespace in which the data controller "
            "exists.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Upgrade data controller using local Kubernetes APIs.",
        )
        # -- direct --
        arg_context.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group in which the data controller exists.",
        )

    with ArgumentsContext(self, "arcdata dc list-upgrades") as arg_context:
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace in which the data controller exists.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            action="store_true",
            help="List available data controller versions using local Kubernetes APIs.",
        )


def _get_release_profiles():
    return list(
        filter(
            lambda x: "dev-test" not in x,
            DeploymentConfigUtil.get_config_map(CONFIG_DIR).keys(),
        )
    )
