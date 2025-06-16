# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.vm import RestrictMovement
from azure.cli.core.aaz import register_command


@register_command(
    "vmware vm restrict-movement",
)
class VmRestrictMovement(RestrictMovement):
    """ Enable or disable DRS-driven VM movement restriction.

    :example: Enable or disable DRS-driven VM movement restriction.
        az vmware vm restrict-movement --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --virtual-machine vm-209 --restrict-movement Enabled
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        setattr(args_schema.no_wait, '_registered', False)

        return args_schema
