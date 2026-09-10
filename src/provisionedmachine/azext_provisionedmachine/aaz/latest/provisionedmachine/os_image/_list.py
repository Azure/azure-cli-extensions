# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "provisionedmachine os-image list",
    is_preview=True,
)
class List(AAZCommand):
    """List available OS images for provisioning.

    Lists validated OS images available for provisioning in a specific Azure region,
    filtered by OS image type (HCI or AzureLinux).

    :example: List available AzureLinux OS images (defaults to eastus)
        az provisionedmachine os-image list --os-image-type AzureLinux

    :example: List available HCI OS images in a specific region with table output
        az provisionedmachine os-image list --location australiaeast --os-image-type HCI -o table
    """

    _aaz_info = {
        "version": "2026-05-01-preview",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/providers/microsoft.azurestackhci/locations/{}/osimages", "2026-05-01-preview"],
        ]
    }

    AZ_SUPPORT_PAGINATION = True

    def _handler(self, command_args):
        super()._handler(command_args)
        return self.build_paging(self._execute_operations, self._output)

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.location = AAZStrArg(
            options=["-l", "--location"],
            help="Azure region. Defaults to 'eastus' if not specified. Values from: az account list-locations.",
            default="eastus",
        )
        _args_schema.os_image_type = AAZStrArg(
            options=["--os-image-type"],
            help="Type of OS image to list. Allowed values: HCI, AzureLinux.",
            enum={"HCI": "HCI", "AzureLinux": "AzureLinux"},
            required=True,
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        self.OsImagesList(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance.value, client_flatten=True)
        next_link = self.deserialize_output(self.ctx.vars.instance.next_link)
        
        # Inject os_image_type from command args into each result item for table transformer
        os_image_type = self.ctx.args.os_image_type.to_serialized_data()
        if result and isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    item['_os_image_type'] = os_image_type
        
        return result, next_link

    class OsImagesList(AAZHttpOperation):
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
                "/subscriptions/{subscriptionId}/providers/Microsoft.AzureStackHCI/locations/{location}/osImages",
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
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "location", self.ctx.args.location,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            # Convert os_image_type to lowercase for API (API expects lowercase)
            os_image_type_lower = self.ctx.args.os_image_type.to_serialized_data().lower()
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2026-05-01-preview",
                    required=True,
                ),
                "solution-type": os_image_type_lower,
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
            _schema_on_200.next_link = AAZStrType(
                serialized_name="nextLink",
            )
            _schema_on_200.value = AAZListType(
                flags={"required": True},
            )

            value = cls._schema_on_200.value
            value.Element = AAZAnyType()

            return cls._schema_on_200


class _ListHelper:
    """Helper class for List"""


__all__ = ["List"]
