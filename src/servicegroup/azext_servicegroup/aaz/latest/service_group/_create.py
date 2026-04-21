# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "service-group create",
)
class Create(AAZCommand):
    """Create or update a service group.

    :example: Create a service group under the tenant root
        az service-group create --name MyServiceGroup --display-name "My Service Group" --parent resource-id="/providers/Microsoft.Management/serviceGroups/<tenantId>"
    :example: Create a child service group under an existing parent
        az service-group create --name ChildGroup --display-name "Child" --parent resource-id="/providers/Microsoft.Management/serviceGroups/ParentGroup"
    """

    _aaz_info = {
        "version": "2024-02-01-preview",
        "resources": [
            ["mgmt-plane", "/providers/microsoft.management/servicegroups/{}", "2024-02-01-preview"],
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
        _args_schema.service_group_name = AAZStrArg(
            options=["-n", "--name"],
            help="ServiceGroup Name.",
            required=True,
            fmt=AAZStrArgFormat(
                pattern=r"^[a-zA-Z0-9\-_().]{1,90}$",
            ),
        )

        # define Arg Group "Resource"

        _args_schema = cls._args_schema
        _args_schema.kind = AAZStrArg(
            options=["--kind"],
            arg_group="Resource",
            help="The kind of the service group.",
        )
        _args_schema.tags = AAZDictArg(
            options=["--tags"],
            arg_group="Resource",
            help="The service group tags.",
        )

        tags = cls._args_schema.tags
        tags.Element = AAZStrArg()

        # define Arg Group "Properties"

        _args_schema = cls._args_schema
        _args_schema.display_name = AAZStrArg(
            options=["--display-name"],
            arg_group="Properties",
            help="The display name of the service group.",
        )
        _args_schema.parent = AAZObjectArg(
            options=["--parent"],
            arg_group="Properties",
            help="The details of the parent service group.",
        )

        parent = cls._args_schema.parent
        parent.resource_id = AAZStrArg(
            options=["resource-id"],
            help="The fully qualified ID of the parent service group. For example, '/providers/Microsoft.Management/serviceGroups/TestServiceGroup'.",
            required=True,
        )

        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.ServiceGroupsCreateOrUpdate(ctx=self.ctx)()
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

    class ServiceGroupsCreateOrUpdate(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [202]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )
            if session.http_response.status_code in [200, 201]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/providers/Microsoft.Management/serviceGroups/{serviceGroupName}",
                **self.url_parameters
            )

        @property
        def method(self):
            return "PUT"

        @property
        def error_format(self):
            return "MgmtErrorFormat"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "serviceGroupName", self.ctx.args.service_group_name,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2024-02-01-preview",
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
            _builder.set_prop("kind", AAZStrType, ".kind")
            _builder.set_prop("properties", AAZObjectType, typ_kwargs={"flags": {"client_flatten": True}})
            _builder.set_prop("tags", AAZDictType, ".tags")

            properties = _builder.get(".properties")
            if properties is not None:
                properties.set_prop("displayName", AAZStrType, ".display_name")
                properties.set_prop("parent", AAZObjectType, ".parent")

            parent = _builder.get(".properties.parent")
            if parent is not None:
                parent.set_prop("resourceId", AAZStrType, ".resource_id")

            tags = _builder.get(".tags")
            if tags is not None:
                tags.set_elements(AAZStrType, ".")

            return self.serialize_content(_content_value)

        def on_200_201(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200_201
            )

        _schema_on_200_201 = None

        @classmethod
        def _build_schema_on_200_201(cls):
            if cls._schema_on_200_201 is not None:
                return cls._schema_on_200_201

            cls._schema_on_200_201 = AAZObjectType()

            _schema_on_200_201 = cls._schema_on_200_201
            _schema_on_200_201.id = AAZStrType(
                flags={"read_only": True},
            )
            _schema_on_200_201.kind = AAZStrType()
            _schema_on_200_201.name = AAZStrType(
                flags={"read_only": True},
            )
            _schema_on_200_201.properties = AAZObjectType(
                flags={"client_flatten": True},
            )
            _schema_on_200_201.system_data = AAZObjectType(
                serialized_name="systemData",
                flags={"read_only": True},
            )
            _schema_on_200_201.tags = AAZDictType()
            _schema_on_200_201.type = AAZStrType(
                flags={"read_only": True},
            )

            properties = cls._schema_on_200_201.properties
            properties.display_name = AAZStrType(
                serialized_name="displayName",
            )
            properties.parent = AAZObjectType()
            properties.provisioning_state = AAZStrType(
                serialized_name="provisioningState",
                flags={"read_only": True},
            )

            parent = cls._schema_on_200_201.properties.parent
            parent.resource_id = AAZStrType(
                serialized_name="resourceId",
            )

            system_data = cls._schema_on_200_201.system_data
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

            tags = cls._schema_on_200_201.tags
            tags.Element = AAZStrType()

            return cls._schema_on_200_201


class _CreateHelper:
    """Helper class for Create"""


__all__ = ["Create"]
