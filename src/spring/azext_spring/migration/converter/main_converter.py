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
                templateName = f"{certName}_cert.bicep"
                certData = {
                    "certName": certName,
                    "moduleName": self._get_cert_module_name(item),
                    "templateName": templateName,
                }
                certs.append(certData)
            storage_configs = []
            apps_data = []
            for app in apps:
                appName = app['name'].split('/')[-1]
                templateName = f"{appName}_app.bicep"
                appData = {
                    "appName": appName,
                    "moduleName": self._get_app_module_name(app),
                    "templateName": templateName,
                    "paramContainerAppImageName": self._get_param_name_of_container_image(app),
                    "paramTargetPort": self._get_param_name_of_target_port(app),
                }
                if 'properties' in app and 'customPersistentDisks' in app['properties']:
                    disks = app['properties']['customPersistentDisks']
                    for disk_props in disks:
                        storage_config = {
                            'paramContainerAppEnvStorageAccountKey': self._get_param_name_of_storage_account_key(disk_props),
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
