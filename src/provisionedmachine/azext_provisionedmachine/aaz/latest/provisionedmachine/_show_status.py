# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "provisionedmachine show-status",
    is_preview=True,
)
class ShowStatus(AAZCommand):
    """Show the lifecycle status of a specific Provisioned Machine resource.

    :example: Show lifecycle status of a provisioned machine
        az provisionedmachine show-status -n myProvisionedMachine -g myResourceGroup

    :example: Show lifecycle status in table format
        az provisionedmachine show-status -n myProvisionedMachine -g myResourceGroup -o table

    :example: Show the lifecycle status using full resource ID
        az provisionedmachine show-status --ids "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.AzureStackHCI/edgeMachines/myProvisionedMachine"
    """

    _aaz_info = {
        "version": "2026-05-01-preview",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.azurestackhci/edgemachines/{}", "2026-05-01-preview"],
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

        _args_schema = cls._args_schema
        _args_schema.edge_machine_name = AAZStrArg(
            options=["-n", "--name", "--provisioned-machine-name"],
            help="Name of the provisioned machine. Must be 4-128 characters, start and end with alphanumeric, and contain only alphanumeric characters and hyphens.",
            required=True,
            id_part="name",
            fmt=AAZStrArgFormat(
                pattern="^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$",
                max_length=128,
                min_length=4,
            ),
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        self.EdgeMachinesGet(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        from azure.cli.core.azclierror import ResourceNotFoundError

        # Get raw result without flattening to preserve field order
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=False)
        if isinstance(result, dict):
            properties = result.get("properties", {})
            lifecycle_details = properties.get("lifecycleDetails")

            if not lifecycle_details:
                machine_name = self.ctx.args.edge_machine_name.to_serialized_data()
                raise ResourceNotFoundError(
                    f"Lifecycle status is not available for provisioned machine '{machine_name}'. "
                    f"This information may not be populated for machines provisioned before lifecycle tracking was enabled. "
                    f"Use 'az provisionedmachine show' to view the current machine details."
                )

            return lifecycle_details
        return result

    class EdgeMachinesGet(AAZHttpOperation):
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
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.AzureStackHCI/edgeMachines/{edgeMachineName}",
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
                    "edgeMachineName", self.ctx.args.edge_machine_name,
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
                    "api-version", "2026-05-01-preview",
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
            self.ctx.set_var("instance", data, schema_builder=lambda: AAZAnyType())

        _schema_on_200 = None

        @classmethod
        def _build_schema_on_200(cls):
            if cls._schema_on_200 is not None:
                return cls._schema_on_200

            cls._schema_on_200 = AAZObjectType()
            return cls._schema_on_200


class _ShowStatusHelper:
    """Helper class for ShowStatus"""


__all__ = ["ShowStatus"]
