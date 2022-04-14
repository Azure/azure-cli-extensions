# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from azure.cli.core.azclierror import FileOperationError, InvalidArgumentValueError
from .vendored_sdks.appplatform.v2022_01_01_preview import models
from .vendored_sdks.appplatform.v2022_03_01_preview import models as models_20220301preview
from azure.cli.core.util import get_file_json


class DefaultApp:
    def format_resource(self, **kwargs):
        return models.AppResource(
            properties=self._format_properties(**kwargs),
            identity=self._format_identity(**kwargs)
        )

    def _format_properties(self, **kwargs):
        kwargs['custom_persistent_disks'] = self._load_custom_persistent_disks(**kwargs)
        kwargs['loaded_certificates'] = self._load_public_certificate_file(**kwargs)
        kwargs['persistent_disk'] = self._load_persistent_disk(**kwargs)
        kwargs['temporary_disk'] = self._load_temp_disk(**kwargs)
        return models.AppResourceProperties(**kwargs)

    def _format_identity(self, system_assigned=None, user_assigned=None, **_):
        target_identity_type = self._get_identity_assign_type(system_assigned, user_assigned)
        user_identity_payload = self._get_user_identity_payload(user_assigned)
        identity_props = None
        if target_identity_type != models_20220301preview.ManagedIdentityType.NONE:
            identity_props = models_20220301preview.ManagedIdentityProperties()
            identity_props.type = target_identity_type
            identity_props.user_assigned_identities = user_identity_payload
        return identity_props

    def _get_identity_assign_type(self, system_assigned=None, user_assigned=None):
        target_identity_type = models_20220301preview.ManagedIdentityType.NONE
        if system_assigned and user_assigned:
            target_identity_type = models_20220301preview.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        elif system_assigned:
            target_identity_type = models_20220301preview.ManagedIdentityType.SYSTEM_ASSIGNED
        elif user_assigned:
            target_identity_type = models_20220301preview.ManagedIdentityType.USER_ASSIGNED
        return target_identity_type

    def _get_user_identity_payload(self, user_assigned=None):
        if not user_assigned:
            return None
        user_identity_payload = {}
        for user_identity_resource_id in user_assigned:
            user_identity_payload[user_identity_resource_id] = models_20220301preview.UserAssignedManagedIdentity()
        if len(user_identity_payload) == 0:
            user_identity_payload = None
        return user_identity_payload

    def _load_temp_disk(self, enable_temporary_disk=None, **_):
        if enable_temporary_disk is not None:
            return models.TemporaryDisk(
                size_in_gb=5, mount_path="/tmp"
            )

    def _load_persistent_disk(self, enable_persistent_storage=None, **_):
        if enable_persistent_storage is not None:  # False matters
            return models.PersistentDisk(
                size_in_gb=self._get_persistent_disk_size(enable_persistent_storage),
                mount_path='/persistent'
            )

    def _get_persistent_disk_size(self, enable_persistent_storage):
        return 50 if enable_persistent_storage else 0

    def _load_public_certificate_file(self, client, resource_group, service, loaded_public_certificate_file=None, **_):
        if not loaded_public_certificate_file:
            return
        data = get_file_json(loaded_public_certificate_file)
        if not data:
            return
        if not data.get('loadedCertificates'):
            raise FileOperationError("loadedCertificates must be provided in the json file")
        loaded_certificates = []
        for item in data['loadedCertificates']:
            if not item.get('certificateName') or not item.get('loadTrustStore'):
                raise FileOperationError("certificateName, loadTrustStore must be provided in the json file")
            certificate_resource = client.certificates.get(resource_group, service, item['certificateName'])
            loaded_certificates.append(models.LoadedCertificate(resource_id=certificate_resource.id,
                                                                load_trust_store=item['loadTrustStore']))
        return loaded_certificates

    def _load_custom_persistent_disks(self, client, resource_group, service, persistent_storage=None, **_):
        if not persistent_storage:
            return
        data = get_file_json(persistent_storage, throw_on_empty=False)
        if not data:
            return
        custom_persistent_disks = []

        if not data.get('customPersistentDisks'):
            raise InvalidArgumentValueError("CustomPersistentDisks must be provided in the json file")
        for item in data['customPersistentDisks']:
            invalidProperties = not item.get('storageName') or \
                not item.get('customPersistentDiskProperties').get('type') or \
                not item.get('customPersistentDiskProperties').get('shareName') or \
                not item.get('customPersistentDiskProperties').get('mountPath')
            if invalidProperties:
                raise InvalidArgumentValueError("StorageName, Type, ShareName, MountPath mast be provided in the json file")
            storage_resource = client.storages.get(resource_group, service, item['storageName'])
            custom_persistent_disk_properties = models.AzureFileVolume(
                type=item['customPersistentDiskProperties']['type'],
                share_name=item['customPersistentDiskProperties']['shareName'],
                mount_path=item['customPersistentDiskProperties']['mountPath'],
                mount_options=item['customPersistentDiskProperties']['mountOptions'] if 'mountOptions' in item['customPersistentDiskProperties'] else None,
                read_only=item['customPersistentDiskProperties']['readOnly'] if 'readOnly' in item['customPersistentDiskProperties'] else None)

            custom_persistent_disks.append(
                models.CustomPersistentDiskResource(
                    storage_id=storage_resource.id,
                    custom_persistent_disk_properties=custom_persistent_disk_properties))
        return custom_persistent_disks


class BasicTierApp(DefaultApp):
    def _get_persistent_disk_size(self, enable_persistent_storage, **_):
        return 1 if enable_persistent_storage else 0


class EnterpriseTierApp(DefaultApp):
    def _get_persistent_disk_size(self, enable_persistent_storage, **_):
        if enable_persistent_storage:
            raise InvalidArgumentValueError('Enterprise tier Spring-Cloud instance does not support --enable-persistent-storage')


def app_selector(sku, **_):
    if sku.name == 'E0':
        return EnterpriseTierApp()
    if sku.name == 'B0':
        return BasicTierApp()
    return DefaultApp()
