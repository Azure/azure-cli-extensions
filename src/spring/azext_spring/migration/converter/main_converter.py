from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class MainConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data(input):
            # TODO: Implement the extract_data method
            return input
        super().__init__(input, extract_data)

    def load_source(self, source):
        self.source = source
        self.apps = source["apps"]
        self.certs = source["certs"]
        self.storages = source["storages"]

    def calculate_data(self):
        certs = []
        for item in self.certs:
            certName = item['name'].split('/')[-1]
            moduleName = "cert_" + certName.replace("-", "_")
            templateName = f"{certName}_cert.bicep"
            certData = {
                "certName": certName,
                "moduleName": moduleName,
                "templateName": templateName,
            }
            certs.append(certData)
        storage_map = {
            storage['name'].split('/')[-1]: storage['properties']['accountName'] 
            for storage in self.storages
        }
        storage_configs = []
        apps_data = []
        for app in self.apps:
            appName = app['name'].split('/')[-1]
            moduleName = appName.replace("-", "_")
            templateName = f"{appName}_app.bicep"
            appData = {
                "appName": appName,
                "moduleName": moduleName,
                "templateName": templateName,
                "containerAppImageName": "containerImageFor_"+appName.replace("-", "_"),
                "targetPort": "targetPortFor_"+appName.replace("-", "_"),
            }
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
                    # print("storage_unique_name:", storage_unique_name)
                    containerAppEnvStorageAccountKey = "containerAppEnvStorageAccountKey_" + storage_unique_name
                    storage_config = {
                        'containerAppEnvStorageAccountKey': containerAppEnvStorageAccountKey,
                    }
                    storage_configs.append(storage_config)

            apps_data.append(appData)

        self.data = {
            "isVnet": self.wrapper_data.is_vnet(),
            "certs": certs,
            "apps": apps_data,
            "storages": storage_configs,
            "gateway": self.wrapper_data.is_support_gateway(),
            "config": self.wrapper_data.is_support_configserver(),
            "eureka": self.wrapper_data.is_support_eureka(),
            "sba": self.wrapper_data.is_support_sba(),
        }

    def get_template_name(self):
        return "main.bicep"
