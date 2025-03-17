# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from .base_converter import BaseConverter

logger = get_logger(__name__)


# Concrete Subclass for Container App Environment
class EnvironmentConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            asa_service = self.wrapper_data.get_asa_service()
            name = self._get_resource_name(asa_service)
            apps = self.wrapper_data.get_apps()
            certs = self.wrapper_data.get_certificates()
            data = {
                "containerAppEnvName": name,
                "containerAppLogAnalyticsName": f"log-{name}",
                "storages": self._get_app_storage_configs(apps),
            }
            if self._need_identity(certs):
                data["identity"] = {
                    "type": "SystemAssigned",
                }
            if self.wrapper_data.is_vnet():
                data["vnetConfiguration"] = {
                    "internal": str(True).lower(),
                }

            asa_zone_redundant = asa_service['properties'].get('zoneRedundant', False)
            if asa_zone_redundant is not None:
                if asa_zone_redundant is True and self.wrapper_data.is_vnet() is False:
                    logger.warning("Mismatch: Zone redundant is only supported in VNet environment for Azure Container Apps.")
                    data["zoneRedundant"] = str(False).lower()
                else:
                    data["zoneRedundant"] = str(asa_zone_redundant).lower()

            asa_maintenance_window = asa_service['properties'].get('maintenanceScheduleConfiguration', None)
            if asa_maintenance_window:
                aca_maintenance_window = [{
                    "weekDay": asa_maintenance_window['day'],
                    "startHourUtc": asa_maintenance_window['hour'],
                    "durationHours": 8,
                }]
                data["scheduledEntries"] = aca_maintenance_window
            return data
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "environment.bicep"

    def _need_identity(self, certs):
        if certs is not None and len(certs) > 0:
            return True
        return False

    def _get_app_storage_configs(self, apps):
        storage_configs = []
        for app in apps:
            # Check if app has properties and customPersistentDiskProperties
            if 'properties' in app and 'customPersistentDisks' in app['properties']:
                disks = app['properties'].get('customPersistentDisks', [])
                for disk_props in disks:
                    if self._get_storage_enable_subpath(disk_props) is True:
                        logger.warning("Mismatch: enableSubPath of custom persistent disks is not supported in Azure Container Apps.")
                    # print("storage_name + account_name + share_name + mount_path + access_mode:", storage_name + account_name + share_name + mountPath + access_mode)
                    storage_config = {
                        'containerAppEnvStorageName': self._get_resource_name_of_storage(app, disk_props),
                        'paramContainerAppEnvStorageAccountKey': self._get_param_name_of_storage_account_key(disk_props),
                        'storageName': self._get_storage_unique_name(disk_props),
                        'shareName': self._get_storage_share_name(disk_props),
                        'accessMode': self._get_storage_access_mode(disk_props),
                        'accountName': self._get_storage_account_name(disk_props),
                    }
                    storage_configs.append(storage_config)
        # print("storage_configs:", storage_configs)
        return storage_configs

    # get resource name of containerAppEnvStorageName
    def _get_resource_name_of_storage(self, app, disk_props):
        storage_name = self._get_storage_name(disk_props)
        app_name = self._get_resource_name(app)
        return (app_name + "_" + storage_name).replace("-", "_")
