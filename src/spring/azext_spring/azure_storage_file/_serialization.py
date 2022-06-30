# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.common._common_conversion import _str
from azure.storage.common._error import (
    _validate_not_none,
    _ERROR_START_END_NEEDED_FOR_MD5,
    _ERROR_RANGE_TOO_LARGE_FOR_MD5,
)
_ERROR_TOO_MANY_FILE_PERMISSIONS = 'file_permission and file_permission_key should not be set at the same time'
_FILE_PERMISSION_TOO_LONG = 'Size of file_permission is too large. file_permission should be <=8KB, else' \
                            'please use file_permission_key'


def _get_path(share_name=None, directory_name=None, file_name=None):
    '''
    Creates the path to access a file resource.

    share_name:
        Name of share.
    directory_name:
        The path to the directory.
    file_name:
        Name of file.
    '''
    if share_name and directory_name and file_name:
        return '/{0}/{1}/{2}'.format(
            _str(share_name),
            _str(directory_name),
            _str(file_name))
    if share_name and directory_name:
        return '/{0}/{1}'.format(
            _str(share_name),
            _str(directory_name))
    if share_name and file_name:
        return '/{0}/{1}'.format(
            _str(share_name),
            _str(file_name))
    if share_name:
        return '/{0}'.format(_str(share_name))

    return '/'


def _validate_and_format_range_headers(request, start_range, end_range, start_range_required=True,
                                       end_range_required=True, check_content_md5=False, is_source=False):
    # If end range is provided, start range must be provided
    if start_range_required or end_range is not None:
        _validate_not_none('start_range', start_range)
    if end_range_required:
        _validate_not_none('end_range', end_range)

    # Format based on whether end_range is present
    request.headers = request.headers or {}
    header_name = 'x-ms-source-range' if is_source else 'x-ms-range'
    if end_range is not None:
        request.headers[header_name] = 'bytes={0}-{1}'.format(
            start_range, end_range)
    elif start_range is not None:
        request.headers[header_name] = 'bytes={0}-'.format(start_range)

    # Content MD5 can only be provided for a complete range less than 4MB in size
    if check_content_md5:
        if start_range is None or end_range is None:
            raise ValueError(_ERROR_START_END_NEEDED_FOR_MD5)
        if end_range - start_range > 4 * 1024 * 1024:
            raise ValueError(_ERROR_RANGE_TOO_LARGE_FOR_MD5)

        request.headers['x-ms-range-get-content-md5'] = 'true'


def _validate_and_return_file_permission(file_permission, file_permission_key, default_permission):
    # if file_permission and file_permission_key are both empty, then use the default_permission
    # value as file permission, file_permission size should be <= 8KB, else file permission_key should be used
    empty_file_permission = file_permission is None or len(
        file_permission) == 0
    empty_file_permission_key = file_permission_key is None or len(
        file_permission_key) == 0
    file_permission_size_too_big = False if file_permission is None \
        else len(str(file_permission).encode('utf-8')) > 8 * 1024

    if file_permission_size_too_big:
        raise ValueError(_FILE_PERMISSION_TOO_LONG)

    if empty_file_permission:
        if empty_file_permission_key:
            return default_permission
        return None

    if empty_file_permission_key:
        return file_permission

    raise ValueError(_ERROR_TOO_MANY_FILE_PERMISSIONS)
