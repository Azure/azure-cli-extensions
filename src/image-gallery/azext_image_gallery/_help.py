# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['sig show-community'] = """
type: command
short-summary: Get a gallery that has been community (preview).
long-summary: Get a gallery that has been community (private preview feature, please contact community image gallery team by email sigpmdev@microsoft.com to register for preview if you're interested in using this feature).
examples:
  - name: Get a gallery that has been community in the given location.
    text: |
        az sig show-community --public-gallery-name publicGalleryName --location myLocation
"""

helps['sig image-definition show-community'] = """
type: command
short-summary: Get an image in a gallery community (preview).
long-summary: Get an image in a gallery community (private preview feature, please contact community image gallery team by email sigpmdev@microsoft.com to register for preview if you're interested in using this feature).
examples:
  - name: Get an image definition in a gallery community in the given location.
    text: |
        az sig image-definition show-community --public-gallery-name publicGalleryName \\
        --gallery-image-definition myGalleryImageName --location myLocation
"""

helps['sig image-definition list-community'] = """
type: command
short-summary: List VM Image definitions in a gallery community (preview).
long-summary: List VM Image definitions in a gallery community (private preview feature, please contact community image gallery team by email sigpmdev@microsoft.com to register for preview if you're interested in using this feature).
examples:
  - name: List an image definition in a gallery community.
    text: |
        az sig image-definition list-community --public-gallery-name publicGalleryName \\
        --location myLocation
"""

helps['sig image-version show-community'] = """
type: command
short-summary: Get an image version in a gallery community (preview).
long-summary: Get an image version in a gallery community (private preview feature, please contact community image gallery team by email sigpmdev@microsoft.com to register for preview if you're interested in using this feature).
examples:
  - name: Get an image version in a gallery community in the given location.
    text: |
        az sig image-version show-community --public-gallery-name publicGalleryName \\
        --gallery-image-definition MyImage --gallery-image-version 1.0.0 --location myLocation
"""

helps['sig image-version list-community'] = """
type: command
short-summary: List VM Image Versions in a gallery community (preview).
long-summary: List VM Image Versions in a gallery community (private preview feature, please contact community image gallery team by email sigpmdev@microsoft.com to register for preview if you're interested in using this feature).
examples:
  - name: List an image versions in a gallery community.
    text: |
        az sig image-version list-community --public-gallery-name publicGalleryName \\
        --gallery-image-definition MyImage --location myLocation
"""

helps['sig share enable-community'] = """
type: command
short-summary: Allow to share gallery to the community
examples:
  - name: Allow to share gallery to the community
    text: |
        az sig share enable-community --resource-group MyResourceGroup --gallery-name MyGallery
"""
