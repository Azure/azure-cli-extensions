# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_community_gallery_image_version


def load_command_table(self, _):

    community_gallery_image_version_sdk = CliCommandType(
        operations_tmpl='azext_image_gallery.vendored_sdks.azure_mgmt_compute.operations._community_gallery_image_versions_operations#CommunityGalleryImageVersionsOperations.{}',
        client_factory=cf_community_gallery_image_version)

    with self.command_group('sig') as g:
        g.custom_command('create', 'create_image_gallery')
        g.custom_command('show-community', 'sig_community_gallery_show', is_experimental=True)

    with self.command_group('sig image-definition') as g:
        g.custom_command('show-community', 'sig_community_gallery_image_show', is_experimental=True)
        g.custom_command('list-community', 'sig_community_image_definition_list', is_experimental=True)

    with self.command_group('sig image-version', community_gallery_image_version_sdk,
                            client_factory=cf_community_gallery_image_version) as g:
        g.custom_command('show-community', 'sig_community_image_version_show', is_experimental=True)
        g.custom_command('list-community', 'sig_community_image_version_list', is_experimental=True)

    with self.command_group('sig share') as g:
        g.custom_command('enable-community', 'sig_share_enable_community', supports_no_wait=True)
