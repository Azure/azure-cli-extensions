# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base_converter import BaseConverter


# Concrete Converter Subclass for Read Me
class ReadMeConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            greenDeployments = self.wrapper_data.get_green_deployments()
            return {
                "greenDeployments": self._transform_deployments(greenDeployments),
            }
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "README.md"

    def _transform_deployments(self, deployments):
        deployments_data = []
        for deployment in deployments:
            deployment_data = {
                "appName": self._get_parent_resource_name(deployment),
                "name": self._get_resource_name(deployment),
            }
            deployments_data.append(deployment_data)
        return deployments_data
