# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base_converter import BaseConverter


# Concrete Converter Subclass for main
class MainConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            asa_certs = self.wrapper_data.get_certificates()
            certs = []
            for cert in asa_certs:
                certName = self._get_resource_name(cert)
                templateName = f"{certName}_cert.bicep"
                certData = {
                    "certName": certName,
                    "moduleName": self._get_cert_module_name(cert),
                    "templateName": templateName,
                }
                certs.append(certData)
            storage_configs = []
            apps_data = []
            apps = self.wrapper_data.get_apps()
            for app in apps:
                appName = self._get_resource_name(app)
                templateName = f"{appName}_app.bicep"
                appData = {
                    "appName": appName,
                    "moduleName": self._get_app_module_name(app),
                    "templateName": templateName,
                    "paramContainerAppImageName": self._get_param_name_of_container_image(app),
                    "paramTargetPort": self._get_param_name_of_target_port(app),
                    "dependsOns": self._get_depends_on_list(app),
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

    def _get_depends_on_list(self, app):
        service_bind = []
        if self.wrapper_data.is_support_configserver_for_app(app):
            service_bind.append("managedConfig")
        if self.wrapper_data.is_enterprise_tier() is not True and self.wrapper_data.is_support_ossconfigserver():
            # standard tier enabled config server and bind all apps automatically
            service_bind.append("managedConfig")
        if self.wrapper_data.is_support_serviceregistry_for_app(app):
            service_bind.append("managedEureka")
        if self.wrapper_data.is_enterprise_tier() is not True and self.wrapper_data.is_support_eureka():
            # standard tier enabled eureka server and bind all apps automatically
            service_bind.append("managedEureka")
        if self.wrapper_data.is_support_sba():
            service_bind.append("managedSpringBootAdmin")
        return service_bind
