# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group("confcom") as g:
        g.custom_command("acipolicygen", "acipolicygen_confcom")

    with self.command_group("confcom", is_preview=True):
        pass
