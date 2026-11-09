# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime, timezone

from azure.cli.core.aaz import (
    AAZDateTimeArg,
    AAZResourceIdArg,
    AAZResourceIdArgFormat,
    AAZResourceLocationArgFormat,
    AAZUndefined,
)
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from azure.mgmt.core.tools import parse_resource_id

from ._show import Show as _ClusterShow
from .custom import ClusterCreate


class ClusterRestore(ClusterCreate):
    AZ_HELP = {
        'type': 'command',
        'short-summary': 'Restore a HorizonDB cluster to a point in time.',
        'long-summary': 'Inherits unspecified cluster settings from the source cluster, waits for '
                        'provisioning, and retrieves the restored cluster.',
        'examples': [{
            'name': 'Restore a HorizonDB cluster to a specified UTC time',
            'text': 'az horizondb cluster restore --resource-group example-resource-group '
                    '--cluster-name restored-cluster --source-cluster-id '
                    '/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/'
                    'source-resource-group/providers/Microsoft.HorizonDb/clusters/source-cluster '
                    '--point-in-time-utc 2026-07-27T12:00:00Z',
        }],
    }

    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.creation_source_cluster_resource_id = AAZResourceIdArg(
            options=['--source-cluster-id', '--creation-source-cluster-resource-id'],
            help='Resource ID of the source HorizonDB cluster.',
            required=True,
            fmt=AAZResourceIdArgFormat(
                template='/subscriptions/{}/resourceGroups/{}/providers/Microsoft.HorizonDb/clusters/{}',
            ),
        )
        args_schema.point_in_time_utc = AAZDateTimeArg(
            options=['--point-in-time-utc'],
            help='UTC restore time, for example 2026-07-27T12:00:00Z. Defaults to the current UTC time.',
        )
        args_schema.geo_redundancy._registered = False  # pylint: disable=protected-access
        args_schema.version._registered = False  # pylint: disable=protected-access
        args_schema.retention_days._registered = False  # pylint: disable=protected-access
        args_schema.location._required = False  # pylint: disable=protected-access
        args_schema.location._fmt = AAZResourceLocationArgFormat()  # pylint: disable=protected-access
        args_schema.location._help['short-summary'] = (  # pylint: disable=protected-access
            'Location of the restored cluster. Can only be specified for a geo-redundant restore '
            'when the source cluster has geo-redundancy enabled. Defaults to the source cluster location.'
        )
        for name in ['retention_days', 'public_access']:
            getattr(args_schema, name)._default = None  # pylint: disable=protected-access
        return args_schema

    def pre_operations(self):
        super().pre_operations()
        args = self.ctx.args
        if args.creation_source_cluster_resource_id.to_serialized_data() in (AAZUndefined, None):
            raise RequiredArgumentMissingError('--source-cluster-id is required.')
        if args.point_in_time_utc.to_serialized_data() in (AAZUndefined, None):
            args.point_in_time_utc = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        source_id = parse_resource_id(args.creation_source_cluster_resource_id.to_serialized_data())
        source = _ClusterShow(cli_ctx=self.cli_ctx)(command_args={
            'subscription': source_id['subscription'],
            'resource_group': source_id['resource_group'],
            'cluster_name': source_id['name'],
        })
        self.ctx.set_var(
            'restore_source', source,
            schema_builder=_ClusterShow.ClustersGet._build_schema_on_200,  # pylint: disable=protected-access
        )
        properties = source.get('properties', {})
        geo_redundancy = properties.get('backup', {}).get('geoRedundancy', AAZUndefined)
        if args.location.to_serialized_data() not in (AAZUndefined, None) and geo_redundancy != 'Enabled':
            raise InvalidArgumentValueError(
                '--location can only be specified for a geo-redundant restore '
                'when the source cluster has geo-redundancy enabled.'
            )
        args.geo_redundancy = geo_redundancy
        args.version = properties.get('postgreSqlVersion', AAZUndefined)
        for name, value in {
            'location': source.get('location', AAZUndefined),
            'tags': source.get('tags', AAZUndefined),
            'public_access': properties.get('network', {}).get('publicAccess', AAZUndefined),
        }.items():
            if getattr(args, name).to_serialized_data() == AAZUndefined and value != AAZUndefined:
                setattr(args, name, value)
        if args.data_encryption.to_serialized_data() == AAZUndefined:
            encryption = properties.get('dataEncryption') or {}
            for name, key in {
                'type': 'type',
                'primary_key_uri': 'primaryKeyUri',
                'primary_user_assigned_identity_id': 'primaryUserAssignedIdentityId',
            }.items():
                if key in encryption:
                    setattr(args.data_encryption, name, encryption[key])

    class ClustersCreateOrReplace(ClusterCreate.ClustersCreateOrReplace):

        @property
        def content(self):
            content = super().content
            encryption_identity = content.get('identity')
            source = self.ctx.vars.restore_source.to_serialized_data()
            properties = content['properties']
            properties['creationMode'] = 'PointInTimeRestore'
            properties['creationSourceClusterResourceId'] = (
                self.ctx.args.creation_source_cluster_resource_id.to_serialized_data()
            )
            properties['pointInTimeUtc'] = self.ctx.args.point_in_time_utc.to_serialized_data()
            properties['creationSourceClusterLocation'] = source['location']
            if 'aiModelManagement' in source.get('properties', {}):
                properties['aiModelManagement'] = source['properties']['aiModelManagement']
            identity = source.get('identity')
            if identity is not None:
                content['identity'] = {'type': identity['type']}
                if 'userAssignedIdentities' in identity:
                    content['identity']['userAssignedIdentities'] = {
                        resource_id: {} for resource_id in identity['userAssignedIdentities']
                    }
                if encryption_identity is not None:
                    content['identity']['type'] = (
                        'SystemAssigned, UserAssigned' if 'SystemAssigned' in identity['type'] else 'UserAssigned'
                    )
                    content['identity'].setdefault('userAssignedIdentities', {}).update(
                        encryption_identity['userAssignedIdentities']
                    )
            return content
