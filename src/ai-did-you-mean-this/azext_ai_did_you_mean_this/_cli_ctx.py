# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class CliContext():  # pylint: disable=too-few-public-methods
    CLI_CTX = None


def on_extension_loaded(cli_ctx):
    CliContext.CLI_CTX = cli_ctx
