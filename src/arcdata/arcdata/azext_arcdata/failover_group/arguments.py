# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.constants import (
    USE_K8S_TEXT,
    CLI_ARG_GROUP_DIRECT_TEXT,
    CLI_ARG_GROUP_INDIRECT_TEXT,
)
from azext_arcdata.failover_group.constants import (
    DAG_PARTNER_SYNC_MODE,
    DAG_ROLES_CREATE,
    DAG_ROLES_UPDATE,
)


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext

    with ArgumentsContext(self, "sql instance-failover-group-arc create") as c:
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the failover group resource.",
        )
        c.argument(
            "partner_sync_mode",
            options_list=["--partner-sync-mode", "-m"],
            help="The partner synchronization mode of the Arc-enabled SQL managed instance.",
            choices=DAG_PARTNER_SYNC_MODE,
        )
        c.argument(
            "mi",
            options_list=["--mi"],
            help="The name of the primary SQL managed instance.",
        )
        c.argument(
            "partner_mi",
            options_list=["--partner-mi"],
            help="The name of the partner SQL managed instance or remote SQL instance. "
            "When using ARM-targeted arguments, this refers to the Disaster Recovery (DR) "
            "instance name.",
        )
        c.argument(
            "role",
            options_list=["--role"],
            choices=DAG_ROLES_CREATE,
            help="The requested role of the failover group. The role can be changed.",
        )
        c.argument(
            "partner_mirroring_url",
            options_list=["--partner-mirroring-url", "-u"],
            help="The mirroring endpoint URL of the partner SQL managed instance.",
        )
        # -- indirect --
        c.argument(
            "shared_name",
            options_list=["--shared-name"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The shared name of the failover group for this SQL "
            "managed instance. Both the primary SQL managed instance "
            "and its partner must use the same shared name.",
        )
        c.argument(
            "partner_mirroring_cert_file",
            options_list=["--partner-mirroring-cert-file", "-f"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="The filename of mirroring endpoint public certificate for "
            "the partner SQL managed instance or availability group on remote SQL "
            "instance. Only PEM format is supported.",
        )
        c.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Namespace where the failover group is to be deployed. "
            "If no namespace is specified, then the namespace defined "
            "in the kubeconfig will be used.",
        )
        c.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help="Create the Arc-enabled SQL managed instance failover group using local Kubernetes APIs.",
        )
        # -- direct --
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the primary Arc-enabled SQL managed instance.",
        )
        c.argument(
            "partner_resource_group",
            options_list=["--partner-resource-group"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the DR partner Arc-enabled SQL managed instance.",
        )
        c.argument(
            "primary_mirroring_url",
            options_list=["--primary-mirroring-url"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The mirroring endpoint URL of the primary SQL managed instance.",
        )

    with ArgumentsContext(self, "sql instance-failover-group-arc update") as c:
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the failover group resource.",
        )
        c.argument(
            "partner_sync_mode",
            options_list=["--partner-sync-mode", "-m"],
            choices=DAG_PARTNER_SYNC_MODE,
            help="The partner synchronization mode of the SQL managed instance.",
        )
        c.argument(
            "role",
            options_list=["--role"],
            choices=DAG_ROLES_UPDATE,
            help="The requested role of the failover group.",
        )
        # -- indirect --
        c.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Namespace where the failover group exists. "
            "If no namespace is specified, then the namespace defined "
            "in the kubeconfig will be used.",
        )
        c.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        c.argument(
            "mi",
            options_list=["--mi"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the Arc-enabled SQL managed instance to update.",
        )
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the primary Arc-enabled SQL managed instance.",
        )

    with ArgumentsContext(self, "sql instance-failover-group-arc delete") as c:
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the failover group resource to delete.",
        )
        # -- indirect --
        c.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Namespace where the failover group is deployed. "
            "If no namespace is specified, then the namespace defined "
            "in the kubeconfig will be used.",
        )
        c.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        c.argument(
            "mi",
            options_list=["--mi"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the primary Arc-enabled SQL managed instance.",
        )
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the primary Arc-enabled SQL managed instance.",
        )

    with ArgumentsContext(self, "sql instance-failover-group-arc show") as c:
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="The name of the failover group resource.",
        )
        # -- indirect --
        c.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Namespace where the failover group is deployed. "
            "If no namespace is specified, then the namespace defined "
            "in the kubeconfig will be used.",
        )
        c.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        c.argument(
            "mi",
            options_list=["--mi"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the primary Arc-enabled SQL managed instance.",
        )
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the primary Arc-enabled SQL managed instance.",
        )

    with ArgumentsContext(self, "sql instance-failover-group-arc list") as c:
        # -- indirect --
        c.argument(
            "namespace",
            options_list=["--k8s-namespace", "-k"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            help="Namespace where the failover groups are deployed. "
            "If no namespace is specified, then the namespace defined "
            "in the kubeconfig will be used.",
        )
        c.argument(
            "use_k8s",
            options_list=["--use-k8s"],
            arg_group=CLI_ARG_GROUP_INDIRECT_TEXT,
            action="store_true",
            help=USE_K8S_TEXT,
        )
        # -- direct --
        c.argument(
            "mi",
            options_list=["--mi"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The name of the Arc-enabled SQL managed instance.",
        )
        c.argument(
            "resource_group",
            options_list=["--resource-group", "-g"],
            arg_group=CLI_ARG_GROUP_DIRECT_TEXT,
            help="The Azure resource group of the Arc-enabled SQL managed instance.",
        )
