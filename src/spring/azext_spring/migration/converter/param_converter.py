from .base_converter import ConverterTemplate

# Concrete Converter Subclass for paramter
class ParamConverter(ConverterTemplate):
    def load_source(self, source):
        self.apps = source['apps']
        self.is_vnet = source['isVnet']
        self.storages = source['storages']

    def calculate_data(self):
        storage_map = {
            storage['name'].split('/')[-1]: storage['properties']['accountName'] 
            for storage in self.storages
        }        
        self.data.setdefault("apps", [])
        storage_configs = []
        for app in self.apps:
            appName = app['name'].split('/')[-1]
            self.data["apps"].append({
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
        self.data["storages"] = storage_configs
        self.data["isVnet"] = self.is_vnet

    def get_template_name(self):
        return "param.bicepparam"
