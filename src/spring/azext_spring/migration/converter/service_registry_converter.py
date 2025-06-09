# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base_converter import BaseConverter


class ServiceRegistryConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            if self.wrapper_data.is_enterprise_tier():
                if self.wrapper_data.is_support_serviceregistry():
                    # service_registry = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/serviceRegistries')
                    name = "eureka"
                    configurations = []
                    replicas = 1

                    return {
                        "eurekaName": name,
                        "configurations": configurations,
                        "replicas": replicas
                    }
                else:
                    return None
            else:
                return None
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "eureka.bicep"
