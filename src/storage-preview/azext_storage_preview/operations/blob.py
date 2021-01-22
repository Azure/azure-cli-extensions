# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

from urllib.parse import quote
from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def set_service_properties(client, parameters, delete_retention=None, days_retained=None, static_website=None,
                           index_document=None, error_document_404_path=None):
    # update
    kwargs = {}
    if any([delete_retention, days_retained]):
        kwargs['delete_retention_policy'] = parameters.delete_retention_policy
    if delete_retention is not None:
        parameters.delete_retention_policy.enabled = delete_retention
    if days_retained is not None:
        parameters.delete_retention_policy.days = days_retained

    if any([static_website, index_document, error_document_404_path]):
        if getattr(parameters, 'static_website', None) is None:
            raise CLIError('Static websites are only supported for StorageV2 (general-purpose v2) accounts.')
        kwargs['static_website'] = parameters.static_website
    if static_website is not None:
        parameters.static_website.enabled = static_website
    if index_document is not None:
        parameters.static_website.index_document = index_document
    if error_document_404_path is not None:
        parameters.static_website.error_document_404_path = error_document_404_path

    # checks
    policy = parameters.delete_retention_policy
    if policy.enabled and not policy.days:
        raise CLIError("must specify days-retained")

    client.set_blob_service_properties(**kwargs)
    return client.get_blob_service_properties()


def show_directory(client, container_name, directory_name, snapshot=None, lease_id=None,
                   if_modified_since=None, if_unmodified_since=None, if_match=None,
                   if_none_match=None, timeout=None):
    directory = client.get_blob_properties(
        container_name, directory_name, snapshot=snapshot, lease_id=lease_id,
        if_modified_since=if_modified_since, if_unmodified_since=if_unmodified_since, if_match=if_match,
        if_none_match=if_none_match, timeout=timeout)

    return directory


def show_blob(cmd, client, container_name, blob_name, snapshot=None, lease_id=None,
              if_modified_since=None, if_unmodified_since=None, if_match=None,
              if_none_match=None, timeout=None):
    blob = client.get_blob_properties(
        container_name, blob_name, snapshot=snapshot, lease_id=lease_id,
        if_modified_since=if_modified_since, if_unmodified_since=if_unmodified_since, if_match=if_match,
        if_none_match=if_none_match, timeout=timeout)

    page_ranges = None
    if blob.properties.blob_type == cmd.get_models('blob.models#_BlobTypes').PageBlob:
        page_ranges = client.get_page_ranges(
            container_name, blob_name, snapshot=snapshot, lease_id=lease_id, if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since, if_match=if_match, if_none_match=if_none_match, timeout=timeout)

    blob.properties.page_ranges = page_ranges

    return blob


# pylint: disable=unused-variable,logging-format-interpolation
def delete_directory(client, container_name, directory_name):

    deleted, marker = client.delete_directory(container_name, directory_name, recursive=True)

    # if HNS is enabled, the delete operation is atomic and no marker is returned
    # if HNS is not enabled, and there are too more files/subdirectories in the directories to be deleted
    # in a single call, the service returns a marker, so that we can follow it and finish deleting
    # the rest of the files/subdirectories
    count = 1
    while marker is not None:
        deleted, marker = client.delete_directory(container_name, directory_name, marker=marker, recursive=True)
        count += 1
    logger.info("Took {} call(s) to finish moving.".format(count))


def list_blobs(client, container_name, prefix=None, num_results=None, include='mc',
               delimiter=None, marker=None, timeout=None):
    client.list_blobs(container_name, prefix, num_results, include,
                      delimiter, marker, timeout)


def list_directory(client, container_name, directory_path, prefix=None, num_results=None, include='mc',
                   delimiter=None, marker=None, timeout=None):
    '''
    :param str container_name:
        Name of existing container.
    :param str prefix:
        Filters the results to return only blobs whose names
        begin with the specified prefix.
    :param int num_results:
        Specifies the maximum number of blobs to return,
        including all :class:`BlobPrefix` elements. If the request does not specify
        num_results or specifies a value greater than 5,000, the server will
        return up to 5,000 items. Setting num_results to a value less than
        or equal to zero results in error response code 400 (Bad Request).
    :param ~azure.storage.blob.models.Include include:
        Specifies one or more additional datasets to include in the response.
    :param str delimiter:
        When the request includes this parameter, the operation
        returns a :class:`~azure.storage.blob.models.BlobPrefix` element in the
        result list that acts as a placeholder for all blobs whose names begin
        with the same substring up to the appearance of the delimiter character.
        The delimiter may be a single character or a string.
    :param str marker:
        An opaque continuation token. This value can be retrieved from the
        next_marker field of a previous generator object if num_results was
        specified and that generator has finished enumerating results. If
        specified, this generator will begin returning results from the point
        where the previous generator stopped.
    :param int timeout:
        The timeout parameter is expressed in seconds.
    '''
    directory_prefix = directory_path + '/' + prefix if prefix else directory_path + '/'
    return client.list_blobs(container_name, directory_prefix, num_results, include,
                             delimiter, marker, timeout)


def rename_directory(client, container_name, new_path, source_path,
                     mode=None, lease_id=None, source_lease_id=None,
                     source_if_modified_since=None, source_if_unmodified_since=None,
                     source_if_match=None, source_if_none_match=None, timeout=None):
    """
     Rename a directory(which can contain other directories or blobs).

     :param str container_name:
         Name of existing container.
     :param str new_path:
         New path for source_path. Ex: 'topdir1/dirsubfoo'.
         Note that the path should be an absolute path under the container.
     :param str source_path:
         Path to be renamed. Ex: 'topdir1/dirbar'.
         Note that the path should be an absolute path under the container.
     :param mode:
         Optional. Valid only when namespace is enabled.
         This parameter determines the behavior of the move operation.
         The value must be "legacy" or "posix", and the default value will be "posix".
         Legacy: if the destination of the move is an existing directory and that directory is empty,
         the source will overwrite the destination. If the directory is not empty, the move will fail.
         Posix: if the destination of the move is an existing empty directory,
         destination will be overwritten. Otherwise, the source will be moved into the destination directory.
         If the destination is an existing file, the file will be overwritten.
     :param str lease_id:
         Optional. A lease ID for the new_path.
         The new_path must have an active lease and the lease ID must match.
     :param str source_lease_id:
         Optional. A lease ID for the source_path.
         The source_path must have an active lease and the lease ID must match.
     :param datetime source_if_modified_since:
         Optional. A date and time value. Specify this header to perform the move operation
         only if the source has been modified since the specified date and time.
     :param datetime source_if_unmodified_since:
         Optional. A date and time value. Specify this header to perform the move operation
         only if the source has not been modified since the specified date and time.
     :param str source_if_match:
         Optional. An ETag value. Specify this header to perform the move operation
         only if the source's ETag matches the value specified.
     :param str source_if_none_match:
         Optional. An ETag value or the special wildcard ("*") value.
         Specify this header to perform the move operation
         only if the source's ETag does not match the value specified.
     :param int timeout:
         The timeout parameter is expressed in seconds.

     """

    # In order to find the required blob, `x-ms-rename-source` in header needs to encode the special character in URL.
    source_path = quote(source_path)

    marker = client.rename_path(container_name, new_path, source_path,
                                mode=mode, lease_id=lease_id, source_lease_id=source_lease_id,
                                source_if_modified_since=source_if_modified_since,
                                source_if_unmodified_since=source_if_unmodified_since,
                                source_if_match=source_if_match, source_if_none_match=source_if_none_match,
                                timeout=timeout)

    # if HNS is enabled, the rename operation is atomic and no marker is returned
    # if HNS is not enabled, and there are too more files/subdirectories in the directories to be renamed
    # in a single call, the service returns a marker, so that we can follow it and finish renaming
    # the rest of the files/subdirectories

    count = 1
    while marker is not None:
        marker = client.rename_path(container_name, new_path, source_path, marker=marker)
        count += 1
    logger.info("Took {} call(s) to finish moving.".format(count))
