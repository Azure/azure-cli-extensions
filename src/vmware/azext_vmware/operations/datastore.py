# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.datastore import Create as _DatastoreCreate
from azure.cli.core.aaz import register_command


@register_command(
    "vmware datastore netapp-volume create",
)
class DatastoreNetappVolumeCreate(_DatastoreCreate):
    """Create a new Microsoft.NetApp provided NetApp volume in a private cloud cluster.
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.net_app_volumn._required = True

        args_schema.lun_name._registered = False
        args_schema.mount_option._registered = False
        args_schema.target_id._registered = False
        return args_schema


@register_command(
    "vmware datastore disk-pool-volume create",
)
class DatastoreDiskPoolVolumeCreate(_DatastoreCreate):
    """Create a VMFS datastore in a private cloud cluster using Microsoft.StoragePool provided iSCSI target.
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.net_app_volumn._registered = False

        args_schema.lun_name._required = True
        args_schema.target_id._required = True
        return args_schema
