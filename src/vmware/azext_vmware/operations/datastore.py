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

        setattr(args_schema.net_app_volume, '_required', True)
        setattr(args_schema.lun_name, '_registered', False)
        setattr(args_schema.mount_option, '_registered', False)
        setattr(args_schema.target_id, '_registered', False)
        setattr(args_schema.elastic_san_volume, '_registered', False)
        setattr(args_schema.size_gb, '_registered', False)
        setattr(args_schema.storage_pool_id, '_registered', False)
        setattr(args_schema.no_wait, '_registered', False)

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

        setattr(args_schema.net_app_volume, '_registered', False)
        setattr(args_schema.lun_name, '_required', True)
        setattr(args_schema.target_id, '_required', True)
        setattr(args_schema.elastic_san_volume, '_registered', False)
        setattr(args_schema.size_gb, '_registered', False)
        setattr(args_schema.storage_pool_id, '_registered', False)
        setattr(args_schema.no_wait, '_registered', False)

        return args_schema


@register_command(
    "vmware datastore elastic-san-volume create",
)
class DatastoreElasticVsanVolumeCreate(_DatastoreCreate):
    """Create an Elastic SAN volume in a private cloud cluster using Microsoft.ElasticSan provider.
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        setattr(args_schema.net_app_volume, '_registered', False)
        setattr(args_schema.lun_name, '_registered', False)
        setattr(args_schema.mount_option, '_registered', False)
        setattr(args_schema.target_id, '_registered', False)
        setattr(args_schema.elastic_san_volume, '_required', True)
        setattr(args_schema.size_gb, '_registered', False)
        setattr(args_schema.storage_pool_id, '_registered', False)
        setattr(args_schema.no_wait, '_registered', False)

        return args_schema


@register_command(
    "vmware datastore pure-storage-volume create",
)
class DatastorePureStorageVolumeCreate(_DatastoreCreate):
    """Create a Pure Storage volume in a private cloud cluster using PureStorage.Block provider.

    :example: Create a Pure Storage volume in a private cloud.
        az vmware datastore pure-storage-volume create --name PureStorageDatastore1 --resource-group ResourceGroup1 --private-cloud PrivateCloud1 --cluster Cluster1 --storage-pool-id StoragePool1 --size-gb 64
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        setattr(args_schema.net_app_volume, '_registered', False)
        setattr(args_schema.lun_name, '_registered', False)
        setattr(args_schema.mount_option, '_registered', False)
        setattr(args_schema.target_id, '_registered', False)
        setattr(args_schema.elastic_san_volume, '_registered', False)
        setattr(args_schema.size_gb, '_required', True)
        setattr(args_schema.storage_pool_id, '_required', True)
        setattr(args_schema.no_wait, '_registered', False)

        return args_schema
