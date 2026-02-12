# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.constants import USE_K8S_TEXT


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext

    with ArgumentsContext(self, "sql midb-arc restore") as arg_context:
        arg_context.argument(
            "managed_instance",
            options_list=["--managed-instance"],
            help="Name of the source Azure Arc enabled SQL managed instance.",
        )
        arg_context.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the source database from where the backups"
            " should be retrieved.",
        )
        arg_context.argument(
            "dest_name",
            options_list=["--dest-name"],
            help="Name of the database that will be created as the restore "
            "destination.",
        )
        arg_context.argument(
            "time",
            options_list=["--time", "-t"],
            help="The point in time of the source database that will be "
            "restored to create the new database. Must be greater than or equal"
            " to the source database's earliest restore date/time value. "
            "Time should be in following format: 'YYYY-MM-DDTHH:MM:SSZ'. "
            "If no time is provided, the most recent backup will be restored.",
        )
        arg_context.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            help="The Kubernetes namespace that contains the Azure Arc enabled "
            "SQL managed instance. If no namespace is specified, then the "
            "namespace defined in the kubeconfig will be used.",
        )
        arg_context.argument(
            "use_k8s",
            options_list=("--use-k8s"),
            action="store_true",
            help=USE_K8S_TEXT,
        )
        arg_context.argument(
            "nowait",
            options_list=["--no-wait"],
            action="store_true",
            help="Do not wait for the long-running operation to finish.",
        )
        arg_context.argument(
            "dry_run",
            options_list=["--dry-run"],
            action="store_true",
            help="Validates if the restore operation can be successful or "
            "not by returning earliest and latest restore time window.",
        )
