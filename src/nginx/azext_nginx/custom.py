# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from .aaz.latest.nginx.deployment.configuration._update import Update as _ConfigurationUpdate
from azure.cli.core.aaz import *

class ConfigurationUpdate(_ConfigurationUpdate):

    @classmethod
    def _build_args_nginx_configuration_file_update(cls, _schema):
        if cls._args_nginx_configuration_file_update is not None:
            _schema.content = cls._args_nginx_configuration_file_update.content
            _schema.virtual_path = cls._args_nginx_configuration_file_update.virtual_path
            return

        cls._args_nginx_configuration_file_update = AAZObjectArg(
            nullable=True,
        )

        nginx_configuration_file_update = cls._args_nginx_configuration_file_update
        nginx_configuration_file_update.content = AAZStrArg(
            options=["content"],
            nullable=True,
        )
        nginx_configuration_file_update.virtual_path = AAZStrArg(
            options=["virtual-path"],
            nullable=True,
        )

        _schema.content = cls._args_nginx_configuration_file_update.content
        _schema.virtual_path = cls._args_nginx_configuration_file_update.virtual_path

    def _execute_operations(self):
        self.pre_operations()
        self.ConfigurationsGet(ctx=self.ctx)()
        self.pre_instance_update(self.ctx.vars.instance)
        self.InstanceUpdateByJson(ctx=self.ctx)()
        self.InstanceUpdateByGeneric(ctx=self.ctx)()
        self.post_instance_update(self.ctx.vars.instance)
        yield self.ConfigurationsCreateOrUpdate(ctx=self.ctx)()
        self.post_operations()

    class ConfigurationsGet(AAZHttpOperation):
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
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Nginx.NginxPlus/nginxDeployments/{deploymentName}/configurations/{configurationName}",
                **self.url_parameters
            )

        @property
        def method(self):
            return "GET"

        @property
        def error_format(self):
            return "MgmtErrorFormat"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "configurationName", self.ctx.args.configuration_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "deploymentName", self.ctx.args.deployment_name,
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
                    "api-version", "2024-01-01-preview",
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
            _UpdateHelper._build_schema_nginx_configuration_read(cls._schema_on_200)

            return cls._schema_on_200

class _UpdateHelper:
    """Helper class for Update"""

    @classmethod
    def _build_schema_nginx_configuration_file_update(cls, _builder):
        if _builder is None:
            return
        _builder.set_prop("content", AAZStrType, ".content")
        _builder.set_prop("virtualPath", AAZStrType, ".virtual_path")

    _schema_nginx_configuration_file_read = None

    @classmethod
    def _build_schema_nginx_configuration_file_read(cls, _schema):
        if cls._schema_nginx_configuration_file_read is not None:
            _schema.content = cls._schema_nginx_configuration_file_read.content
            _schema.virtual_path = cls._schema_nginx_configuration_file_read.virtual_path
            return

        cls._schema_nginx_configuration_file_read = _schema_nginx_configuration_file_read = AAZObjectType()

        nginx_configuration_file_read = _schema_nginx_configuration_file_read
        nginx_configuration_file_read.content = AAZStrType()
        nginx_configuration_file_read.virtual_path = AAZStrType(
            serialized_name="virtualPath",
        )

        _schema.content = cls._schema_nginx_configuration_file_read.content
        _schema.virtual_path = cls._schema_nginx_configuration_file_read.virtual_path

    _schema_nginx_configuration_read = None

    @classmethod
    def _build_schema_nginx_configuration_read(cls, _schema):
        if cls._schema_nginx_configuration_read is not None:
            _schema.id = cls._schema_nginx_configuration_read.id
            _schema.location = cls._schema_nginx_configuration_read.location
            _schema.name = cls._schema_nginx_configuration_read.name
            _schema.properties = cls._schema_nginx_configuration_read.properties
            _schema.system_data = cls._schema_nginx_configuration_read.system_data
            _schema.type = cls._schema_nginx_configuration_read.type
            return

        cls._schema_nginx_configuration_read = _schema_nginx_configuration_read = AAZObjectType()

        nginx_configuration_read = _schema_nginx_configuration_read
        nginx_configuration_read.id = AAZStrType(
            flags={"read_only": True},
        )
        nginx_configuration_read.location = AAZStrType()
        nginx_configuration_read.name = AAZStrType(
            flags={"read_only": True},
        )
        nginx_configuration_read.properties = AAZObjectType()
        nginx_configuration_read.system_data = AAZObjectType(
            serialized_name="systemData",
            flags={"read_only": True},
        )
        nginx_configuration_read.type = AAZStrType(
            flags={"read_only": True},
        )

        properties = _schema_nginx_configuration_read.properties
        properties.files = AAZListType()
        properties.package = AAZObjectType()
        properties.protected_files = AAZListType(
            serialized_name="protectedFiles",
        )
        properties.provisioning_state = AAZStrType(
            serialized_name="provisioningState",
            flags={"read_only": True},
        )
        properties.root_file = AAZStrType(
            serialized_name="rootFile",
        )

        files = _schema_nginx_configuration_read.properties.files
        files.Element = AAZObjectType()
        cls._build_schema_nginx_configuration_file_read(files.Element)

        package = _schema_nginx_configuration_read.properties.package
        package.data = AAZStrType()
        package.protected_files = AAZListType(
            serialized_name="protectedFiles",
        )

        protected_files = _schema_nginx_configuration_read.properties.package.protected_files
        protected_files.Element = AAZStrType()

        protected_files = _schema_nginx_configuration_read.properties.protected_files
        protected_files.Element = AAZObjectType()
        cls._build_schema_nginx_configuration_file_read(protected_files.Element)

        system_data = _schema_nginx_configuration_read.system_data
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

        _schema.id = cls._schema_nginx_configuration_read.id
        _schema.location = cls._schema_nginx_configuration_read.location
        _schema.name = cls._schema_nginx_configuration_read.name
        # _schema.properties = cls._schema_nginx_configuration_read.properties # by not setting the properties for get it will only use our update payload
        _schema.system_data = cls._schema_nginx_configuration_read.system_data
        _schema.type = cls._schema_nginx_configuration_read.type
