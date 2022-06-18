# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from knack.log import get_logger
from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.azclierror import RequiredArgumentMissingError
from azure.cli.core.util import sdk_no_wait
from ._client_factory import _compute_client_factory
logger = get_logger(__name__)


def sig_community_image_definition_list(client, location, public_gallery_name, marker=None, show_next_marker=None):
    generator = client.list(location=location, public_gallery_name=public_gallery_name)
    return get_page_result(generator, marker, show_next_marker)


def sig_community_image_version_list(client, location, public_gallery_name, gallery_image_name, marker=None,
                                     show_next_marker=None):
    generator = client.list(location=location, public_gallery_name=public_gallery_name,
                            gallery_image_name=gallery_image_name)
    return get_page_result(generator, marker, show_next_marker)


def get_page_result(generator, marker, show_next_marker=None):
    pages = generator.by_page(continuation_token=marker)  # ContainerPropertiesPaged
    result = list_generator(pages=pages)

    if show_next_marker:
        next_marker = {"nextMarker": pages.continuation_token}
        result.append(next_marker)
    else:
        if pages.continuation_token:
            logger.warning('Next Marker:')
            logger.warning(pages.continuation_token)

    return result


# The REST service takes 50 items as a page by default
def list_generator(pages, num_results=50):
    result = []

    # get first page items
    page = list(next(pages))
    result += page

    while True:
        if not pages.continuation_token:
            break

        # handle num results
        if num_results is not None:
            if num_results == len(result):
                break

        page = list(next(pages))
        result += page

    return result


def _get_resource_group_location(cli_ctx, resource_group_name):
    client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    # pylint: disable=no-member
    return client.resource_groups.get(resource_group_name).location


def create_image_gallery(cmd, resource_group_name, gallery_name, description=None,
                         location=None, no_wait=False, tags=None, permissions=None, soft_delete=None,
                         publisher_uri=None, publisher_contact=None, eula=None, public_name_prefix=None):
    from .vendored_sdks.azure_mgmt_compute.models._models_py3 import Gallery
    location = location or _get_resource_group_location(cmd.cli_ctx, resource_group_name)
    gallery = Gallery(description=description, location=location, tags=(tags or {}))
    if soft_delete is not None:
        gallery.soft_delete_policy = {'is_soft_delete_enabled': soft_delete}
    client = _compute_client_factory(cmd.cli_ctx)
    if permissions:
        from .vendored_sdks.azure_mgmt_compute.models._models_py3 import SharingProfile
        gallery.sharing_profile = SharingProfile(permissions=permissions)
        if permissions == 'Community':
            if publisher_uri is None or publisher_contact is None or eula is None or public_name_prefix is None:
                raise RequiredArgumentMissingError('If you want to share to the community, '
                                                   'you need to fill in all the following parameters:'
                                                   ' --publisher-uri, --publisher-email, --eula, --public-name-prefix.')

            from .vendored_sdks.azure_mgmt_compute.models._models_py3 import CommunityGalleryInfo
            gallery.sharing_profile.community_gallery_info = CommunityGalleryInfo(publisher_uri=publisher_uri,
                                                                                  publisher_contact=publisher_contact,
                                                                                  eula=eula,
                                                                                  public_name_prefix=public_name_prefix)
    return sdk_no_wait(no_wait, client.galleries.begin_create_or_update, resource_group_name, gallery_name, gallery)


def sig_share_update(cmd, client, resource_group_name, gallery_name, subscription_ids=None, tenant_ids=None,
                     op_type=None):
    from .vendored_sdks.azure_mgmt_compute.models._models_py3 import SharingProfileGroup, SharingUpdate, SharingProfileGroupTypes
    if op_type != 'EnableCommunity':
        if subscription_ids is None and tenant_ids is None:
            raise RequiredArgumentMissingError('At least one of subscription ids or tenant ids must be provided')
    groups = []
    if subscription_ids:
        groups.append(SharingProfileGroup(type=SharingProfileGroupTypes.SUBSCRIPTIONS, ids=subscription_ids))
    if tenant_ids:
        groups.append(SharingProfileGroup(type=SharingProfileGroupTypes.AAD_TENANTS, ids=tenant_ids))
    sharing_update = SharingUpdate(operation_type=op_type, groups=groups)
    return client.begin_update(resource_group_name=resource_group_name,
                               gallery_name=gallery_name,
                               sharing_update=sharing_update)
