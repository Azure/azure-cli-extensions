# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage queue commands"""
from ..profiles import CUSTOM_DATA_STORAGE_QUEUE


def queue_exists(cmd, client, **kwargs):
    from azure.core.exceptions import HttpResponseError
    try:
        client.get_queue_properties(**kwargs)
        return True
    except HttpResponseError as ex:
        from azure.cli.command_modules.storage.track2_util import _dont_fail_on_exist
        StorageErrorCode = cmd.get_models("_shared.models#StorageErrorCode",
                                          resource_type=CUSTOM_DATA_STORAGE_QUEUE)
        return _dont_fail_on_exist(ex, StorageErrorCode.queue_not_found)


def generate_queue_sas(cmd, client, permission=None, expiry=None, start=None,
                       policy_id=None, ip=None, protocol=None, **kwargs):
    generate_queue_sas_fn = cmd.get_models('_shared_access_signature#generate_queue_sas')

    sas_kwargs = {'protocol': protocol}
    sas_token = generate_queue_sas_fn(account_name=client.account_name, queue_name=client.queue_name,
                                      account_key=client.credential.account_key, permission=permission,
                                      expiry=expiry, start=start, policy_id=policy_id, ip=ip, **sas_kwargs)

    return sas_token


def create_queue(cmd, client, metadata=None, fail_on_exist=False, timeout=None, **kwargs):
    from azure.core.exceptions import HttpResponseError
    try:
        client.create_queue(metadata=metadata, timeout=timeout, **kwargs)
        return True
    except HttpResponseError as ex:
        from azure.cli.command_modules.storage.track2_util import _dont_fail_on_exist
        StorageErrorCode = cmd.get_models("_shared.models#StorageErrorCode",
                                          resource_type=CUSTOM_DATA_STORAGE_QUEUE)
        if not fail_on_exist:
            return _dont_fail_on_exist(ex, StorageErrorCode.queue_already_exists)
        raise ex


def delete_queue(cmd, client, fail_not_exist=False, timeout=None, **kwargs):
    from azure.core.exceptions import HttpResponseError
    try:
        client.delete_queue(timeout=timeout, **kwargs)
        return True
    except HttpResponseError as ex:
        from azure.cli.command_modules.storage.track2_util import _dont_fail_on_exist
        StorageErrorCode = cmd.get_models("_shared.models#StorageErrorCode",
                                          resource_type=CUSTOM_DATA_STORAGE_QUEUE)
        if not fail_not_exist:
            return _dont_fail_on_exist(ex, StorageErrorCode.queue_not_found)
        raise ex
