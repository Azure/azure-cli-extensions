from .base_converter import ConverterTemplate

# Concrete Converter Subclass for paramter
class ParamConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            self.apps = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/apps')
            self.storages = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/storages')
            storage_map = {
                    storage['name'].split('/')[-1]: storage['properties']['accountName'] 
                    for storage in self.storages
                }        
            storage_configs = []
            apps_data = []
            for app in self.apps:
                appName = app['name'].split('/')[-1]
                apps_data.append({
                    "appName": appName,
                    "containerAppImageName": "containerImageFor_"+appName.replace("-", "_"),
                    "targetPort": "targetPortFor_"+appName.replace("-", "_"),
                })
                if 'properties' in app and 'customPersistentDisks' in app['properties']:
                    disks = app['properties']['customPersistentDisks']
                    for disk_props in disks:
                        # Get the account name from storage map using storageId
                        storage_id = disk_props.get('storageId', '')
                        storage_name = self._get_resource_name(storage_id) if storage_id else ''
                        app_name = app['name'].split('/')[-1]
                        account_name = storage_map.get(storage_name, '')
                        share_name = disk_props.get('customPersistentDiskProperties', '').get('shareName', '')
                        readOnly = disk_props.get('customPersistentDiskProperties', False).get('readOnly', False)
                        access_mode = 'ReadOnly' if readOnly else 'ReadWrite'
                        mount_path = disk_props.get('customPersistentDiskProperties').get('mountPath')     
                        storage_unique_name = self._get_storage_unique_name(storage_name, account_name, share_name, mount_path, access_mode)
                        containerAppEnvStorageAccountKey = "containerAppEnvStorageAccountKey_" + storage_unique_name
                        # print("storage_unique_name:", storage_unique_name)
                        storage_config = {
                            'containerAppEnvStorageAccountKey': containerAppEnvStorageAccountKey,
                            'accountName': account_name,
                        }
                        storage_configs.append(storage_config)
            return {
                "apps": apps_data,
                "storages": storage_configs,
                "isVnet": self.wrapper_data.is_vnet()
            }
        super().__init__(input, extract_data)

    def get_template_name(self):
        return "param.bicepparam"
