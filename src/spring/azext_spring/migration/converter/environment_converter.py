from .base_converter import ConverterTemplate

# Concrete Subclass for Container App Environment
class EnvironmentConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            asa_service = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring')[0]
            name = asa_service['name'].split('/')[-1]
            apps = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/apps')
            storages = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/storages')
            certs = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/certificates')
            data = {
                "containerAppEnvName": name,
                "containerAppLogAnalyticsName": f"log-{name}",
                "storages": self._get_app_storage_configs(apps, storages),
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
        super().__init__(input, extract_data)

    def get_template_name(self):
        return "environment.bicep"

    def _need_identity(self, certs):
        if certs is not None and len(certs) > 0:
            return True
        return False

    def _get_app_storage_configs(self, apps, storages):
        storage_configs = []
        
        # Create a mapping of storage IDs to account names
        storage_map = {
            storage['name'].split('/')[-1]: storage['properties']['accountName'] 
            for storage in storages
        }
        # print("storage_map:", storage_map)
        for app in apps:
            # Check if app has properties and customPersistentDiskProperties
            if 'properties' in app and 'customPersistentDisks' in app['properties']:
                disks = app['properties']['customPersistentDisks']
                for disk_props in disks:
                    # Get the account name from storage map using storageId
                    storage_id = disk_props.get('storageId', '')
                    storage_name = self._get_resource_name(storage_id) if storage_id else ''
                    account_name = storage_map.get(storage_name, '')
                    share_name = disk_props.get('customPersistentDiskProperties', '').get('shareName', '')
                    app_name = app['name'].split('/')[-1]
                    readOnly = disk_props.get('customPersistentDiskProperties', False).get('readOnly', False)
                    access_mode = 'ReadOnly' if readOnly else 'ReadWrite'
                    mount_path = disk_props.get('customPersistentDiskProperties').get('mountPath')
                    # print("storage_name + account_name + share_name + mount_path + access_mode:", storage_name + account_name + share_name + mountPath + access_mode)
                    storage_unique_name = self._get_storage_unique_name(storage_name, account_name, share_name, mount_path, access_mode)
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
