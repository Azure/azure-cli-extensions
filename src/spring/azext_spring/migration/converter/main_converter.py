from .base_converter import BaseConverter

# Concrete Converter Subclass for Read Me
class MainConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            apps = self.wrapper_data.get_apps()
            asa_certs = self.wrapper_data.get_certificates()
            certs = []
            for item in asa_certs:
                certName = item['name'].split('/')[-1]
                moduleName = "cert_" + certName.replace("-", "_")
                templateName = f"{certName}_cert.bicep"
                certData = {
                    "certName": certName,
                    "moduleName": moduleName,
                    "templateName": templateName,
                }
                certs.append(certData)
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
                        storage_unique_name = self._get_storage_unique_name(disk_props)
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
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "main.bicep"
