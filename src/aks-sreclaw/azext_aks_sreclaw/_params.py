# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-statements,too-many-lines
def load_arguments(self, _):
    with self.argument_context("aks claw create") as c:
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )
        c.argument(
            "namespace",
            options_list=["--namespace"],
            help="The Kubernetes namespace where the sreclaw will be deployed.",
            required=True,
        )

    with self.argument_context("aks claw connect") as c:
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )
        c.argument(
            "namespace",
            options_list=["--namespace"],
            help="The Kubernetes namespace where the openclaw service is deployed.",
            required=True,
        )
        c.argument(
            "local_port",
            options_list=["--local-port"],
            type=int,
            help="Local port to use for port-forwarding. Defaults to 18789.",
            required=False,
        )

    with self.argument_context("aks claw delete") as c:
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )
        c.argument(
            "namespace",
            options_list=["--namespace"],
            help="The Kubernetes namespace where the openclaw service is deployed.",
            required=True,
        )
        c.argument(
            "yes",
            options_list=["--yes", "-y"],
            action="store_true",
            help="Do not prompt for confirmation.",
        )

    with self.argument_context("aks claw status") as c:
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )
        c.argument(
            "namespace",
            options_list=["--namespace"],
            help="The Kubernetes namespace where the openclaw service is deployed.",
            required=True,
        )
