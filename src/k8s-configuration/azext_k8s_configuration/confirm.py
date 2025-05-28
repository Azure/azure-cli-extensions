# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.util import user_confirmation


def user_confirmation_factory(
    cmd, yes, message="Are you sure you want to perform this operation?"
):
    if cmd.cli_ctx.config.getboolean("core", "disable_confirm_prompt", fallback=False):
        return
    user_confirmation(message, yes=yes)
