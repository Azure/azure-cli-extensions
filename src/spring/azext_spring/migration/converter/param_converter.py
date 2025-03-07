from .base_converter import BaseConverter

# Concrete Converter Subclass for paramter
class ParamConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            self.apps = self.wrapper_data.get_apps()
            storage_configs = []
            apps_data = []
            for app in self.apps:
                appName = app['name'].split('/')[-1]
                apps_data.append({
                    "appName": appName,
                    "paramContainerAppImageName": "containerImageFor_"+appName.replace("-", "_"),
                    "paramTargetPort": "targetPortFor_"+appName.replace("-", "_"),
                })
                if 'properties' in app and 'customPersistentDisks' in app['properties']:
                    disks = app['properties']['customPersistentDisks']
                    for disk_props in disks:
                        # Get the account name from storage map using storageId
                        account_name = self._get_account_name(disk_props)
                        storage_unique_name = self._get_storage_unique_name(disk_props)
                        paramContainerAppEnvStorageAccountKey = "containerAppEnvStorageAccountKey_" + storage_unique_name
                        # print("storage_unique_name:", storage_unique_name)
                        storage_config = {
                            'paramContainerAppEnvStorageAccountKey': paramContainerAppEnvStorageAccountKey,
                            'accountName': account_name,
                        }
                        storage_configs.append(storage_config)
            return {
                "apps": apps_data,
                "storages": storage_configs,
                "isVnet": self.wrapper_data.is_vnet()
            }
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "param.bicepparam"
