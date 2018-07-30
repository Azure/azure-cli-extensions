# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access,line-too-long,too-many-locals,too-many-statements
import ctypes
import os
import base64
import json
import platform
import struct
import uuid
import shutil
import tempfile
import multiprocessing

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from knack.log import get_logger
from knack.util import CLIError

from msrestazure.tools import parse_resource_id, is_valid_resource_id
from azure.common import AzureMissingResourceHttpError
from azure.storage.common.retry import ExponentialRetry
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.commands.client_factory import get_data_service_client, get_mgmt_service_client

try:
    xrange
except NameError:
    xrange = range

logger = get_logger(__name__)


def client_side_encrypt(cmd, vhd_file, vhd_file_enc=None, storage_account=None, container='vhds', blob_name=None,
                        key_encryption_key=None, key_encryption_keyvault=None, no_progress=None, max_connections=10):
    # TODO: storage account should support sas as well

    # arguments checks
    if not key_encryption_key or not key_encryption_keyvault:
        raise CLIError('useage error: --key-encryption-key KEY_NAME or KEY_ID --key-encryption-keyvault KEY_VAULT_RESOURCE_ID')

    if bool(storage_account) == bool(vhd_file_enc):
        raise CLIError('usage error: please specify either "--storage-acount" or "--vhd-file-enc", but not both')

    if not os.path.isfile(vhd_file):
        raise CLIError('"{}" to encrypt doesn\'t exist')

    if storage_account:
        data_client = _get_storage_prerequisites(cmd, storage_account, container)

    # check there is enough disk-space
    required_size = os.path.getsize(vhd_file)
    if vhd_file_enc:
        target_path = os.path.dirname(os.path.abspath(vhd_file_enc))
    else:
        target_path = tempfile.gettempdir()
    if _get_disk_free_spaces(target_path) < required_size:
        raise CLIError('No enough disk space to contain encryption result. Please free up at least {} GB from the drive of "{}"'.format(
            required_size // (1024**3), target_path))

    if storage_account and not blob_name:
        blob_name = '{0}.encrypted.vhd'.format(os.path.splitext(os.path.basename(vhd_file))[0])

    metadata_key = 'DiskEncryptionSettings'
    key, metedata_vaule = _encyrption_key_gen(cmd, key_encryption_key, key_encryption_keyvault)

    result_file = _encrypt_vhd(cmd, vhd_file, vhd_file_enc, key, not no_progress)
    if storage_account:
        logger.warning('\nUploading "%s" to blob "%s" at storage of "%s"', result_file, blob_name, storage_account)
        try:
            _upload_vhd_to_storage(cmd, result_file, data_client, container, blob_name, metadata_key,
                                   metedata_vaule, not no_progress, max_connections)
        finally:
            logger.warning('Removing local encrypted VHD: %s', result_file)
            os.remove(result_file)
    else:
        # tell user the command they should run later to upload vhd and metadata together
        _, metadata_file = tempfile.mkstemp()
        with open(metadata_file, 'w') as f:
            f.write(json.dumps(metedata_vaule))
        cmd = 'az storage blob upload --account-name myStorageAccount -c containter -n {0} -f "{1}" --metadata {2}=@{3}'.format(
            os.path.basename(result_file), result_file, metadata_key, metadata_file)
        logger.warning('Encryption is completed. If you like to upload the encrypted VHD to create a VM later,'
                       ' run the following command:\n    %s', cmd)


def _encyrption_key_gen(cmd, key_encryption_key, key_encryption_keyvault):
    key = os.urandom(64)
    if not key_encryption_keyvault:
        return key, None, None
    if not is_valid_resource_id(key_encryption_keyvault) or not key_encryption_key:
        raise CLIError('Please supply a full resource id of the keyvault and a keyvault key name or id')
    vault_name = parse_resource_id(key_encryption_keyvault)['name']
    kv_client = _create_keyvault_data_plane_client(cmd.cli_ctx)
    vault_base_url = 'https://{}{}'.format(vault_name, cmd.cli_ctx.cloud.suffixes.keyvault_dns)

    key_encryption_key = key_encryption_key.lower()
    parts = key_encryption_key.lstrip('https://').rstrip('/').split('/')
    if len(parts) in [1, 3]:  # we can take a key name or a key id w/o version, and resolve to the latest version
        key_result = kv_client.get_key(vault_base_url, key_encryption_key if len(parts) == 1 else parts[-1], '')
        key_encryption_key = key_result.key.kid  # pylint: disable=no-member
        parts = key_encryption_key.lstrip('https://').split('/')
    elif len(parts) != 4:
        raise CLIError('usage error: --key-encryption-key KEY-NAME|KEYID')

    kek_name, kek_version = parts[-2], parts[-1]
    logger.warning('Wrapping data encryption key with key encryption key:\n    vault_base_url: %s\n    key encrypton key: %s\n    key version: %s',
                   vault_base_url, kek_name, kek_version)
    wraped = kv_client.wrap_key(vault_base_url, kek_name, kek_version, 'RSA-OAEP', base64.b64encode(key))
    secret_name = str(uuid.uuid4()).replace('-', '')
    logger.warning('Uploading wrapped key as secret:\n    secret name: %s', secret_name)
    secret_result = kv_client.set_secret(vault_base_url, secret_name, wraped.result)
    metadate_value = {
        "encryptionSettingsVersion": "2.0",
        "dataEncryptionMetadata": {
            "encryptionCipherMode": "AES-XTS",
            "encryptionKeyLength": 512,
            "encryptionBlockSize": 512
        },
        "encryptionEnabled": True,
        "encryptionSettings": [{
            "DiskEncryptionKey": {
                "sourceVault": {"id": key_encryption_keyvault},
                "secretUrl": secret_result.id
            },
            "keyEncryptionKey": {
                "sourceVault": {"id": key_encryption_keyvault},
                "keyUrl": key_encryption_key,
                "kekAlgorithm": "RSA-OAEP"
            }
        }]
    }
    return key, metadate_value


def _encrypt_vhd(cmd, vhd_file, vhd_file_enc, key, show_progress):
    vhd_size = os.path.getsize(vhd_file)

    if not vhd_size or vhd_size < 512 or vhd_size % 512:
        raise ValueError('file size of "{}" is not right at "{}"'.format(vhd_file, vhd_size))

    with open(vhd_file, 'rb') as f:
        # verify the vhd file
        f.seek(vhd_size - 512)
        footer = f.read(512)

    cookie = footer[0:8].decode()
    if cookie != 'conectix':
        raise ValueError('right footer is not found for invalid cookie "{}"'.format(cookie))
    buffer = footer[60:64]
    disk_type = struct.unpack("i", buffer)[0]
    if disk_type != 0x02000000:
        raise CLIError('VHD footer has an invalid disk type of "{}". Expect: "{}"'.format(disk_type, 0x02000000))

    sector_count = (vhd_size - 512) // 512

    proc_count = min(multiprocessing.cpu_count(), 8)
    proc_sector_load = sector_count // proc_count

    if not vhd_file_enc:
        fd, fname = tempfile.mkstemp()
        os.close(fd)
        vhd_file_enc = fname

    if proc_count != 1:
        # do we have enugh temp space?
        if _get_disk_free_spaces(tempfile.gettempdir()) - 1024**3 < vhd_size:
            logger.info('no enough temporary disk space for concurrent encryption')
            proc_count = 1

    if proc_count != 1:
        staging_dir = tempfile.mkdtemp()
        logger.warning('Created staging folder "%s" for %s concurrent encryption tasks', staging_dir, proc_count)
        vhd_fragment_files = []
        try:
            for t in range(proc_count - 1):
                fd, fname = tempfile.mkstemp(dir=staging_dir)
                os.close(fd)
                vhd_fragment_files.append(fname + '.vhd')
            vhd_fragment_files.insert(0, vhd_file_enc)

            task_infos = [[vhd_file, vhd_fragment_files[t], t * proc_sector_load, proc_sector_load, key] for t in range(proc_count)]
            task_infos[-1][3] += (sector_count % proc_count)

            sub_processes = [multiprocessing.Process(target=_encrypt_vhd_fragment, args=(arg, None)) for arg in task_infos[1:]]
            for p in sub_processes:
                p.start()
            _encrypt_vhd_fragment(task_infos[0], _init_progress_callback(cmd, 'Encrypting') if show_progress else None)
            for p in sub_processes:
                p.join()

            # with multiprocessing.Pool(processes=proc_count) as pool:
            #    pool.map(_encrypt_vhd_fragment, task_infos)
            progress = _init_progress_callback(cmd, 'Finalizing encrypted vhd file') if show_progress else None
            with open(vhd_file_enc, 'ab') as f_enc:
                for i, t in enumerate(vhd_fragment_files[1:]):
                    with open(t, 'rb') as t_f:
                        shutil.copyfileobj(t_f, f_enc, 1024 * 2048)  # TODO make sure the number is fine
                        if progress:
                            progress(i + 1, len(vhd_fragment_files) - 1)
                    os.remove(t)
                f_enc.write(footer)
        finally:
            if os.path.isdir(staging_dir):
                shutil.rmtree(staging_dir)
    else:
        _encrypt_vhd_fragment([vhd_file, vhd_file_enc, 0, sector_count, key])
    return vhd_file_enc


def _encrypt_vhd_fragment(args, progress=None):
    vhd_file, vhd_file_enc, sector_start, sectors, key = args
    if progress:
        prev, current, step, total = 0, 0, sectors // 100, sectors
    current, total = sector_start, sector_start + sectors
    with open(vhd_file, 'rb') as f:
        f.seek(sector_start * 512)
        with open(vhd_file_enc, 'wb') as f_enc:
            tweak = _get_tweak(sector_start)
            cipher = Cipher(
                algorithms.AES(key, ),
                modes.XTS(tweak),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            for _ in xrange(sectors):
                plaintext = f.read(512)
                ciphertext = encryptor.update(plaintext)
                f_enc.write(ciphertext)

                sector_start += 1
                cipher.mode._tweak = _get_tweak(sector_start)
                res = cipher._backend._lib.EVP_CipherInit_ex(
                    encryptor._ctx._ctx,
                    cipher._backend._ffi.NULL,
                    cipher._backend._ffi.NULL,
                    key,
                    cipher.mode._tweak,
                    1
                )
                if res == 0:
                    raise ValueError('"EVP_CipherInit_ex" failed to refresh the tweak')
                if progress:
                    current += 1
                    if current - prev >= step:
                        progress(current, total)
                        prev = current
            encryptor.finalize()
            if progress and prev != total:  # make it 100%
                progress(total, total)


def _upload_vhd_to_storage(cmd, file_path, client, container_name, blob_name,
                           metadata_key, metedata_vaule, show_progress, max_connections):

    client.retry = ExponentialRetry(initial_backoff=30, increment_base=2, max_attempts=10).retry
    # increase the block size to 100MB when the block list will contain more
    # than 50,000 blocks
    if os.stat(file_path).st_size > 50000 * 4 * 1024 * 1024:
        client.MAX_BLOCK_SIZE = 100 * 1024 * 1024
        client.MAX_SINGLE_PUT_SIZE = 256 * 1024 * 1024
    t_content_settings = cmd.get_models('blob.models#ContentSettings', resource_type=ResourceType.DATA_STORAGE)

    create_blob_args = {
        'container_name': container_name,
        'blob_name': blob_name,
        'file_path': file_path,
        'progress_callback': _init_progress_callback(cmd, 'Uploading') if show_progress else None,
        'content_settings': t_content_settings(),  # can we get rid of this?
        'metadata': {metadata_key: json.dumps(metedata_vaule)},
        'max_connections': max_connections,
        'lease_id': None,
        'if_modified_since': None,
        'if_unmodified_since': None,
        'if_match': None,
        'if_none_match': None,
        'timeout': None
    }
    # do we need this???
    # if cmd.supported_api_version(min_api='2016-05-31'):
    #     create_blob_args['validate_content'] = validate_content
    return client.create_blob_from_path(**create_blob_args)


def _init_progress_callback(cmd, msg):
    def _update_progress(current, total):
        hook = cmd.cli_ctx.get_progress_controller(det=True)

        if total:
            hook.add(message=msg, value=current, total_val=total)
            if total == current:
                hook.end()

    return _update_progress


def _create_keyvault_data_plane_client(cli_ctx):
    from azure.cli.core._profile import Profile

    def get_token(server, resource, scope):  # pylint: disable=unused-argument
        return Profile(cli_ctx=cli_ctx).get_login_credentials(resource)[0]._token_retriever()  # pylint: disable=protected-access

    from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
    return KeyVaultClient(KeyVaultAuthentication(get_token))


def _get_tweak(int_v):
    v = struct.pack('<I', int_v)
    return v.ljust(16, b'\0')


def _get_disk_free_spaces(folder):
    try:
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            return free_bytes.value
        statvfs = os.statvfs(folder)  # pylint: disable=no-member
        return statvfs.f_frsize * statvfs.f_bfree
    except Exception as ex:  # pylint: disable=broad-except
        logger.info('get free space failed for error %s', ex)
        return 0


def _get_storage_prerequisites(cmd, storage_account, container):
    t_page_blob_service = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE, 'blob.pageblobservice#PageBlobService')

    mgmt_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_STORAGE)
    acc = next((x for x in mgmt_client.storage_accounts.list() if x.name.lower() == storage_account.lower()), None)
    account_key = None
    if acc:
        rg = parse_resource_id(acc.id)['resource_group']

        t_storage_account_keys, t_storage_account_list_keys_results = get_sdk(
            cmd.cli_ctx, ResourceType.MGMT_STORAGE,
            'models.storage_account_keys#StorageAccountKeys',
            'models.storage_account_list_keys_result#StorageAccountListKeysResult')

        if t_storage_account_keys:
            account_key = mgmt_client.storage_accounts.list_keys(rg, storage_account).key1
        elif t_storage_account_list_keys_results:
            account_key = mgmt_client.storage_accounts.list_keys(rg, storage_account).keys[0].value
    else:
        raise CLIError('Storage account of "{}" doesn\'t exist'.format(storage_account))

    if not account_key:
        raise ValueError('credentials to access storage account is missing')
    data_client = get_data_service_client(cmd.cli_ctx, t_page_blob_service, storage_account,
                                          account_key, None, None, socket_timeout=None,
                                          endpoint_suffix=cmd.cli_ctx.cloud.suffixes.storage_endpoint)
    try:
        data_client.get_container_properties(container)  # verify the container exists
    except AzureMissingResourceHttpError:
        raise CLIError('"{}" doesn\'t exist in the storage account of "{}"'.format(container, storage_account))
    return data_client
