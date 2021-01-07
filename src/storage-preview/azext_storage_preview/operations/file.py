# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from knack.log import get_logger


def storage_file_upload(client, local_file_path, content_settings=None,
                        metadata=None, validate_content=False, progress_callback=None, max_connections=2, timeout=None):

    upload_args = {
        'content_settings': content_settings,
        'metadata': metadata,
        'validate_content': validate_content,
        'max_concurrency': max_connections,
        'timeout': timeout
    }

    if progress_callback:
        upload_args['raw_response_hook'] = progress_callback

    # Because the contents of the uploaded file may be too large, it should be passed into the a stream object,
    # upload_file() read file data in batches to avoid OOM problems
    count = os.path.getsize(local_file_path)
    with open(local_file_path, 'rb') as stream:
        response = client.upload_file(data=stream, length=count, **upload_args)

    return response


def storage_file_upload_batch(cmd, client, destination, source, destination_path=None, pattern=None, dryrun=False,
                              validate_content=False, content_settings=None, max_connections=1, metadata=None,
                              progress_callback=None):
    """ Upload local files to Azure Storage File Share in batch """

    from ..util import glob_files_locally, normalize_blob_file_path, guess_content_type
    from ..track2_util import make_file_url

    source_files = [c for c in glob_files_locally(source, pattern)]
    logger = get_logger(__name__)
    settings_class = cmd.get_models('_models#ContentSettings')

    if dryrun:
        logger.info('upload files to file share')
        logger.info('    account %s', client.account_name)
        logger.info('      share %s', destination)
        logger.info('      total %d', len(source_files))
        return [{'File': make_file_url(client, os.path.dirname(dst) or None, os.path.basename(dst)),
                 'Type': guess_content_type(src, content_settings, settings_class).content_type} for src, dst in
                source_files]

    # TODO: Performance improvement
    # 1. Upload files in parallel
    def _upload_action(src, dst):
        dst = normalize_blob_file_path(destination_path, dst)
        dir_name = os.path.dirname(dst)
        file_name = os.path.basename(dst)

        _make_directory_in_files_share(client, dir_name)

        logger.warning('uploading %s', src)

        storage_file_upload(client.get_file_client(dst), src, content_settings, metadata, validate_content,
                            progress_callback, max_connections)

        return make_file_url(client, dir_name, file_name)

    return list(_upload_action(src, dst) for src, dst in source_files)


def _make_directory_in_files_share(share_client, directory_path, existing_dirs=None):
    """
    Create directories recursively.
    This method accept a existing_dirs set which serves as the cache of existing directory. If the
    parameter is given, the method will search the set first to avoid repeatedly create directory
    which already exists.
    """
    from azure.common import AzureHttpError
    from azure.core.exceptions import ResourceExistsError

    if not directory_path:
        return

    parents = [directory_path]
    p = os.path.dirname(directory_path)
    while p:
        parents.append(p)
        p = os.path.dirname(p)

    for dir_name in reversed(parents):
        if existing_dirs and (dir_name in existing_dirs):
            continue

        try:
            share_client.get_directory_client(directory_path=dir_name).create_directory()
        except ResourceExistsError:
            pass
        except AzureHttpError:
            from knack.util import CLIError
            raise CLIError('Failed to create directory {}'.format(dir_name))

        if existing_dirs:
            existing_dirs.add(directory_path)
