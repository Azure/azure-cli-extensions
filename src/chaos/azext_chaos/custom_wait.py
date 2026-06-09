# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Hand-written ``chaos scenario run wait`` command.

``aaz-dev`` only auto-generates ``_wait.py`` for resources whose spec advertises an
LRO; the public ``Microsoft.Chaos`` spec does not (yet) declare ``ScenarioRuns``
as an LRO-bearing resource, so the aaz tool emits no wait sibling. The CLI
linter (``require_wait_command_if_no_wait``) needs one anyway because
``chaos scenario run cancel`` declares ``supports_no_wait=True``.

Living next to ``custom.py`` (instead of under ``azext_chaos/aaz/``) keeps the
aaz-generated tree byte-identical with a fresh ``aaz-dev`` export. The command
is registered explicitly in :mod:`azext_chaos.commands` via
``self.command_table['chaos scenario run wait'] = ScenarioRunWait(loader=self)``.
"""

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "chaos scenario run wait",
)
class ScenarioRunWait(AAZWaitCommand):
    """Place the CLI in a waiting state until a condition is met.
    """

    _aaz_info = {
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.chaos/workspaces/{}/scenarios/{}/runs/{}", "2026-05-01-preview"],
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
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )
        _args_schema.run_id = AAZStrArg(
            options=["-n", "--name", "--run-id"],
            help="The name of the ScenarioRun",
            required=True,
            id_part="child_name_2",
            fmt=AAZStrArgFormat(
                pattern="^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
            ),
        )
        _args_schema.scenario_name = AAZStrArg(
            options=["--scenario-name"],
            help="Name of the scenario.",
            required=True,
            id_part="child_name_1",
            fmt=AAZStrArgFormat(
                pattern="^[^<>%&:?#/\\\\]+$",
                min_length=1,
            ),
        )
        _args_schema.workspace_name = AAZStrArg(
            options=["--workspace-name"],
            help="String that represents a Workspace resource name.",
            required=True,
            id_part="name",
            fmt=AAZStrArgFormat(
                pattern="^[^<>%&:?#/\\\\]+$",
                min_length=1,
            ),
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        self.ScenarioRunsGet(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=False)
        return result

    class ScenarioRunsGet(AAZHttpOperation):
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
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Chaos/workspaces/{workspaceName}/scenarios/{scenarioName}/runs/{runId}",
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
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "runId", self.ctx.args.run_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "scenarioName", self.ctx.args.scenario_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "workspaceName", self.ctx.args.workspace_name,
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
            _schema_on_200.name = AAZStrType(
                flags={"read_only": True},
            )
            _schema_on_200.properties = AAZObjectType()
            _schema_on_200.system_data = AAZObjectType(
                serialized_name="systemData",
                flags={"read_only": True},
            )
            _schema_on_200.type = AAZStrType(
                flags={"read_only": True},
            )

            return cls._schema_on_200


__all__ = ["ScenarioRunWait"]
