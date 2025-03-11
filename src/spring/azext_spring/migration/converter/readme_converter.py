# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from .base_converter import BaseConverter


# Concrete Converter Subclass for Read Me
class ReadMeConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            is_vnet = self.wrapper_data.is_vnet()
            build_results_deployments = self.wrapper_data.get_build_results_deployments()
            container_deployments = self.wrapper_data.get_container_deployments()
            is_support_configserver = self.wrapper_data.is_support_ossconfigserver()
            custom_domains = self.wrapper_data.get_custom_domains()
            apps = self.wrapper_data.get_apps()
            keyvault_certs = self.wrapper_data.get_keyvault_certificates()
            content_certs = self.wrapper_data.get_content_certificates()
            green_deployments = self.wrapper_data.get_green_deployments()
            should_system_assigned_identity_enabled = len(self.wrapper_data.get_keyvault_certificates()) > 0
            auto_scale_enabled_deployments = []  # todo
            system_assigned_identity_apps = []  # todo

            data = {
                "isVnet": is_vnet,
                "containerApps": container_deployments,
                "buildResultsApps": build_results_deployments,
                "hasApps": len(apps) > 0,
                "isSupportConfigServer": is_support_configserver,
                "customDomains": self._transform_domains(custom_domains),
                "hasCerts": len(keyvault_certs) > 0 or len(content_certs) > 0,
                "keyVaultCerts": keyvault_certs,
                "contentCerts": content_certs,
                "greenDeployments": self._transform_deployments(green_deployments),
                "autoScaleEnabledApps": auto_scale_enabled_deployments,
                "shouldSystemAssignedIdentityEnabled": should_system_assigned_identity_enabled,
                "systemAssignedIdentityApps": system_assigned_identity_apps,
            }
            # print(f"ReadMeConverter data: {data}")
            return data
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

    def _transform_domains(self, domains):
        domains_data = []
        for domain in domains:
            domain_data = {
                "appName": self._get_parent_resource_name(domain),
                "name": self._get_resource_name(domain),
            }
            domains_data.append(domain_data)
        return domains_data
