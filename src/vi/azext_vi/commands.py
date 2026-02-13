# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._client_factory import cf_vi
from ._format import camera_list_table_format
from . import consts


def load_command_table(self, _):
    with self.command_group(f"{consts.EXTENSION_NAME} extension", client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_show_command('show', 'show_vi_extension')
        g.custom_command('troubleshoot', 'troubleshoot_vi_extension')

    with self.command_group(f"{consts.EXTENSION_NAME} camera", client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_command('add', 'add_camera')
        g.custom_command('list', 'list_cameras', table_transformer=camera_list_table_format)
