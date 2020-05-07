# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class CommandTable():  # pylint: disable=too-few-public-methods
    CMD_TBL = None


def on_command_table_loaded(_, **kwargs):
    cmd_tbl = kwargs.pop('cmd_tbl', None)
    CommandTable.CMD_TBL = cmd_tbl
