# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_community_gallery, cf_community_gallery_image, cf_community_gallery_image_version, cf_galleries, cf_community_gallery_sharing_profile


def load_command_table(self, _):

    community_gallery_sdk = CliCommandType(
        operations_tmpl='azext_image_gallery.vendored_sdks.azure_mgmt_compute.operations._community_galleries_operations#CommunityGalleriesOperations.{}',
        client_factory=cf_community_gallery)

    community_gallery_image_sdk = CliCommandType(
        operations_tmpl='azext_image_gallery.vendored_sdks.azure_mgmt_compute.operations._community_gallery_images_operations#CommunityGalleryImagesOperations.{}',
        client_factory=cf_community_gallery_image)

    community_gallery_image_version_sdk = CliCommandType(
        operations_tmpl='azext_image_gallery.vendored_sdks.azure_mgmt_compute.operations._community_gallery_image_versions_operations#CommunityGalleryImageVersionsOperations.{}',
        client_factory=cf_community_gallery_image_version)

    community_gallery_sharing_profile_sdk = CliCommandType(
        operations_tmpl='azext_image_gallery.vendored_sdks.azure_mgmt_compute.operations._gallery_sharing_profile_operations#GallerySharingProfileOperations.{}',
        client_factory=cf_community_gallery_sharing_profile)

    compute_galleries_sdk = CliCommandType(
        operations_tmpl='azext_image_gallery.vendored_sdks.azure_mgmt_compute.operations._galleries_operations#GalleriesOperations.{}',
        client_factory=cf_galleries,
    )

    with self.command_group('sig', compute_galleries_sdk, client_factory=cf_galleries) as g:
        g.custom_command('create', 'create_image_gallery')

    with self.command_group('sig', community_gallery_sdk, client_factory=cf_community_gallery) as g:
        g.command('show-community', 'get', is_experimental=True)

    with self.command_group('sig image-definition', community_gallery_image_sdk,
                            client_factory=cf_community_gallery_image) as g:
        g.command('show-community', 'get', is_experimental=True)
        g.custom_command('list-community', 'sig_community_image_definition_list', is_experimental=True)

    with self.command_group('sig image-version', community_gallery_image_version_sdk,
                            client_factory=cf_community_gallery_image_version) as g:
        g.command('show-community', 'get', is_experimental=True)
        g.custom_command('list-community', 'sig_community_image_version_list', is_experimental=True)

    with self.command_group('sig share', community_gallery_sharing_profile_sdk,
                            client_factory=cf_community_gallery_sharing_profile) as g:
        g.custom_command('enable-community', 'sig_share_update', supports_no_wait=True)
