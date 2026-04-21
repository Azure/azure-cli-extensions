# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "service-group delete",
    confirmation="Are you sure you want to delete this service group?",
)
class Delete(AAZCommand):
    """Delete a service group.

    :example: Delete a service group
        az service-group delete --name MyServiceGroup --yes
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
        return self.build_lro_poller(self._execute_operations, None)

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
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        yield self.ServiceGroupsDelete(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    class ServiceGroupsDelete(AAZHttpOperation):
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
            if session.http_response.status_code in [204]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_204,
                    self.on_error,
                    lro_options={"final-state-via": "location"},
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
            return "DELETE"

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

        def on_204(self, session):
            pass

        def on_200(self, session):
            pass


class _DeleteHelper:
    """Helper class for Delete"""


__all__ = ["Delete"]
