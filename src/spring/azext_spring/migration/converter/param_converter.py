# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base_converter import BaseConverter


# Concrete Converter Subclass for paramter
class ParamConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            apps = self.wrapper_data.get_apps()
            storage_configs = []
            apps_data = []
            for app in apps:
                apps_data.append({
                    "appName": self._get_resource_name(app),
                    "paramContainerAppImageName": self._get_param_name_of_container_image(app),
                    "paramTargetPort": self._get_param_name_of_target_port(app),
                })
                if 'properties' in app and 'customPersistentDisks' in app['properties']:
                    disks = app['properties']['customPersistentDisks']
                    for disk_props in disks:
                        storage_config = {
                            'paramContainerAppEnvStorageAccountKey': self._get_param_name_of_storage_account_key(disk_props),
                            'accountName': self._get_storage_account_name(disk_props),
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
