# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_enum_type
from .consts import IncludedExtensionTypes
from .action import AddIncludedExtensionTypes


def load_arguments(self, _):

    with self.argument_context('vme upgrade') as c:
        c.argument(
            'resource_group',
            options_list=['--resource-group', '-g'],
            help='Name of the resource group'
        )
        c.argument(
            'cluster_name',
            options_list=['--cluster-name', '-c'],
            help='Name of the Kubernetes cluster'
        )
        c.argument(
            "kube_config",
            options_list=["--kube-config"],
            help="Path to the kube config file. Optional if the cluster has the feature flag enabled or the current Kubernetes config/context is set to this cluster.",
        )
        c.argument(
            "kube_context",
            options_list=["--kube-context"],
            help="Kube context from current machine. Optional if the cluster has the feature flag enabled or the current Kubernetes config/context is set to this cluster.",
        )
        c.argument(
            "wait",
            options_list=["--wait"],
            help="Wait for the bundle upgrade to finish.",
        )
        c.argument(
            "timeout",
            options_list=["--timeout"],
            help="Time required (in seconds) for the bundle upgrade to finish.",
        )

    with self.argument_context('vme install') as c:
        c.argument(
            'resource_group',
            options_list=['--resource-group', '-g'],
            help='Name of the resource group'
        )
        c.argument(
            'cluster_name',
            options_list=['--cluster-name', '-c'],
            help='Name of the Kubernetes cluster'
        )
        c.argument(
            'include_extension_types',
            options_list=['--include', '-i'],
            action=AddIncludedExtensionTypes,
            nargs="+",
            help='Extension types to be installed.',
            arg_type=get_enum_type(IncludedExtensionTypes),
        )
        c.argument(
            "kube_config",
            options_list=["--kube-config"],
            help="Path to the kube config file. Optional if the cluster has the feature flag enabled or the current Kubernetes config/context is set to this cluster.",
        )
        c.argument(
            "kube_context",
            options_list=["--kube-context"],
            help="Kube context from current machine. Optional if the cluster has the feature flag enabled or the current Kubernetes config/context is set to this cluster.",
        )

    with self.argument_context('vme uninstall') as c:
        c.argument(
            'resource_group',
            options_list=['--resource-group', '-g'],
            help='Name of the resource group'
        )
        c.argument(
            'cluster_name',
            options_list=['--cluster-name', '-c'],
            help='Name of the Kubernetes cluster'
        )
        c.argument(
            'include_extension_types',
            options_list=['--include', '-i'],
            action=AddIncludedExtensionTypes,
            nargs="+",
            help='Extension types to be uninstalled.',
            arg_type=get_enum_type(IncludedExtensionTypes),
        )
        c.argument(
            'force',
            help='Specify whether to force delete the extension from the cluster.',
        )

    with self.argument_context('vme list') as c:
        c.argument(
            'resource_group',
            options_list=['--resource-group', '-g'],
            help='Name of the resource group'
        )
        c.argument(
            'cluster_name',
            options_list=['--cluster-name', '-c'],
            help='Name of the Kubernetes cluster'
        )
