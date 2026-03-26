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
            apps_data = []
            for app in apps:
                apps_data.append({
                    "appName": self._get_resource_name(app),
                    "paramContainerAppImageName": self._get_param_name_of_container_image(app),
                    "paramTargetPort": self._get_param_name_of_target_port(app),
                    "isByoc": self.wrapper_data.is_support_custom_container_image_for_app(app),
                    "isPrivateImage": self.wrapper_data.is_private_custom_container_image(app),
                    "paramContainerAppImagePassword": self._get_param_name_of_container_image_password(app),
                    "image": self._get_container_image(app),
                })

            return {
                "apps": apps_data,
                "storages": self._get_app_storage_configs(),
                "isVnet": self.wrapper_data.is_vnet()
            }
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "param.bicepparam"
