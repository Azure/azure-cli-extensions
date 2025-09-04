# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

logger = get_logger(__name__)


# pylint: disable=too-many-statements
def load_command_table(self, _):
    with self.command_group(
        "aks",
    ) as g:
        g.custom_command("agent", "aks_agent")
