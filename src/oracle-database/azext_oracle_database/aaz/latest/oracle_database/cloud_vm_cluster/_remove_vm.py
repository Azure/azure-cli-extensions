# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# Code generated by aaz-dev-tools
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "oracle-database cloud-vm-cluster remove-vm",
)
class RemoveVm(AAZCommand):
    """Remove VMs from the VM Cluster

    :example: Remove VM from Cluster
        az oracle-database cloud-vm-cluster remove-vm --cloudvmclustername <vmclustername> --resource-group <Resource group> --db-servers ['ocid1','ocid2']
    """

    _aaz_info = {
        "version": "2023-09-01",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/oracle.database/cloudvmclusters/{}/removevms", "2023-09-01"],
        ]
    }

    AZ_SUPPORT_NO_WAIT = True

    def _handler(self, command_args):
        super()._handler(command_args)
        return self.build_lro_poller(self._execute_operations, self._output)

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        # define Arg Group ""

        _args_schema = cls._args_schema
        _args_schema.cloudvmclustername = AAZStrArg(
            options=["--cloudvmclustername"],
            help="CloudVmCluster name",
            required=True,
            id_part="name",
            fmt=AAZStrArgFormat(
                pattern=".*",
            ),
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )

        # define Arg Group "Body"

        _args_schema = cls._args_schema
        _args_schema.db_servers = AAZListArg(
            options=["--db-servers"],
            arg_group="Body",
            help="Db servers ocids",
            required=True,
        )

        db_servers = cls._args_schema.db_servers
        db_servers.Element = AAZStrArg(
            fmt=AAZStrArgFormat(
                max_length=255,
                min_length=1,
            ),
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.CloudVmClustersRemoveVms(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result

    class CloudVmClustersRemoveVms(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [202]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200,
                    self.on_error,
                    lro_options={"final-state-via": "location"},
                    path_format_arguments=self.url_parameters,
                )
            if session.http_response.status_code in [200]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200,
                    self.on_error,
                    lro_options={"final-state-via": "location"},
                    path_format_arguments=self.url_parameters,
                )

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Oracle.Database/cloudVmClusters/{cloudvmclustername}/removeVms",
                **self.url_parameters
            )

        @property
        def method(self):
            return "POST"

        @property
        def error_format(self):
            return "MgmtErrorFormat"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "cloudvmclustername", self.ctx.args.cloudvmclustername,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2023-09-01",
                    required=True,
                ),
            }
            return parameters

        @property
        def header_parameters(self):
            parameters = {
                **self.serialize_header_param(
                    "Content-Type", "application/json",
                ),
                **self.serialize_header_param(
                    "Accept", "application/json",
                ),
            }
            return parameters

        @property
        def content(self):
            _content_value, _builder = self.new_content_builder(
                self.ctx.args,
                typ=AAZObjectType,
                typ_kwargs={"flags": {"required": True, "client_flatten": True}}
            )
            _builder.set_prop("dbServers", AAZListType, ".db_servers", typ_kwargs={"flags": {"required": True}})

            db_servers = _builder.get(".dbServers")
            if db_servers is not None:
                db_servers.set_elements(AAZStrType, ".")

            return self.serialize_content(_content_value)

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200
            )

        _schema_on_200 = None

        @classmethod
        def _build_schema_on_200(cls):
            if cls._schema_on_200 is not None:
                return cls._schema_on_200

            cls._schema_on_200 = AAZObjectType()

            _schema_on_200 = cls._schema_on_200
            _schema_on_200.id = AAZStrType(
                flags={"read_only": True},
            )
            _schema_on_200.location = AAZStrType(
                flags={"required": True},
            )
            _schema_on_200.name = AAZStrType(
                flags={"read_only": True},
            )
            _schema_on_200.properties = AAZObjectType(
                flags={"client_flatten": True},
            )
            _schema_on_200.system_data = AAZObjectType(
                serialized_name="systemData",
                flags={"read_only": True},
            )
            _schema_on_200.tags = AAZDictType()
            _schema_on_200.type = AAZStrType(
                flags={"read_only": True},
            )

            properties = cls._schema_on_200.properties
            properties.backup_subnet_cidr = AAZStrType(
                serialized_name="backupSubnetCidr",
            )
            properties.cloud_exadata_infrastructure_id = AAZStrType(
                serialized_name="cloudExadataInfrastructureId",
                flags={"required": True},
            )
            properties.cluster_name = AAZStrType(
                serialized_name="clusterName",
            )
            properties.compartment_id = AAZStrType(
                serialized_name="compartmentId",
            )
            properties.cpu_core_count = AAZIntType(
                serialized_name="cpuCoreCount",
                flags={"required": True},
            )
            properties.data_collection_options = AAZObjectType(
                serialized_name="dataCollectionOptions",
            )
            properties.data_storage_percentage = AAZIntType(
                serialized_name="dataStoragePercentage",
            )
            properties.data_storage_size_in_tbs = AAZFloatType(
                serialized_name="dataStorageSizeInTbs",
            )
            properties.db_node_storage_size_in_gbs = AAZIntType(
                serialized_name="dbNodeStorageSizeInGbs",
            )
            properties.db_servers = AAZListType(
                serialized_name="dbServers",
            )
            properties.disk_redundancy = AAZStrType(
                serialized_name="diskRedundancy",
            )
            properties.display_name = AAZStrType(
                serialized_name="displayName",
                flags={"required": True},
            )
            properties.domain = AAZStrType()
            properties.gi_version = AAZStrType(
                serialized_name="giVersion",
                flags={"required": True},
            )
            properties.hostname = AAZStrType(
                flags={"required": True},
            )
            properties.iorm_config_cache = AAZObjectType(
                serialized_name="iormConfigCache",
            )
            properties.is_local_backup_enabled = AAZBoolType(
                serialized_name="isLocalBackupEnabled",
            )
            properties.is_sparse_diskgroup_enabled = AAZBoolType(
                serialized_name="isSparseDiskgroupEnabled",
            )
            properties.last_update_history_entry_id = AAZStrType(
                serialized_name="lastUpdateHistoryEntryId",
            )
            properties.license_model = AAZStrType(
                serialized_name="licenseModel",
            )
            properties.lifecycle_details = AAZStrType(
                serialized_name="lifecycleDetails",
                flags={"read_only": True},
            )
            properties.lifecycle_state = AAZStrType(
                serialized_name="lifecycleState",
            )
            properties.listener_port = AAZIntType(
                serialized_name="listenerPort",
                flags={"read_only": True},
            )
            properties.memory_size_in_gbs = AAZIntType(
                serialized_name="memorySizeInGbs",
            )
            properties.node_count = AAZIntType(
                serialized_name="nodeCount",
                flags={"read_only": True},
            )
            properties.nsg_cidrs = AAZListType(
                serialized_name="nsgCidrs",
            )
            properties.nsg_url = AAZStrType(
                serialized_name="nsgUrl",
                flags={"read_only": True},
            )
            properties.oci_url = AAZStrType(
                serialized_name="ociUrl",
                flags={"read_only": True},
            )
            properties.ocid = AAZStrType()
            properties.ocpu_count = AAZFloatType(
                serialized_name="ocpuCount",
            )
            properties.provisioning_state = AAZStrType(
                serialized_name="provisioningState",
                flags={"read_only": True},
            )
            properties.scan_dns_name = AAZStrType(
                serialized_name="scanDnsName",
                flags={"read_only": True},
            )
            properties.scan_dns_record_id = AAZStrType(
                serialized_name="scanDnsRecordId",
            )
            properties.scan_ip_ids = AAZListType(
                serialized_name="scanIpIds",
                flags={"read_only": True},
            )
            properties.scan_listener_port_tcp = AAZIntType(
                serialized_name="scanListenerPortTcp",
            )
            properties.scan_listener_port_tcp_ssl = AAZIntType(
                serialized_name="scanListenerPortTcpSsl",
            )
            properties.shape = AAZStrType(
                flags={"read_only": True},
            )
            properties.ssh_public_keys = AAZListType(
                serialized_name="sshPublicKeys",
                flags={"required": True},
            )
            properties.storage_size_in_gbs = AAZIntType(
                serialized_name="storageSizeInGbs",
            )
            properties.subnet_id = AAZStrType(
                serialized_name="subnetId",
                flags={"required": True},
            )
            properties.subnet_ocid = AAZStrType(
                serialized_name="subnetOcid",
            )
            properties.system_version = AAZStrType(
                serialized_name="systemVersion",
            )
            properties.time_created = AAZStrType(
                serialized_name="timeCreated",
                flags={"read_only": True},
            )
            properties.time_zone = AAZStrType(
                serialized_name="timeZone",
            )
            properties.vip_ids = AAZListType(
                serialized_name="vipIds",
                flags={"read_only": True},
            )
            properties.vnet_id = AAZStrType(
                serialized_name="vnetId",
                flags={"required": True},
            )
            properties.zone_id = AAZStrType(
                serialized_name="zoneId",
            )

            data_collection_options = cls._schema_on_200.properties.data_collection_options
            data_collection_options.is_diagnostics_events_enabled = AAZBoolType(
                serialized_name="isDiagnosticsEventsEnabled",
            )
            data_collection_options.is_health_monitoring_enabled = AAZBoolType(
                serialized_name="isHealthMonitoringEnabled",
            )
            data_collection_options.is_incident_logs_enabled = AAZBoolType(
                serialized_name="isIncidentLogsEnabled",
            )

            db_servers = cls._schema_on_200.properties.db_servers
            db_servers.Element = AAZStrType()

            iorm_config_cache = cls._schema_on_200.properties.iorm_config_cache
            iorm_config_cache.db_plans = AAZListType(
                serialized_name="dbPlans",
            )
            iorm_config_cache.lifecycle_details = AAZStrType(
                serialized_name="lifecycleDetails",
            )
            iorm_config_cache.lifecycle_state = AAZStrType(
                serialized_name="lifecycleState",
            )
            iorm_config_cache.objective = AAZStrType()

            db_plans = cls._schema_on_200.properties.iorm_config_cache.db_plans
            db_plans.Element = AAZObjectType()

            _element = cls._schema_on_200.properties.iorm_config_cache.db_plans.Element
            _element.db_name = AAZStrType(
                serialized_name="dbName",
            )
            _element.flash_cache_limit = AAZStrType(
                serialized_name="flashCacheLimit",
            )
            _element.share = AAZIntType()

            nsg_cidrs = cls._schema_on_200.properties.nsg_cidrs
            nsg_cidrs.Element = AAZObjectType()

            _element = cls._schema_on_200.properties.nsg_cidrs.Element
            _element.destination_port_range = AAZObjectType(
                serialized_name="destinationPortRange",
            )
            _element.source = AAZStrType(
                flags={"required": True},
            )

            destination_port_range = cls._schema_on_200.properties.nsg_cidrs.Element.destination_port_range
            destination_port_range.max = AAZIntType(
                flags={"required": True},
            )
            destination_port_range.min = AAZIntType(
                flags={"required": True},
            )

            scan_ip_ids = cls._schema_on_200.properties.scan_ip_ids
            scan_ip_ids.Element = AAZStrType()

            ssh_public_keys = cls._schema_on_200.properties.ssh_public_keys
            ssh_public_keys.Element = AAZStrType()

            vip_ids = cls._schema_on_200.properties.vip_ids
            vip_ids.Element = AAZStrType()

            system_data = cls._schema_on_200.system_data
            system_data.created_at = AAZStrType(
                serialized_name="createdAt",
            )
            system_data.created_by = AAZStrType(
                serialized_name="createdBy",
            )
            system_data.created_by_type = AAZStrType(
                serialized_name="createdByType",
            )
            system_data.last_modified_at = AAZStrType(
                serialized_name="lastModifiedAt",
            )
            system_data.last_modified_by = AAZStrType(
                serialized_name="lastModifiedBy",
            )
            system_data.last_modified_by_type = AAZStrType(
                serialized_name="lastModifiedByType",
            )

            tags = cls._schema_on_200.tags
            tags.Element = AAZStrType()

            return cls._schema_on_200


class _RemoveVmHelper:
    """Helper class for RemoveVm"""


__all__ = ["RemoveVm"]
