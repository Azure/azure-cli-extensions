# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.addon import Show as _AddonShow, Create as _AddonCreate, Update as _AddonUpdate, \
    Delete as _AddonDelete
from azure.cli.core.aaz import register_command

# vr


@register_command(
    "vmware addon vr show",
)
class AddonVrShow(_AddonShow):
    """Show details of a vSphere Replication (VR) addon for a private cloud.

    :example: Show details of a vSphere Replication (VR) addon.
        az vmware addon vr show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "vr"


@register_command(
    "vmware addon vr create",
)
class AddonVrCreate(_AddonCreate):
    """Create a vSphere Replication (VR) addon for a private cloud.

    :example: Create a vSphere Replication (VR) addon.
        az vmware addon vr create --resource-group MyResourceGroup --private-cloud MyPrivateCloud --vrs-count 1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZIntArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.vrs_count = AAZIntArg(
            options=["--vrs-count"],
            help="The vSphere Replication Server (VRS) count",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "vr"
        args.vr.vrs_count = args.vrs_count


@register_command(
    "vmware addon vr update",
)
class AddonVrUpdate(_AddonUpdate):
    """Update a vSphere Replication (VR) addon for a private cloud.

    :example: Update a vSphere Replication (VR) addon.
        az vmware addon vr update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --vrs-count 1
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZIntArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.vrs_count = AAZIntArg(
            options=["--vrs-count"],
            help="The vSphere Replication Server (VRS) count",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "vr"
        args.vr.vrs_count = args.vrs_count


@register_command(
    "vmware addon vr delete",
    confirmation="This will delete the VR addon. Are you sure?"
)
class AddonVrDelete(_AddonDelete):
    """Delete a vSphere Replication (VR) addon for a private cloud.

    :example: Delete a vSphere Replication (VR) addon.
        az vmware addon vr delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "vr"

# hcx


@register_command(
    "vmware addon hcx show",
)
class AddonHcxShow(_AddonShow):
    """Show details of a HCX addon for a private cloud.

    :example: Show details of a HCX addon.
        az vmware addon hcx show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "hcx"


@register_command(
    "vmware addon hcx create",
)
class AddonHcxCreate(_AddonCreate):
    """ Create a HCX addon for a private cloud.

    :example: Create a HCX addon.
        az vmware addon hcx create --resource-group MyResourceGroup --private-cloud MyPrivateCloud --offer "VMware MaaS Cloud Provider (Enterprise)"
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.offer = AAZStrArg(
            options=["--offer"],
            help="The HCX offer, example VMware MaaS Cloud Provider (Enterprise)",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "hcx"

        args.hcx.offer = args.offer


@register_command(
    "vmware addon hcx update",
)
class AddonHcxUpdate(_AddonUpdate):
    """Update a HCX addon for a private cloud.

    :example: Update a HCX addon.
        az vmware addon hcx update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --offer "VMware MaaS Cloud Provider (Enterprise)"
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.offer = AAZStrArg(
            options=["--offer"],
            help="The HCX offer, example VMware MaaS Cloud Provider (Enterprise)",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "hcx"

        args.hcx.offer = args.offer


@register_command(
    "vmware addon hcx delete",
    confirmation="This will delete the HCX addon. Are you sure?"
)
class AddonHcxDelete(_AddonDelete):
    """Delete a HCX addon for a private cloud.

    :example: Delete a HCX addon.
        az vmware addon hcx delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "hcx"


# srm


@register_command(
    "vmware addon srm show",
)
class AddonSrmShow(_AddonShow):
    """Show details of a Site Recovery Manager (SRM) addon.

    :example: Show details of a Site Recovery Manager (SRM) addon.
        az vmware addon srm show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "srm"


@register_command(
    "vmware addon srm create",
)
class AddonSrmCreate(_AddonCreate):
    """Create a Site Recovery Manager (SRM) addon for a private cloud.

    :example:  Create a Site Recovery Manager (SRM) addon.
        az vmware addon srm create --resource-group MyResourceGroup --private-cloud MyPrivateCloud --license-key "41915-178A8-FF4A4-DB683-6D735"
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.license_key = AAZStrArg(
            options=["--license-key"],
            help="The Site Recovery Manager (SRM) license",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "srm"
        args.srm.license_key = args.license_key


@register_command(
    "vmware addon srm update",
)
class AddonSrmUpdate(_AddonUpdate):
    """Update a Site Recovery Manager (SRM) addon for a private cloud.

    :example: Update a Site Recovery Manager (SRM) addon.
        az vmware addon srm update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --license-key "41915-178A8-FF4A4-DB683-6D735"
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.license_key = AAZStrArg(
            options=["--license-key"],
            help="The Site Recovery Manager (SRM) license",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "srm"
        args.srm.license_key = args.license_key


@register_command(
    "vmware addon srm delete",
    confirmation="This will delete the SRM addon. Are you sure?"
)
class AddonSrmDelete(_AddonDelete):
    """Delete a Site Recovery Manager (SRM) addon for a private cloud.

    :example: Delete a Site Recovery Manager (SRM) addon.
        az vmware addon srm delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "srm"


# arc


@register_command(
    "vmware addon arc show",
)
class AddonArcShow(_AddonShow):
    """Show details of an Arc addon for a private cloud.

    :example: Show details of an Arc addon.
        az vmware addon arc show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "arc"


@register_command(
    "vmware addon arc create",
)
class AddonArcCreate(_AddonCreate):
    """Create an Arc addon for a private cloud.

    :example: Create an Arc addon.
        az vmware addon vr show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.vcenter = AAZStrArg(
            options=["--vcenter"],
            help="The VMware vCenter resource ID",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "arc"
        args.arc.vcenter = args.vcenter


@register_command(
    "vmware addon arc update",
)
class AddonArcUpdate(_AddonUpdate):
    """Update an Arc addon for a private cloud.

    :example: Update an Arc addon.
        az vmware addon arc update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --vcenter "00000000-0000-0000-0000-000000000000"
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.vcenter = AAZStrArg(
            options=["--vcenter"],
            help="The VMware vCenter resource ID",
            required=True,
        )

        args_schema.vr._registered = False
        args_schema.hcx._registered = False
        args_schema.srm._registered = False
        args_schema.arc._registered = False

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "arc"
        args.arc.vcenter = args.vcenter


@register_command(
    "vmware addon arc delete",
    confirmation="This will delete the Arc addon. Are you sure?"
)
class AddonArcDelete(_AddonDelete):
    """Delete an Arc addon for a private cloud.

    :example: Delete an Arc addon.
        az vmware addon arc delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.addon_name._required = False
        args_schema.addon_name._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.addon_name = "arc"
