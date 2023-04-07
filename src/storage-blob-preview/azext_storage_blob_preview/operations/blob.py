# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import os
from datetime import datetime, timedelta

from azure.cli.core.profiles import get_sdk
from azure.cli.core.util import sdk_no_wait
from azure.cli.command_modules.storage.url_quote_util import make_encoded_file_url_and_params
from knack.log import get_logger
from knack.util import CLIError

from .._transformers import transform_response_with_bytearray
from ..util import (create_file_share_from_storage_client,
                    create_short_lived_share_sas,
                    filter_none, collect_blobs, collect_blob_objects, collect_files,
                    mkdir_p, guess_content_type, normalize_blob_file_path,
                    check_precondition_success)
from ..profiles import CUSTOM_DATA_STORAGE_BLOB

logger = get_logger(__name__)


def delete_container(client, container_name, fail_not_exist=False, lease_id=None, if_modified_since=None,
                     if_unmodified_since=None, timeout=None, bypass_immutability_policy=False,
                     processed_resource_group=None, processed_account_name=None, mgmt_client=None):
    if bypass_immutability_policy:
        return mgmt_client.blob_containers.delete(processed_resource_group, processed_account_name, container_name)
    return client.delete_container(
        container_name, fail_not_exist=fail_not_exist, lease_id=lease_id, if_modified_since=if_modified_since,
        if_unmodified_since=if_unmodified_since, timeout=timeout)


def restore_blob_ranges(cmd, client, resource_group_name, account_name, time_to_restore, blob_ranges=None,
                        no_wait=False):

    if blob_ranges is None:
        BlobRestoreRange = cmd.get_models("BlobRestoreRange")
        blob_ranges = [BlobRestoreRange(start_range="", end_range="")]

    return sdk_no_wait(no_wait, client.restore_blob_ranges, resource_group_name=resource_group_name,
                       account_name=account_name, time_to_restore=time_to_restore, blob_ranges=blob_ranges)


def set_blob_tier(client, container_name, blob_name, tier, blob_type='block', timeout=None):
    if blob_type == 'block':
        return client.set_standard_blob_tier(container_name=container_name, blob_name=blob_name,
                                             standard_blob_tier=tier, timeout=timeout)
    if blob_type == 'page':
        return client.set_premium_page_blob_tier(container_name=container_name, blob_name=blob_name,
                                                 premium_page_blob_tier=tier, timeout=timeout)
    raise ValueError('Blob tier is only applicable to block or page blob.')


def set_delete_policy(client, enable=None, days_retained=None):
    policy = client.get_service_properties()['delete_retention_policy']

    if enable is not None:
        policy.enabled = enable == 'true'
    if days_retained is not None:
        policy.days = days_retained

    if policy.enabled and not policy.days:
        raise CLIError("must specify days-retained")

    client.set_service_properties(delete_retention_policy=policy)
    return client.get_service_properties()['delete_retention_policy']


def set_service_properties(client, delete_retention=None, delete_retention_period=None,
                           static_website=None, index_document=None, error_document_404_path=None,
                           default_index_document_path=None, timeout=None):
    properties = client.get_service_properties()

    # update
    if delete_retention is not None:
        properties['delete_retention_policy'].enabled = delete_retention
    if delete_retention_period is not None:
        properties['delete_retention_policy'].days = delete_retention_period

    if static_website is not None:
        properties['static_website'].enabled = static_website
    if index_document is not None:
        properties['static_website'].index_document = index_document
    if error_document_404_path is not None:
        properties['static_website'].error_document404_path = error_document_404_path
    if default_index_document_path is not None:
        properties['static_website'].default_index_document_path = default_index_document_path
    policy = properties.get('delete_retention_policy', None)
    if policy and policy.enabled and not policy.days:
        raise CLIError("must specify days-retained")

    client.set_service_properties(timeout=timeout, **properties)
    return client.get_service_properties()


def set_blob_immutability_policy(cmd, client, expiry_time=None, policy_mode=None, **kwargs):
    ImmutabilityPolicy = cmd.get_models("_models#ImmutabilityPolicy", resource_type=CUSTOM_DATA_STORAGE_BLOB)
    if not expiry_time and not policy_mode:
        from azure.cli.core.azclierror import InvalidArgumentValueError
        raise InvalidArgumentValueError('Please specify --expiry-time | --policy-mode')
    immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time, policy_mode=policy_mode)
    return client.set_immutability_policy(immutability_policy=immutability_policy, **kwargs)


def storage_blob_copy_batch(cmd, client, source_client, container_name=None,
                            destination_path=None, source_container=None, source_share=None,
                            source_sas=None, pattern=None, dryrun=False, source_account_name=None,
                            source_account_key=None):
    """Copy a group of blob or files to a blob container."""
    if dryrun:
        logger.warning('copy files or blobs to blob container')
        logger.warning('    account %s', client.account_name)
        logger.warning('  container %s', container_name)
        logger.warning('     source %s', source_container or source_share)
        logger.warning('source type %s', 'blob' if source_container else 'file')
        logger.warning('    pattern %s', pattern)
        logger.warning(' operations')

    if source_container:
        # copy blobs for blob container
        if source_account_name != client.account_name:
            from .._client_factory import cf_blob_service
            account_kwargs = {'account_name': source_account_name,
                              'account_key': source_account_key,
                              'sas_token': source_sas}
            source_client = cf_blob_service(cmd.cli_ctx, account_kwargs)
        else:
            source_client = client

        # pylint: disable=inconsistent-return-statements
        def action_blob_copy(blob_name):
            if dryrun:
                logger.warning('  - copy blob %s', blob_name)
            else:
                return _copy_blob_to_blob_container(cmd, blob_service=client, source_blob_service=source_client,
                                                    destination_container=container_name,
                                                    destination_path=destination_path,
                                                    source_container=source_container,
                                                    source_blob_name=blob_name,
                                                    source_sas=source_sas)

        return list(filter_none(action_blob_copy(blob) for blob in collect_blobs(source_client,
                                                                                 source_container,
                                                                                 pattern)))

    if source_share:
        # copy blob from file share

        # if the source client is None, recreate one from the destination client.
        source_client = source_client or create_file_share_from_storage_client(cmd, account_name=source_account_name,
                                                                               account_key=source_account_key,
                                                                               sas_token=source_sas)

        if not source_sas:
            source_sas = create_short_lived_share_sas(cmd, source_client.account_name, source_client.account_key,
                                                      source_share)

        # pylint: disable=inconsistent-return-statements
        def action_file_copy(file_info):
            dir_name, file_name = file_info
            if dryrun:
                logger.warning('  - copy file %s', os.path.join(dir_name, file_name))
            else:
                return _copy_file_to_blob_container(client, source_client, container_name, destination_path,
                                                    source_share, source_sas, dir_name, file_name)

        return list(filter_none(action_file_copy(file) for file in collect_files(cmd,
                                                                                 source_client,
                                                                                 source_share,
                                                                                 pattern)))
    raise ValueError('Fail to find source. Neither blob container or file share is specified')


# pylint: disable=unused-argument, too-many-locals
def storage_blob_download_batch(client, source, destination, container_name, pattern=None, dryrun=False,
                                progress_callback=None, socket_timeout=None, **kwargs):
    source_blobs = collect_blobs(client, container_name, pattern)
    blobs_to_download = {}
    for blob_name in source_blobs:
        # remove starting path seperator and normalize
        normalized_blob_name = normalize_blob_file_path(None, blob_name)
        if normalized_blob_name in blobs_to_download:
            raise CLIError('Multiple blobs with download path: `{}`. As a solution, use the `--pattern` parameter '
                           'to select for a subset of blobs to download OR utilize the `storage blob download` '
                           'command instead to download individual blobs.'.format(normalized_blob_name))
        blobs_to_download[normalized_blob_name] = blob_name

    results = []
    if dryrun:
        # download_blobs = _blob_precondition_check(source_blobs, if_modified_since=if_modified_since,
        #                                           if_unmodified_since=if_unmodified_since)
        logger.warning('download action: from %s to %s', source, destination)
        logger.warning('    pattern %s', pattern)
        logger.warning('  container %s', container_name)
        logger.warning('      total %d', len(source_blobs))
        logger.warning(' operations')
        for b in source_blobs:
            logger.warning('  - %s', b)

    else:
        @check_precondition_success
        def _download_blob(*args, **kwargs):
            blob = download_blob(*args, **kwargs)
            return blob.name

        # Tell progress reporter to reuse the same hook
        if progress_callback:
            progress_callback.reuse = True

        for index, blob_normed in enumerate(blobs_to_download):
            from azure.cli.core.azclierror import FileOperationError
            # add blob name and number to progress message
            if progress_callback:
                progress_callback.message = '{}/{}: "{}"'.format(
                    index + 1, len(blobs_to_download), blobs_to_download[blob_normed])
            blob_client = client.get_blob_client(container=container_name,
                                                 blob=blobs_to_download[blob_normed])
            destination_path = os.path.join(destination, os.path.normpath(blob_normed))
            destination_folder = os.path.dirname(destination_path)
            # Failed when there is same name for file and folder
            if os.path.isfile(destination_path) and os.path.exists(destination_folder):
                raise FileOperationError("%s already exists in %s. Please rename existing file or choose another "
                                         "destination folder. ")
            if not os.path.exists(destination_folder):
                mkdir_p(destination_folder)
            include, result = _download_blob(client=blob_client, file_path=destination_path,
                                             progress_callback=progress_callback, **kwargs)
            if include:
                results.append(result)

        # end progress hook
        if progress_callback:
            progress_callback.hook.end()
        num_failures = len(blobs_to_download) - len(results)
        if num_failures:
            logger.warning('%s of %s files not downloaded due to "Failed Precondition"',
                           num_failures, len(blobs_to_download))
    return results


def storage_blob_upload_batch(cmd, client, source, destination, pattern=None,  # pylint: disable=too-many-locals
                              source_files=None, destination_path=None,
                              container_name=None, blob_type=None,
                              content_settings=None, metadata=None, validate_content=False,
                              maxsize_condition=None, max_connections=2, lease_id=None, progress_callback=None,
                              if_modified_since=None, if_unmodified_since=None, if_match=None,
                              if_none_match=None, timeout=None, dryrun=False, socket_timeout=None, **kwargs):
    def _create_return_result(blob_content_settings, upload_result=None):
        return {
            'Blob': client.url,
            'Type': blob_content_settings.content_type,
            'Last Modified': upload_result['last_modified'] if upload_result else None,
            'eTag': upload_result['etag'] if upload_result else None}

    source_files = source_files or []
    t_content_settings = cmd.get_models('_models#ContentSettings', resource_type=cmd.command_kwargs['resource_type'])

    results = []
    if dryrun:
        logger.info('upload action: from %s to %s', source, destination)
        logger.info('    pattern %s', pattern)
        logger.info('  container %s', container_name)
        logger.info('       type %s', blob_type)
        logger.info('      total %d', len(source_files))
        results = []
        for src, dst in source_files:
            results.append(_create_return_result(blob_content_settings=guess_content_type(src, content_settings,
                                                                                          t_content_settings)))
    else:
        @check_precondition_success
        def _upload_blob(*args, **kwargs):
            return upload_blob(*args, **kwargs)

        # Tell progress reporter to reuse the same hook
        if progress_callback:
            progress_callback.reuse = True

        for index, source_file in enumerate(source_files):
            src, dst = source_file
            # logger.warning('uploading %s', src)
            guessed_content_settings = guess_content_type(src, content_settings, t_content_settings)

            # add blob name and number to progress message
            if progress_callback:
                progress_callback.message = '{}/{}: "{}"'.format(
                    index + 1, len(source_files), normalize_blob_file_path(destination_path, dst))
            blob_client = client.get_blob_client(container=container_name,
                                                 blob=normalize_blob_file_path(destination_path, dst))
            include, result = _upload_blob(cmd, blob_client, file_path=src,
                                           blob_type=blob_type, content_settings=guessed_content_settings,
                                           metadata=metadata, validate_content=validate_content,
                                           maxsize_condition=maxsize_condition, max_connections=max_connections,
                                           lease_id=lease_id, progress_callback=progress_callback,
                                           if_modified_since=if_modified_since,
                                           if_unmodified_since=if_unmodified_since, if_match=if_match,
                                           if_none_match=if_none_match, timeout=timeout, **kwargs)
            if include:
                results.append(_create_return_result(blob_content_settings=guessed_content_settings,
                                                     upload_result=result))
        # end progress hook
        if progress_callback:
            progress_callback.hook.end()
        num_failures = len(source_files) - len(results)
        if num_failures:
            logger.warning('%s of %s files not uploaded due to "Failed Precondition"', num_failures, len(source_files))
    return results


def transform_blob_type(cmd, blob_type):
    """
    get_blob_types() will get ['block', 'page', 'append']
    transform it to BlobType in track2
    """
    BlobType = cmd.get_models('_models#BlobType', resource_type=CUSTOM_DATA_STORAGE_BLOB)
    if blob_type == 'block':
        return BlobType.BlockBlob
    if blob_type == 'page':
        return BlobType.PageBlob
    if blob_type == 'append':
        return BlobType.AppendBlob
    return None


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


def _blob_precondition_check(source_blobs, if_modified_since=None, if_unmodified_since=None):
    from datetime import timezone
    if_modified_since_utc = if_modified_since.replace(tzinfo=timezone.utc) if if_modified_since else None
    if_unmodified_since_utc = if_unmodified_since.replace(tzinfo=timezone.utc) if if_unmodified_since else None
    result = []
    for blob in source_blobs:
        if not if_modified_since or blob[1].last_modified >= if_modified_since_utc:
            if not if_unmodified_since or blob[1].last_modified <= if_unmodified_since_utc:
                result.append(blob[0])
    return result


def storage_blob_delete_batch(client, source, container_name, pattern=None, lease_id=None,
                              delete_snapshots=None, if_modified_since=None, if_unmodified_since=None, if_match=None,
                              if_none_match=None, timeout=None, dryrun=False, **kwargs):
    @check_precondition_success
    def _delete_blob(blob_name):
        blob_client = client.get_blob_client(container=container_name, blob=blob_name)
        delete_blob_args = {
            'lease': lease_id,
            'delete_snapshots': delete_snapshots,
            'if_modified_since': if_modified_since,
            'if_unmodified_since': if_unmodified_since,
            'if_match': if_match,
            'if_none_match': if_none_match,
            'timeout': timeout
        }
        return blob_client.delete_blob(**delete_blob_args)

    source_blobs = list(collect_blob_objects(client, container_name, pattern))

    if dryrun:
        delete_blobs = _blob_precondition_check(source_blobs, if_modified_since=if_modified_since,
                                                if_unmodified_since=if_unmodified_since)
        logger.warning('delete action: from %s', source)
        logger.warning('    pattern %s', pattern)
        logger.warning('  container %s', container_name)
        logger.warning('      total %d', len(delete_blobs))
        logger.warning(' operations')
        for blob in delete_blobs:
            logger.warning('  - %s', blob)
        return []

    results = [result for include, result in (_delete_blob(blob[0]) for blob in source_blobs) if include]
    num_failures = len(source_blobs) - len(results)
    if num_failures:
        logger.warning('%s of %s blobs not deleted due to "Failed Precondition"', num_failures, len(source_blobs))


def generate_container_shared_access_signature(client, container_name, permission=None,
                                               expiry=None, start=None, id=None, ip=None,  # pylint: disable=redefined-builtin
                                               protocol=None, cache_control=None, content_disposition=None,
                                               content_encoding=None, content_language=None,
                                               content_type=None, as_user=False):
    user_delegation_key = None
    if as_user:
        user_delegation_key = client.get_user_delegation_key(
            _get_datetime_from_string(start) if start else datetime.utcnow(), _get_datetime_from_string(expiry))

    return client.generate_container_shared_access_signature(
        container_name, permission=permission, expiry=expiry, start=start, id=id, ip=ip,
        protocol=protocol, cache_control=cache_control, content_disposition=content_disposition,
        content_encoding=content_encoding, content_language=content_language, content_type=content_type,
        user_delegation_key=user_delegation_key)


def create_blob_url(client, container_name, blob_name, protocol=None, snapshot=None):
    return client.make_blob_url(
        container_name, blob_name, protocol=protocol, snapshot=snapshot, sas_token=client.sas_token)


def _copy_blob_to_blob_container(cmd, blob_service, source_blob_service, destination_container, destination_path,
                                 source_container, source_blob_name, source_sas):
    from azure.core.exceptions import HttpResponseError
    t_blob_client = cmd.get_models('_blob_client#BlobClient', resource_type=CUSTOM_DATA_STORAGE_BLOB)
    source_client = t_blob_client(account_url=source_blob_service.url, container_name=source_container,
                                  blob_name=source_blob_name, credential=source_sas)
    source_blob_url = source_client.url

    destination_blob_name = normalize_blob_file_path(destination_path, source_blob_name)
    try:
        blob_client = blob_service.get_blob_client(container=destination_container, blob=destination_blob_name)
        blob_client.start_copy_from_url(source_url=source_blob_url, incremental_copy=False)
        return blob_client.url
    except HttpResponseError as ex:
        error_template = 'Failed to copy blob {} to container {}. {}'
        raise CLIError(error_template.format(source_blob_name, destination_container, ex))


def _copy_file_to_blob_container(blob_service, source_file_service, destination_container, destination_path,
                                 source_share, source_sas, source_file_dir, source_file_name):
    from azure.core.exceptions import HttpResponseError
    file_url, source_file_dir, source_file_name = \
        make_encoded_file_url_and_params(source_file_service, source_share, source_file_dir,
                                         source_file_name, source_sas)

    source_path = os.path.join(source_file_dir, source_file_name) if source_file_dir else source_file_name
    destination_blob_name = normalize_blob_file_path(destination_path, source_path)

    try:
        blob_client = blob_service.get_blob_client(container=destination_container, blob=destination_blob_name)
        blob_client.start_copy_from_url(source_url=file_url, incremental_copy=False)
        return blob_client.url
    except HttpResponseError as ex:
        error_template = 'Failed to copy file {} to container {}. {}'
        raise CLIError(error_template.format(source_file_name, destination_container, ex))


def _get_datetime_from_string(dt_str):
    accepted_date_formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%MZ',
                             '%Y-%m-%dT%HZ', '%Y-%m-%d']
    for form in accepted_date_formats:
        try:
            return datetime.strptime(dt_str, form)
        except ValueError:
            continue
    raise ValueError("datetime string '{}' not valid. Valid example: 2000-12-31T12:59:59Z".format(dt_str))


def copy_blob(cmd, client, source_url, metadata=None, **kwargs):
    if not kwargs['requires_sync']:
        kwargs.pop('requires_sync')
    blob_type = kwargs.pop('destination_blob_type', None)
    src_client = kwargs.pop('source_client', None)
    if src_client is None:
        src_client = client.from_blob_url(source_url)
        if src_client.account_name == client.account_name:
            src_client = client.from_blob_url(source_url, credential=client.credential)
    StandardBlobTier = cmd.get_models('_models#StandardBlobTier', resource_type=CUSTOM_DATA_STORAGE_BLOB)
    if blob_type is not None and blob_type != 'Detect':
        blob_service_client = src_client._get_container_client()._get_blob_service_client()
        if blob_service_client.credential is not None:
            as_user = True
            if hasattr(blob_service_client.credential, 'account_key'):
                as_user = False
            expiry = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')
            source_url = generate_sas_blob_uri(cmd, blob_service_client, full_uri=True, blob_url=source_url,
                                               blob_name=None, container_name=None, as_user=as_user,
                                               expiry=expiry, permission='r')

        params = {"source_if_modified_since": kwargs.get("source_if_modified_since"),
                  "source_if_unmodified_since": kwargs.get("source_if_unmodified_since"),
                  "if_modified_since": kwargs.get("if_modified_since"),
                  "if_unmodified_since": kwargs.get("if_unmodified_since"),
                  "timeout": kwargs.get("timeout")}

        if blob_type == 'AppendBlob':
            params.update({"lease": kwargs.get("destination_lease")})
            client.create_append_blob()
            res = client.append_block_from_url(copy_source_url=source_url, **params)
            return transform_response_with_bytearray(res)
        if blob_type == 'BlockBlob':
            standard_blob_tier = getattr(StandardBlobTier, (kwargs.get("tier"))) if (kwargs.get("tier")) else None
            params.update({"overwrite": True, "tags": kwargs.get("tags"),
                           "destination_lease": kwargs.get("destination_lease"),
                           "standard_blob_tier": standard_blob_tier})
            return client.upload_blob_from_url(source_url=source_url, **params)
        if blob_type == 'PageBlob':
            params.update({"lease": kwargs.get("destination_lease")})
            source_blob_client = client.from_blob_url(source_url)
            blob_length = source_blob_client.get_blob_properties().size
            if blob_length % 512 != 0:
                raise ValueError("Source blob size must be an integer that aligns with 512 page size")
            client.create_page_blob(size=blob_length)
            res = client.upload_pages_from_url(source_url=source_url, offset=0, length=blob_length,
                                               source_offset=0, **params)
            return transform_response_with_bytearray(res)
    if kwargs.get('tier') is not None:
        tier = kwargs.pop('tier')
        try:
            kwargs["standard_blob_tier"] = getattr(StandardBlobTier, tier)
        except AttributeError:
            PremiumPageBlobTier = cmd.get_models('_models#PremiumPageBlobTier', resource_type=CUSTOM_DATA_STORAGE_BLOB)
            kwargs["premium_page_blob_tier"] = getattr(PremiumPageBlobTier, tier)
    return client.start_copy_from_url(source_url=source_url, metadata=metadata, incremental_copy=False, **kwargs)


def download_blob(client, file_path, open_mode='wb', progress_callback=None, socket_timeout=None, **kwargs):
    if progress_callback:
        kwargs['raw_response_hook'] = progress_callback
    download_stream = client.download_blob(**kwargs)
    with open(file_path, open_mode) as stream:
        download_stream.readinto(stream)
    return client.get_blob_properties()


def generate_sas_blob_uri(cmd, client, container_name, blob_name, permission=None,
                          expiry=None, start=None, id=None, ip=None,  # pylint: disable=redefined-builtin
                          protocol=None, cache_control=None, content_disposition=None,
                          content_encoding=None, content_language=None,
                          content_type=None, full_uri=False, as_user=False, snapshot=None, version_id=None, **kwargs):
    from ..url_quote_util import encode_url_path, encode_for_url
    generate_blob_sas = get_sdk(cmd.cli_ctx, CUSTOM_DATA_STORAGE_BLOB, '_shared_access_signature#generate_blob_sas')
    t_blob_client = get_sdk(cmd.cli_ctx, CUSTOM_DATA_STORAGE_BLOB, '_blob_client#BlobClient')

    sas_kwargs = {}
    if as_user:
        sas_kwargs['user_delegation_key'] = client.get_user_delegation_key(
            _get_datetime_from_string(start) if start else datetime.utcnow(),
            _get_datetime_from_string(expiry))
    else:
        sas_kwargs['account_key'] = client.credential.account_key

    blob_url = kwargs.pop('blob_url', None)
    if blob_url:
        credential = sas_kwargs.get('user_delegation_key', None) or sas_kwargs.get('account_key', None)
        blob_client = t_blob_client.from_blob_url(blob_url=blob_url, credential=credential, snapshot=snapshot)
        container_name = blob_client.container_name
        blob_name = blob_client.blob_name

    sas_token = generate_blob_sas(account_name=client.account_name, container_name=container_name, blob_name=blob_name,
                                  snapshot=snapshot, version_id=version_id, permission=permission,
                                  expiry=expiry, start=start, policy_id=id, ip=ip, protocol=protocol,
                                  cache_control=cache_control, content_disposition=content_disposition,
                                  content_encoding=content_encoding, content_language=content_language,
                                  content_type=content_type, **sas_kwargs)

    if full_uri:
        blob_client = t_blob_client(account_url=client.url, container_name=container_name,
                                    blob_name=blob_name, snapshot=snapshot, credential=sas_token)
        return encode_url_path(blob_client.url, safe='&%()$=\',~')

    return encode_for_url(sas_token, safe='&%()$=\',~')


def generate_sas_container_uri(client, cmd, container_name, permission=None,
                               expiry=None, start=None, id=None, ip=None,  # pylint: disable=redefined-builtin
                               protocol=None, cache_control=None, content_disposition=None,
                               content_encoding=None, content_language=None,
                               content_type=None, full_uri=False, as_user=False):
    generate_container_sas = cmd.get_models('_shared_access_signature#generate_container_sas')

    sas_kwargs = {}
    if as_user:
        sas_kwargs['user_delegation_key'] = client.get_user_delegation_key(
            _get_datetime_from_string(start) if start else datetime.utcnow(),
            _get_datetime_from_string(expiry))
    else:
        sas_kwargs['account_key'] = client.credential.account_key
    sas_token = generate_container_sas(account_name=client.account_name, container_name=container_name,
                                       permission=permission, expiry=expiry, start=start, policy_id=id,
                                       ip=ip, protocol=protocol,
                                       cache_control=cache_control, content_disposition=content_disposition,
                                       content_encoding=content_encoding, content_language=content_language,
                                       content_type=content_type, **sas_kwargs)

    if full_uri:
        t_container_client = cmd.get_models('_container_client#ContainerClient')
        container_client = t_container_client(account_url=client.url, container_name=container_name,
                                              credential=sas_token)
        return container_client.url

    return sas_token


def list_containers(client, include_metadata=False, include_deleted=False, marker=None,
                    num_results=None, prefix=None, show_next_marker=None, **kwargs):
    from ..track2_util import list_generator

    generator = client.list_containers(name_starts_with=prefix, include_metadata=include_metadata,
                                       include_deleted=include_deleted, results_per_page=num_results, **kwargs)

    pages = generator.by_page(continuation_token=marker)  # ContainerPropertiesPaged
    result = list_generator(pages=pages, num_results=num_results)

    if show_next_marker:
        next_marker = {"nextMarker": pages.continuation_token}
        result.append(next_marker)
    else:
        if pages.continuation_token:
            logger.warning('Next Marker:')
            logger.warning(pages.continuation_token)

    return result


def show_blob_v2(cmd, client, version_id=None, **kwargs):

    blob = client.get_blob_properties(version_id=version_id, **kwargs)

    page_ranges = None
    if blob.blob_type == cmd.get_models('_models#BlobType', resource_type=CUSTOM_DATA_STORAGE_BLOB).PageBlob:
        page_ranges = client.get_page_ranges(**kwargs)

    blob.page_ranges = page_ranges

    return blob


def set_blob_tags(client, tags=None, **kwargs):
    client.set_blob_tags(tags=tags, **kwargs)
    return client.get_blob_tags()


def set_blob_tier_v2(client, blob_type='block', rehydrate_priority=None, **kwargs):
    if blob_type == 'block':
        return client.set_standard_blob_tier(rehydrate_priority=rehydrate_priority,
                                             **kwargs)
    if blob_type == 'page':
        return client.set_premium_page_blob_tier(**kwargs)
    raise ValueError('Blob tier is only applicable to block or page blob.')


def snapshot_blob(client, metadata=None, **kwargs):
    client.snapshot = client.create_snapshot(metadata=metadata, **kwargs)['snapshot']
    return client.get_blob_properties()


# pylint: disable=protected-access
def _adjust_block_blob_size(client, blob_type, length):
    if not blob_type or blob_type != 'block' or length is None:
        return
    # increase the block size to 100MB when the block list will contain more than 50,000 blocks(each block 4MB)
    if length > 50000 * 4 * 1024 * 1024:
        client._config.max_block_size = 100 * 1024 * 1024
        client._config.max_single_put_size = 256 * 1024 * 1024

    # increase the block size to 4000MB when the block list will contain more than 50,000 blocks(each block 100MB)
    if length > 50000 * 100 * 1024 * 1024:
        client._config.max_block_size = 4000 * 1024 * 1024
        client._config.max_single_put_size = 5000 * 1024 * 1024


# pylint: disable=too-many-locals
def upload_blob(cmd, client, file_path=None, container_name=None, blob_name=None, blob_type=None,
                metadata=None, validate_content=False, maxsize_condition=None, max_connections=2, lease_id=None,
                if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None,
                timeout=None, progress_callback=None, encryption_scope=None, overwrite=None, data=None,
                length=None, **kwargs):
    """Upload a blob to a container."""
    from azure.core.exceptions import ResourceExistsError
    upload_args = {
        'blob_type': transform_blob_type(cmd, blob_type),
        'lease': lease_id,
        'max_concurrency': max_connections
    }

    if file_path and 'content_settings' in kwargs:
        t_blob_content_settings = cmd.get_models('_models#ContentSettings',
                                                 resource_type=CUSTOM_DATA_STORAGE_BLOB)
        kwargs['content_settings'] = guess_content_type(file_path, kwargs['content_settings'], t_blob_content_settings)

    if overwrite is not None:
        upload_args['overwrite'] = overwrite
    if maxsize_condition:
        upload_args['maxsize_condition'] = maxsize_condition

    if cmd.supported_api_version(min_api='2016-05-31'):
        upload_args['validate_content'] = validate_content

    if progress_callback:
        upload_args['progress_hook'] = progress_callback

    check_blob_args = {
        'if_modified_since': if_modified_since,
        'if_unmodified_since': if_unmodified_since,
        'if_match': if_match,
        'if_none_match': if_none_match,
    }

    # used to check for the preconditions as upload_append_blob() cannot
    if blob_type == 'append':
        if client.exists(timeout=timeout):
            client.get_blob_properties(lease=lease_id, timeout=timeout, **check_blob_args)
    else:
        upload_args['if_modified_since'] = if_modified_since
        upload_args['if_unmodified_since'] = if_unmodified_since
        upload_args['if_match'] = if_match
        upload_args['if_none_match'] = if_none_match

    # Because the contents of the uploaded file may be too large, it should be passed into the a stream object,
    # upload_blob() read file data in batches to avoid OOM problems
    try:
        if file_path:
            length = os.path.getsize(file_path)
            _adjust_block_blob_size(client, blob_type, length)
            with open(file_path, 'rb') as stream:
                response = client.upload_blob(data=stream, length=length, metadata=metadata,
                                              encryption_scope=encryption_scope,
                                              **upload_args, **kwargs)
        if data is not None:
            _adjust_block_blob_size(client, blob_type, length)
            try:
                response = client.upload_blob(data=data, length=length, metadata=metadata,
                                              encryption_scope=encryption_scope,
                                              **upload_args, **kwargs)
            except UnicodeEncodeError:
                response = client.upload_blob(data=data.encode('UTF-8', 'ignore').decode('UTF-8'),
                                              length=length, metadata=metadata,
                                              encryption_scope=encryption_scope,
                                              **upload_args, **kwargs)
    except ResourceExistsError as ex:
        from azure.cli.core.azclierror import AzureResponseError
        raise AzureResponseError(
            "{}\nIf you want to overwrite the existing one, please add --overwrite in your command.".format(ex.message))

    # PageBlobChunkUploader verifies the file when uploading the chunk data, If the contents of the file are
    # all null byte("\x00"), the file will not be uploaded, and the response will be none.
    # Therefore, the compatibility logic for response is added to keep it consistent with track 1
    if response is None:
        return {
            "etag": None,
            "lastModified": None
        }

    from msrest import Serializer
    if 'content_md5' in response and response['content_md5'] is not None:
        response['content_md5'] = Serializer.serialize_bytearray(response['content_md5'])
    if 'content_crc64' in response and response['content_crc64'] is not None:
        response['content_crc64'] = Serializer.serialize_bytearray(response['content_crc64'])
    return response


def acquire_blob_lease(client, lease_duration=-1, **kwargs):
    client.acquire(lease_duration=lease_duration, **kwargs)
    return client.id


def renew_blob_lease(client, **kwargs):
    client.renew(**kwargs)
    return client.id


def query_blob(cmd, client, query_expression, input_config=None, output_config=None, result_file=None, **kwargs):

    reader = client.query_blob(query_expression=query_expression, blob_format=input_config, output_format=output_config,
                               **kwargs)

    if result_file is not None:
        with open(result_file, 'wb') as stream:
            reader.readinto(stream)
        stream.close()
        return None

    return reader.readall().decode("utf-8")


def find_blobs_by_tags(client, filter_expression, container_name=None):
    if container_name:
        client = client.get_container_client(container_name)
    return client.find_blobs_by_tags(filter_expression=filter_expression)
