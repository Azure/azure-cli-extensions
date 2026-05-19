# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "provisionedmachine reset-os",
    is_preview=True,
)
class ResetOs(AAZCommand):
    """Resets a specific Provisioned Machine resource to maintenance operating system.

    :example: Resets a provisioned machine
        az provisionedmachine reset-os -g myResourceGroup -n myProvisionedMachine
    """

    _aaz_info = {
        "version": "2025-12-01-preview",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.azurestackhci/edgemachines/{}/jobs/ProvisionOs", "2025-12-01-preview"],
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

        _args_schema = cls._args_schema

        # Define Arg Group "" (default - Resource identifiers)
        _args_schema.edge_machine_name = AAZStrArg(
            options=["-n", "--name", "--provisioned-machine-name"],
            help="Name of the provisioned machine. Must be 4-128 characters, start and end with alphanumeric, and contain only alphanumeric characters and hyphens.",
            required=True,
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
        yield self.EdgeMachinesJobsProvisionOs(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        self._validate_machine_state()

    def _validate_machine_state(self):
        """Validate that the provisioned machine is in 'Purposed' state before reset."""
        from azure.cli.core.util import send_raw_request
        from azure.cli.core.azclierror import InvalidArgumentValueError
        import logging

        logger = logging.getLogger(__name__)
        args = self.ctx.args

        try:
            url = (
                f"/subscriptions/{self.ctx.subscription_id}"
                f"/resourceGroups/{args.resource_group.to_serialized_data()}"
                f"/providers/Microsoft.AzureStackHCI/edgeMachines/{args.edge_machine_name.to_serialized_data()}"
                f"?api-version=2025-12-01-preview"
            )

            response = send_raw_request(self.ctx.cli_ctx, "GET", url)

            if response.status_code == 200:
                data = response.json()
                machine_state = data.get('properties', {}).get('machineState', '')
                
                allowed_states = ['Purposed', 'Transitioning', 'Resetting']
                if machine_state not in allowed_states:
                    raise InvalidArgumentValueError(
                        f"Cannot reset provisioned machine '{args.edge_machine_name.to_serialized_data()}'. "
                        f"Machine is in '{machine_state}' state. Reset is only allowed when machine is in {allowed_states} state."
                    )
                logger.info("Machine state validated: %s", machine_state)
            else:
                raise InvalidArgumentValueError(
                    f"Failed to get provisioned machine '{args.edge_machine_name.to_serialized_data()}': HTTP {response.status_code}"
                )

        except InvalidArgumentValueError:
            raise
        except Exception as e:
            raise InvalidArgumentValueError(
                f"Error validating machine state: {str(e)}"
            )

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        return self.ctx.vars.instance

    class EdgeMachinesJobsProvisionOs(AAZHttpOperation):
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
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.AzureStackHCI/edgeMachines/{edgeMachineName}/jobs/ProvisionOs",
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
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "edgeMachineName", self.ctx.args.edge_machine_name,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2025-12-01-preview",
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
            return {
                "properties": {
                    "jobType": "ProvisionOs",
                    "deploymentMode": "Deploy",
                    "provisioningRequest": {
                        "target": "AzureLinux",
                        "osProfile": {
                            "osName": "AzureLinux",
                            "osType": "AzureLinuxROE",
                            "osVersion": "3.0",
                            "osImageLocation": "https://aka.ms/aep/installeros/2602.reset"
                        },
                        "deviceConfiguration": {}
                    }
                }
            }

        def on_200_201(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var("instance", data, schema_builder=lambda: AAZAnyType())
