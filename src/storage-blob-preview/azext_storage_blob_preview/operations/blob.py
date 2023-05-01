# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

from datetime import datetime, timedelta

from azure.cli.core.profiles import get_sdk
from knack.log import get_logger
from knack.util import CLIError

from .._transformers import transform_response_with_bytearray
from ..profiles import CUSTOM_DATA_STORAGE_BLOB

logger = get_logger(__name__)


def set_blob_tier(client, container_name, blob_name, tier, blob_type='block', timeout=None):
    if blob_type == 'block':
        return client.set_standard_blob_tier(container_name=container_name, blob_name=blob_name,
                                             standard_blob_tier=tier, timeout=timeout)
    if blob_type == 'page':
        return client.set_premium_page_blob_tier(container_name=container_name, blob_name=blob_name,
                                                 premium_page_blob_tier=tier, timeout=timeout)
    raise ValueError('Blob tier is only applicable to block or page blob.')


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


def find_blobs_by_tags(client, filter_expression, container_name=None):
    if container_name:
        client = client.get_container_client(container_name)
    return client.find_blobs_by_tags(filter_expression=filter_expression)
