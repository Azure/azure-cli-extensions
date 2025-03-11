# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base_converter import BaseConverter


class LiveViewConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            if self.wrapper_data.is_support_sba():
                # live_view = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/applicationLiveViews')[0]
                name = "admin"
                configurations = []
                replicas = 1
                return {
                    "sbaName": name,
                    "configurations": configurations,
                    "replicas": replicas
                }
            else:
                return None
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "spring_boot_admin.bicep"
