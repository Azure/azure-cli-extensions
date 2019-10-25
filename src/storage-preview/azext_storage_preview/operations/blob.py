# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import uuid

from knack.util import CLIError
import os
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

def guess_content_type(file_path, original, settings_class):
    if original.content_encoding or original.content_type:
        return original

    import mimetypes
    mimetypes.add_type('application/json', '.json')
    mimetypes.add_type('application/javascript', '.js')

    content_type, _ = mimetypes.guess_type(file_path)
    return settings_class(
        content_type=content_type,
        content_encoding=original.content_encoding,
        content_disposition=original.content_disposition,
        content_language=original.content_language,
        content_md5=original.content_md5,
        cache_control=original.cache_control)


def upload_blob(cmd, client, container_name, blob_name, file_path, blob_type=None, content_settings=None, metadata=None,
                validate_content=False, maxsize_condition=None, max_connections=2, lease_id=None, tier=None,
                if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None,
                progress_callback=None):
    """Upload a blob to a container."""

    t_content_settings = cmd.get_models('blob.models#ContentSettings')
    content_settings = guess_content_type(file_path, content_settings, t_content_settings)

    def upload_append_blob():
        check_blob_args = {
            'container_name': container_name,
            'blob_name': blob_name,
            'lease_id': lease_id,
            'if_modified_since': if_modified_since,
            'if_unmodified_since': if_unmodified_since,
            'if_match': if_match,
            'if_none_match': if_none_match,
            'timeout': timeout
        }

        if client.exists(container_name, blob_name):
            # used to check for the preconditions as append_blob_from_path() cannot
            client.get_blob_properties(**check_blob_args)
        else:
            client.create_diectory(content_settings=content_settings, metadata=metadata, **check_blob_args)

        append_blob_args = {
            'container_name': container_name,
            'blob_name': blob_name,
            'file_path': file_path,
            'progress_callback': progress_callback,
            'maxsize_condition': maxsize_condition,
            'lease_id': lease_id,
            'timeout': timeout
        }

        if cmd.supported_api_version(min_api='2016-05-31'):
            append_blob_args['validate_content'] = validate_content

        return client.append_blob_from_path(**append_blob_args)

    def upload_block_blob():
        # increase the block size to 100MB when the block list will contain more than 50,000 blocks
        if os.path.isfile(file_path) and os.stat(file_path).st_size > 50000 * 4 * 1024 * 1024:
            client.MAX_BLOCK_SIZE = 100 * 1024 * 1024
            client.MAX_SINGLE_PUT_SIZE = 256 * 1024 * 1024

        create_blob_args = {
            'container_name': container_name,
            'blob_name': blob_name,
            'file_path': file_path,
            'progress_callback': progress_callback,
            'content_settings': content_settings,
            'metadata': metadata,
            'max_connections': max_connections,
            'lease_id': lease_id,
            'if_modified_since': if_modified_since,
            'if_unmodified_since': if_unmodified_since,
            'if_match': if_match,
            'if_none_match': if_none_match,
            'timeout': timeout
        }

        if cmd.supported_api_version(min_api='2017-04-17') and tier:
            create_blob_args['premium_page_blob_tier'] = tier

        if cmd.supported_api_version(min_api='2016-05-31'):
            create_blob_args['validate_content'] = validate_content

        return client.create_blob_from_path(**create_blob_args)

    type_func = {
        'append': upload_append_blob,
        'block': upload_block_blob,
        'page': upload_block_blob  # same implementation
    }
    return type_func[blob_type]()





def delete_directory(client, container_name, directory_name):

    deleted, marker = client.delete_directory(container_name, directory_name, recursive=True)

    # if HNS is enabled, the delete operation is atomic and no marker is returned
    # if HNS is not enabled, and there are too more files/subdirectories in the directories to be deleted
    # in a single call, the service returns a marker, so that we can follow it and finish deleting
    # the rest of the files/subdirectories
    count = 1
    while marker is not None:
        deleted, marker = client.delete_directory(container_name, directory_name,
                                                        marker=marker, recursive=True)
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


def rename_directory(client, container_name, destination_path, source_path):

    marker = client.rename_path(container_name, destination_path, source_path)

    # if HNS is enabled, the rename operation is atomic and no marker is returned
    # if HNS is not enabled, and there are too more files/subdirectories in the directories to be renamed
    # in a single call, the service returns a marker, so that we can follow it and finish renaming
    # the rest of the files/subdirectories

    count = 1
    while marker is not None:
        marker = client.rename_path(container_name, destination_path, source_path, marker=marker)
        count += 1
    logger.info("Took {} call(s) to finish moving.".format(count))


def _create_blobs(client, container_name, destination_path,
        source_path, num_of_blobs):
    import concurrent.futures
    import itertools
    # Use a thread pool because it is too slow otherwise
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        def create_blob(blob_name):
            # generate a random name


            # create a blob under the directory
            # blob_service.create_blob_from_bytes(container_name, blob_name, b"test")
            client.create_directory(container_name, blob_name)

        futures = {executor.submit(create_blob) for _ in itertools.repeat(None, num_of_blobs)}
        concurrent.futures.wait(futures)
        print("Created {} blobs under the directory: {}".format(num_of_blobs, destination_path))




def set_entry(client, container_name, path, acl, lease_id=None, if_modified_since=None, if_unmodified_since=None,
              if_match=None, if_none_match=None, timeout=None):
    acl_list = client.get_path_access_control(container_name, path)

    client.set_path_access_control(container_name, path, acl_list.owner, acl_list.group, acl_list.permissions, acl,
                                   lease_id, if_modified_since, if_unmodified_since, if_match, if_none_match, timeout)