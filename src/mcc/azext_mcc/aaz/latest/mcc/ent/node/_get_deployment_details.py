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
    "mcc ent node get-deployment-details",
)
class GetDeploymentDetails(AAZCommand):
    """Retrieves Microsoft Connected Cache for Enterprise cache node details and keys needed to deploy cache node.

    :example: Get Deployment Details For MCC Enterprise Cache Node
        az mcc ent node get-deployment-details --mcc-resource-name [MccResourceName] --cache-node-name [MccCacheNodeName] --resource-group [MccResourceRgName]
    """

    _aaz_info = {
        "version": "2024-11-30-preview",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.connectedcache/enterprisemcccustomers/{}/enterprisemcccachenodes/{}/getcachenodeinstalldetails", "2024-11-30-preview"],
        ]
    }

    def _handler(self, command_args):
        super()._handler(command_args)
        self._execute_operations()
        return self._output()

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        # define Arg Group ""

        _args_schema = cls._args_schema
        _args_schema.cache_node_name = AAZStrArg(
            options=["--cache-node-name"],
            help="Name of Microsoft Connected Cache for Enterprise cache node.",
            required=True,
            id_part="child_name_1",
            fmt=AAZStrArgFormat(
                pattern="^[a-zA-Z0-9\\_\\-]*",
                max_length=90,
                min_length=1,
            ),
        )
        _args_schema.mcc_resource_name = AAZStrArg(
            options=["--mcc-resource-name"],
            help="Name of Microsoft Connected Cache for Enterprise resource.",
            required=True,
            id_part="name",
            fmt=AAZStrArgFormat(
                pattern="^[a-zA-Z0-9\\_\\-]*",
                max_length=90,
                min_length=1,
            ),
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        self.EnterpriseMccCacheNodesOperationsGetCacheNodeInstallDetails(ctx=self.ctx)()
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

    class EnterpriseMccCacheNodesOperationsGetCacheNodeInstallDetails(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ConnectedCache/enterpriseMccCustomers/{customerResourceName}/enterpriseMccCacheNodes/{cacheNodeResourceName}/getCacheNodeInstallDetails",
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
                    "cacheNodeResourceName", self.ctx.args.cache_node_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "customerResourceName", self.ctx.args.mcc_resource_name,
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
                    "api-version", "2024-11-30-preview",
                    required=True,
                ),
            }
            return parameters

        @property
        def header_parameters(self):
            parameters = {
                **self.serialize_header_param(
                    "Accept", "application/json",
                ),
            }
            return parameters

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
            _schema_on_200.properties = AAZObjectType()
            _schema_on_200.system_data = AAZObjectType(
                serialized_name="systemData",
                flags={"read_only": True},
            )
            _schema_on_200.tags = AAZDictType()
            _schema_on_200.type = AAZStrType(
                flags={"read_only": True},
            )

            properties = cls._schema_on_200.properties
            properties.cache_node_id = AAZStrType(
                serialized_name="cacheNodeId",
            )
            properties.customer_id = AAZStrType(
                serialized_name="customerId",
            )
            properties.drive_configuration = AAZListType(
                serialized_name="driveConfiguration",
            )
            properties.primary_account_key = AAZStrType(
                serialized_name="primaryAccountKey",
                flags={"secret": True, "read_only": True},
            )
            properties.proxy_url_configuration = AAZObjectType(
                serialized_name="proxyUrlConfiguration",
            )
            properties.registration_key = AAZStrType(
                serialized_name="registrationKey",
                flags={"secret": True, "read_only": True},
            )
            properties.secondary_account_key = AAZStrType(
                serialized_name="secondaryAccountKey",
                flags={"secret": True, "read_only": True},
            )
            properties.tls_certificate_provisioning_key = AAZStrType(
                serialized_name="tlsCertificateProvisioningKey",
                flags={"secret": True, "read_only": True},
            )

            drive_configuration = cls._schema_on_200.properties.drive_configuration
            drive_configuration.Element = AAZObjectType()

            _element = cls._schema_on_200.properties.drive_configuration.Element
            _element.cache_number = AAZIntType(
                serialized_name="cacheNumber",
            )
            _element.nginx_mapping = AAZStrType(
                serialized_name="nginxMapping",
            )
            _element.physical_path = AAZStrType(
                serialized_name="physicalPath",
            )
            _element.size_in_gb = AAZIntType(
                serialized_name="sizeInGb",
            )

            proxy_url_configuration = cls._schema_on_200.properties.proxy_url_configuration
            proxy_url_configuration.proxy_url = AAZStrType(
                serialized_name="proxyUrl",
            )

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


class _GetDeploymentDetailsHelper:
    """Helper class for GetDeploymentDetails"""


__all__ = ["GetDeploymentDetails"]
