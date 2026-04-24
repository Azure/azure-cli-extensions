# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *
from ._create import Create


@register_command(
    "fileshare private-endpoint-connection reject",
)
class Reject(Create):
    """Reject a private endpoint connection for a file share.

    :example: Reject a private endpoint connection
        az fileshare private-endpoint-connection reject --name MyConnection --resource-group MyRG --resource-name MyFileShare --description "Policy violation"
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.private_link_service_connection_state._registered = False
        args_schema.description = AAZStrArg(
            options=["--description"],
            help="Comments for the rejection.",
        )
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        connection_state = {"status": "Rejected"}
        if has_value(args.description):
            connection_state["description"] = args.description.to_serialized_data()
        args.private_link_service_connection_state = connection_state
