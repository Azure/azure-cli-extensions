# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import add_common_params


def load_azure_openai_deployment_params(self):
    with self.argument_context("ml azure-openai-deployment list") as c:
        add_common_params(c)
        c.argument(
            "connection_name",
            options_list=["--connection-name", "-c"],
            help="Name of the connection from which to list deployments",
        )
