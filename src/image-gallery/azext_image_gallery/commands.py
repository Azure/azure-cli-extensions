# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):
    with self.command_group('sig') as g:
        g.custom_command('create', 'create_image_gallery')
        g.custom_command('show-community', 'sig_community_gallery_show', is_experimental=True)

    with self.command_group('sig image-definition') as g:
        g.custom_command('show-community', 'sig_community_gallery_image_show', is_experimental=True)
        g.custom_command('list-community', 'sig_community_image_definition_list', is_experimental=True)

    with self.command_group('sig image-version') as g:
        g.custom_command('show-community', 'sig_community_image_version_show', is_experimental=True)
        g.custom_command('list-community', 'sig_community_image_version_list', is_experimental=True)

    with self.command_group('sig share') as g:
        g.custom_command('enable-community', 'sig_share_enable_community', supports_no_wait=True)