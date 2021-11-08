# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_location_type


def load_arguments(self, _):

    public_gallery_name_type = CLIArgumentType(help='The public name of community gallery.', id_part='child_name_1')

    gallery_image_name_type = CLIArgumentType(
        options_list=['--gallery-image-definition', '-i'],
        help='The name of the community gallery image definition from which the image versions are to be listed.',
        id_part='child_name_2'
    )

    gallery_image_name_version_type = CLIArgumentType(
        options_list=['--gallery-image-version', '-e'],
        help='The name of the gallery image version to be created. Needs to follow semantic version name pattern: '
             'The allowed characters are digit and period. Digits must be within the range of a 32-bit integer. '
             'Format: <MajorVersion>.<MinorVersion>.<Patch>', id_part='child_name_3'
    )

    marker_type = CLIArgumentType(
        help='A string value that identifies the portion of the list of containers to be '
             'returned with the next listing operation. The operation returns the NextMarker value within '
             'the response body if the listing operation did not return all containers remaining to be listed '
             'with the current page. If specified, this generator will begin returning results from the point '
             'where the previous generator stopped.')

    with self.argument_context('sig show-community') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), id_part='name')
        c.argument('public_gallery_name', public_gallery_name_type)

    with self.argument_context('sig image-definition show-community') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), id_part='name')
        c.argument('public_gallery_name', public_gallery_name_type)
        c.argument('gallery_image_name', gallery_image_name_type)

    with self.argument_context('sig image-definition list-community') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), id_part='name')
        c.argument('public_gallery_name', public_gallery_name_type)
        c.argument('marker', arg_type=marker_type)
        c.argument('show_next_marker', action='store_true', help='Show nextMarker in result when specified.')

    with self.argument_context('sig image-version show-community') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), id_part='name')
        c.argument('public_gallery_name', public_gallery_name_type)
        c.argument('gallery_image_name', gallery_image_name_type)
        c.argument('gallery_image_version_name', gallery_image_name_version_type)

    with self.argument_context('sig image-version list-community') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), id_part='name')
        c.argument('public_gallery_name', public_gallery_name_type)
        c.argument('gallery_image_name', gallery_image_name_type)
        c.argument('marker', arg_type=marker_type)
        c.argument('show_next_marker', action='store_true', help='Show nextMarker in result when specified.')
