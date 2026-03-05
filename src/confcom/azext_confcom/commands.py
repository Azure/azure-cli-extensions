# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group("confcom") as g:
        g.custom_command("acipolicygen", "acipolicygen_confcom")
        g.custom_command("acifragmentgen", "acifragmentgen_confcom")
        g.custom_command("katapolicygen", "katapolicygen_confcom")

    with self.command_group("confcom fragment") as g:
        g.custom_command("attach", "fragment_attach", is_preview=True)
        g.custom_command("push", "fragment_push", is_preview=True)

    with self.command_group("confcom"):
        pass

    with self.command_group("confcom containers") as g:
        g.custom_command("from_vn2", "containers_from_vn2")
        g.custom_command("from_image", "containers_from_image")
