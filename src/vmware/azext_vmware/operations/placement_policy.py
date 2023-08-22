# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.placement_policy import Create as _Create, Update as _Update, Delete as _Delete
from azure.cli.core.aaz import register_command


# vm


@register_command(
    "vmware placement-policy vm create",
)
class PlacementPolicyVMCreate(_Create):
    """Create a VM placement policy in a private cloud cluster.

    :example: Create a VM placement policy.
        az vmware placement-policy vm create --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --display-name policy1 --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256 --affinity-type AntiAffinity
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.affinity_type = AAZStrArg(
            options=["--affinity-type"],
            help="placement policy affinity type",
            required=True,
            enum={"Affinity": "Affinity", "AntiAffinity": "AntiAffinity"},
        )
        args_schema.vm_members = AAZListArg(
            options=["--vm-members"],
            help="Virtual machine members list",
            required=True,
        )
        vm_members = args_schema.vm_members
        vm_members.Element = AAZStrArg()

        args_schema.vm_host._registered = False
        args_schema.vm_vm._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.vm_vm.affinity_type = args.affinity_type
        args.vm_vm.vm_members = args.vm_members


@register_command(
    "vmware placement-policy vm update",
)
class PlacementPolicyVMUpdate(_Update):
    """Update a VM placement policy in a private cloud cluster.

    :example: Update a VM placement policy.
        az vmware placement-policy vm update --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --display-name policy1 --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.vm_members = AAZListArg(
            options=["--vm-members"],
            help="Virtual machine members list",
        )
        vm_members = args_schema.vm_members
        vm_members.Element = AAZStrArg(
            nullable=True,
        )

        args_schema.vm_host._registered = False
        args_schema.vm_vm._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.vm_vm.vm_members = args.vm_members


@register_command(
    "vmware placement-policy vm delete",
    confirmation="This will delete the placement policy. Are you sure?"
)
class PlacementPolicyVMDelete(_Delete):
    """Delete a VM placement policy in a private cloud cluster.

    :example: Delete a VM placement policy.
        az vmware placement-policy vm delete --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1
    """


# vm-host


@register_command(
    "vmware placement-policy vm-host create",
)
class PlacementPolicyVMHostCreate(_Create):
    """Create a VM Host placement policy in a private cloud cluster.

    :example: Create a VM placement policy.
        az vmware placement-policy vm-host create --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --display-name policy1 --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256 --host-members fakehost22.nyc1.kubernetes.center fakehost23.nyc1.kubernetes.center --affinity-type AntiAffinity
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.affinity_strength = AAZStrArg(
            options=["--affinity-strength"],
            help="vm-host placement policy affinity strength (should/must)",
            enum={"Must": "Must", "Should": "Should"},
        )
        args_schema.affinity_type = AAZStrArg(
            options=["--affinity-type"],
            help="placement policy affinity type",
            required=True,
            enum={"Affinity": "Affinity", "AntiAffinity": "AntiAffinity"},
        )
        args_schema.azure_hybrid_benefit = AAZStrArg(
            options=["--azure-hybrid-benefit"],
            help="placement policy azure hybrid benefit opt-in type",
            enum={"None": "None", "SqlHost": "SqlHost"},
        )
        args_schema.host_members = AAZListArg(
            options=["--host-members"],
            help="Host members list",
            required=True,
        )
        args_schema.vm_members = AAZListArg(
            options=["--vm-members"],
            help="Virtual machine members list",
            required=True,
        )

        host_members = args_schema.host_members
        host_members.Element = AAZStrArg()

        vm_members = args_schema.vm_members
        vm_members.Element = AAZStrArg()

        args_schema.vm_host._registered = False
        args_schema.vm_vm._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.vm_host.affinity_strength = args.affinity_strength
        args.vm_host.affinity_type = args.affinity_type
        args.vm_host.azure_hybrid_benefit = args.azure_hybrid_benefit
        args.vm_host.host_members = args.host_members
        args.vm_host.vm_members = args.vm_members


@register_command(
    "vmware placement-policy vm-host update",
)
class PlacementPolicyVMHostUpdate(_Update):
    """Update a VM Host placement policy in a private cloud cluster.

    :example: Update a VM Host placement policy.
        az vmware placement-policy vm-host update --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --display-name policy1 --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256 --host-members fakehost22.nyc1.kubernetes.center fakehost23.nyc1.kubernetes.center
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.affinity_strength = AAZStrArg(
            options=["--affinity-strength"],
            help="vm-host placement policy affinity strength (should/must)",
            nullable=True,
            enum={"Must": "Must", "Should": "Should"},
        )
        args_schema.azure_hybrid_benefit = AAZStrArg(
            options=["--azure-hybrid-benefit"],
            help="placement policy azure hybrid benefit opt-in type",
            nullable=True,
            enum={"None": "None", "SqlHost": "SqlHost"},
        )
        args_schema.host_members = AAZListArg(
            options=["--host-members"],
            help="Host members list",
        )
        args_schema.vm_members = AAZListArg(
            options=["--vm-members"],
            help="Virtual machine members list",
        )

        host_members = args_schema.host_members
        host_members.Element = AAZStrArg(
            nullable=True,
        )

        vm_members = args_schema.vm_members
        vm_members.Element = AAZStrArg(
            nullable=True,
        )

        args_schema.vm_host._registered = False
        args_schema.vm_vm._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.vm_host.affinity_strength = args.affinity_strength
        args.vm_host.azure_hybrid_benefit = args.azure_hybrid_benefit
        args.vm_host.host_members = args.host_members
        args.vm_host.vm_members = args.vm_members


@register_command(
    "vmware placement-policy vm-host delete",
    confirmation="This will delete the placement policy. Are you sure?"
)
class PlacementPolicyVMHostDelete(_Delete):
    """Delete a VM Host placement policy in a private cloud cluster.

    :example: Delete a VM Host placement policy.
        az vmware placement-policy vm-host delete --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1
    """
