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
