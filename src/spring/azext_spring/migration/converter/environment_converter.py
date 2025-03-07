from .base_converter import BaseConverter

# Concrete Subclass for Container App Environment
class EnvironmentConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            asa_service = self.wrapper_data.get_asa_service()
            name = asa_service['name'].split('/')[-1]
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

            asa_zone_redundant = asa_service['properties'].get('zoneRedundant')
            if asa_zone_redundant is not None:
                data["zoneRedundant"] = str(asa_zone_redundant).lower()

            asa_maintenance_window = asa_service['properties'].get('maintenanceScheduleConfiguration')
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
                disks = app['properties']['customPersistentDisks']
                for disk_props in disks:
                    # Get the account name from storage map using storageId
                    storage_name = self._get_storage_name(disk_props)
                    account_name = self._get_account_name(disk_props)
                    share_name = disk_props.get('customPersistentDiskProperties', '').get('shareName', '')
                    app_name = app['name'].split('/')[-1]
                    readOnly = disk_props.get('customPersistentDiskProperties', False).get('readOnly', False)
                    access_mode = 'ReadOnly' if readOnly else 'ReadWrite'
                    # print("storage_name + account_name + share_name + mount_path + access_mode:", storage_name + account_name + share_name + mountPath + access_mode)
                    storage_unique_name = self._get_storage_unique_name(disk_props)
                    containerAppEnvStorageName = (app_name + "_" + storage_name).replace("-", "_")
                    containerAppEnvStorageAccountKey = "containerAppEnvStorageAccountKey_" + storage_unique_name
                    # print("storage_unique_name:", storage_unique_name)
                    storage_config = {
                        'containerAppEnvStorageName': containerAppEnvStorageName,
                        'containerAppEnvStorageAccountKey': containerAppEnvStorageAccountKey,
                        'storageName': storage_unique_name,
                        'shareName': share_name,
                        'accessMode': access_mode,
                        'accountName': account_name,
                    }
                    storage_configs.append(storage_config)
        # print("storage_configs:", storage_configs)
        return storage_configs
