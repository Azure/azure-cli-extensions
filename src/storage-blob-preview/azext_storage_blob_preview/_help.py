# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['storage blob copy start'] = """
type: command
short-summary: Start a copy blob job.
parameters:
  - name: --source-uri -u
    type: string
    short-summary: >
        A URL of up to 2 KB in length that specifies an Azure file or blob.
        The value should be URL-encoded as it would appear in a request URI.
        If the source is in another account, the source must either be public
        or must be authenticated via a shared access signature. If the source
        is public, no authentication is required.
        Examples:
        `https://myaccount.blob.core.windows.net/mycontainer/myblob`,
        `https://myaccount.blob.core.windows.net/mycontainer/myblob?snapshot=<DateTime>`,
        `https://otheraccount.blob.core.windows.net/mycontainer/myblob?sastoken`
  - name: --destination-if-modified-since
    type: string
    short-summary: >
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only
        if the destination blob has been modified since the specified date/time.
        If the destination blob has not been modified, the Blob service returns
        status code 412 (Precondition Failed).
  - name: --destination-if-unmodified-since
    type: string
    short-summary: >
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only
        if the destination blob has not been modified since the specified
        date/time. If the destination blob has been modified, the Blob service
        returns status code 412 (Precondition Failed).
  - name: --source-if-modified-since
    type: string
    short-summary: >
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only if the source
        blob has been modified since the specified date/time.
  - name: --source-if-unmodified-since
    type: string
    short-summary: >
        A DateTime value. Azure expects the date value passed in to be UTC.
        If timezone is included, any non-UTC datetimes will be converted to UTC.
        If a date is passed in without timezone info, it is assumed to be UTC.
        Specify this conditional header to copy the blob only if the source blob
        has not been modified since the specified date/time.
examples:
  - name: Copy a blob asynchronously. Use `az storage blob show` to check the status of the blobs.
    text: |
        az storage blob copy start --account-key 00000000 --account-name MyAccount --destination-blob MyDestinationBlob --destination-container MyDestinationContainer --source-uri https://storage.blob.core.windows.net/photos
  - name: Copy a blob asynchronously. Use `az storage blob show` to check the status of the blobs.
    text: |
        az storage blob copy start --account-name MyAccount --destination-blob MyDestinationBlob --destination-container MyDestinationContainer --sas-token $sas --source-uri https://storage.blob.core.windows.net/photos
"""

helps['storage blob filter'] = """
type: command
short-summary: List blobs across all containers whose tags match a given search expression.
parameters:
  - name: --tag-filter
    short-summary: >
            The expression to find blobs whose tags matches the specified condition.
            eg. ""yourtagname"='firsttag' and "yourtagname2"='secondtag'"
"""

helps['storage blob tag'] = """
type: group
short-summary: Manage blob tags.
"""

helps['storage blob tag list'] = """
type: command
short-summary: Get tags on a blob or specific blob version, or snapshot.
"""

helps['storage blob tag set'] = """
type: command
short-summary: Set tags on a blob or specific blob version, but not snapshot.
long-summary: >
    Each call to this operation replaces all existing tags attached to the blob. To remove all
    tags from the blob, call this operation with no tags set.
"""
