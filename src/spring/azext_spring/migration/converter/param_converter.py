from .base_converter import ConverterTemplate

# Concrete Converter Subclass for paramter
class ParamConverter(ConverterTemplate):
    def load_source(self, source):
        self.apps = source['apps']
        self.is_vnet = source['isVnet']

    def calculate_data(self):
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
                    containerAppEnvStorageAccountKey = "containerAppEnvStorageAccountKey_" + (app_name + "_" + storage_name).replace("-", "")
                    storage_config = {
                        'containerAppEnvStorageAccountKey': containerAppEnvStorageAccountKey,
                    }
                    storage_configs.append(storage_config)
        self.data["storages"] = storage_configs
        self.data["isVnet"] = self.is_vnet

    def get_template_name(self):
        return "param.bicepparam"
