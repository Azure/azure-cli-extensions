from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class MainConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            apps = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/apps')
            storages = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/storages')
            asa_certs = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/certificates')
            asa_kv_certs = []
            for cert in asa_certs:
                certName = cert['name'].split('/')[-1]
                if cert['properties'].get('type') == "KeyVaultCertificate":
                    asa_kv_certs.append(cert)
            certs = []
            for item in asa_kv_certs:
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
                for storage in storages
            }
            storage_configs = []
            apps_data = []
            for app in apps:
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

            return {
                "isVnet": self.wrapper_data.is_vnet(),
                "certs": certs,
                "apps": apps_data,
                "storages": storage_configs,
                "gateway": self.wrapper_data.is_support_gateway(),
                "config": self.wrapper_data.is_support_configserver(),
                "eureka": self.wrapper_data.is_support_eureka(),
                "sba": self.wrapper_data.is_support_sba(),
            }
        super().__init__(input, extract_data)

    def get_template_name(self):
        return "main.bicep"
