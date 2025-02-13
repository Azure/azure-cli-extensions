import re

from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Container App
class AppConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source
        # print(f"App source: {self.source}")

    def calculate_data(self):
        appName = self.source['name'].split('/')[-1]
        envName = self.source['name'].split('/')[0]
        moduleName = appName.replace("-", "")
        containers = []
        serviceBinds = self._get_service_bind(self.source, envName)

        self.data = {
            "containerAppName": appName,
            "moduleName": moduleName,
            "containerImage": "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest",
            "targetPort": "80",
            "cpuCore": "0.5",
            "memorySize": "1",
            "minReplicas": 1,
            "template": {
                "containers": containers,
                "serviceBinds": serviceBinds,
            },
            "maxReplicas": 5
        }

    def get_template_name(self):
        return "app.bicep"
    
    def get_app_name(input_string):
        return input_string.split('/')[-1]

    def _get_service_bind(self, source, envName):
        enable_sba = source['enabled_sba']
        service_bind = []
        addon = source['properties'].get('addonConfigs')

        if addon is None:
            return None

        if addon.get('applicationConfigurationService') is not None and addon['applicationConfigurationService'].get('resourceId') is not None \
            or addon.get('configServer') is not None and addon['configServer'].get('resourceId') is not None:
            service_bind.append({
                "name": "bind-config",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'config')"
            })
        if addon.get('serviceRegistry') is not None and addon['serviceRegistry'].get('resourceId') is not None:
            service_bind.append({
                "name": "bind-eureka",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'eureka')"
            })
        if enable_sba:
            service_bind.append({
                "name": "bind-sba",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'admin')"
            })
        # print(f"Service bind: {service_bind}")
        return service_bind

