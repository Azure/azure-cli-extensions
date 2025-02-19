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
        moduleName = appName.replace("-", "_")
        # serviceBinds = self._get_service_bind(self.source, envName)
        deployments = self._get_deployments(self.source)
        blueDeployment = deployments[0] if len(deployments) > 0 else {}
        greenDeployment = deployments[1] if len(deployments) > 1 else {}
        tier = blueDeployment.get('sku', {}).get('tier')
        ingress = self._get_ingress(self.source, tier)
        isPublic = self.source['properties'].get('public')

        self.data = {
            "containerAppName": appName,
            "containerAppImageName": "containerImageFor_"+appName.replace("-", "_"),
            "moduleName": moduleName,
            "ingress": ingress,
            "isPublic": isPublic,
            "minReplicas": 1,
            "maxReplicas": 5,
            # "serviceBinds": serviceBinds,
            "blue": blueDeployment,
            "green": greenDeployment,
            "isBlueGreen": len(deployments) > 1
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

    def _get_deployments(self, source):
        deployments = []
        for deployment in source['deployments']:
            deployment_name = deployment['name'].split('/')[-1]
            env = deployment.get('properties', {}).get('deploymentSettings', {}).get('environmentVariables', {})
            liveness_probe = deployment.get('properties', {}).get('deploymentSettings', {}).get('livenessProbe', {})
            readiness_probe = deployment.get('properties', {}).get('deploymentSettings', {}).get('readinessProbe', {})
            resource_requests = deployment.get('properties', {}).get('deploymentSettings', {}).get('resourceRequests', {})
            cpuCore = float(resource_requests.get("cpu").replace("250m", "0.25").replace("500m", "0.5"))
            memorySize = resource_requests.get("memory")
            tier = deployment.get('sku', {}).get('tier')
            deployment = {
                "name": deployment_name,
                "env": [
                    {
                        "name": key,
                        "value": value
                    } for key, value in env.items()
                ],
                "livenessProbe": self._convert_probe(liveness_probe, tier),
                "readinessProbe": self._convert_probe(readiness_probe, tier),
                "cpuCore": cpuCore,
                "memorySize": self._get_memory_by_cpu(cpuCore) or memorySize,
            }
            deployments.append(deployment)

        # print(f"deployments: {deployments}")
        return deployments

    # A Container App must add up to one of the following CPU - Memory combinations:
    # [cpu: 0.25, memory: 0.5Gi]; [cpu: 0.5, memory: 1.0Gi]; [cpu: 0.75, memory: 1.5Gi]; [cpu: 1.0, memory: 2.0Gi]; [cpu: 1.25, memory: 2.5Gi]; [cpu: 1.5, memory: 3.0Gi]; [cpu: 1.75, memory: 3.5Gi]; [cpu: 2.0, memory: 4.0Gi]; [cpu: 2.25, memory: 4.5Gi]; [cpu: 2.5, memory: 5.0Gi]; [cpu: 2.75, memory: 5.5Gi]; [cpu: 3, memory: 6.0Gi]; [cpu: 3.25, memory: 6.5Gi]; [cpu: 3.5, memory: 7Gi]; [cpu: 3.75, memory: 7.5Gi]; [cpu: 4, memory: 8Gi]
    def _get_memory_by_cpu(self, cpu):
        cpu_memory_map = {
            0.25: "0.5Gi",
            0.5: "1.0Gi",
            0.75: "1.5Gi",
            1.0: "2.0Gi",
            1.25: "2.5Gi",
            1.5: "3.0Gi",
            1.75: "3.5Gi",
            2.0: "4.0Gi",
            2.25: "4.5Gi",
            2.5: "5.0Gi",
            2.75: "5.5Gi",
            3.0: "6.0Gi",
            3.25: "6.5Gi",
            3.5: "7.0Gi",
            3.75: "7.5Gi",
            4.0: "8.0Gi"
        }
        return cpu_memory_map.get(cpu, None)

    # create a method _convert_probe to convert the probe from the source to the target format
    def _convert_probe(self, probe, tier):
        # print(f"probe: {probe}")
        if probe is None:
            return None
        if probe.get("disableProbe") == True:
            print(f"Probe is disabled")
            return None
        initialDelaySeconds = probe.get("initialDelaySeconds", None)
        if initialDelaySeconds is not None:
            if initialDelaySeconds > 60: # Container 'undefined' 'Type' probe's InitialDelaySeconds must be in the range of ['0', '60'].
                initialDelaySeconds = 60
        result = {
            "initialDelaySeconds": initialDelaySeconds,
            "periodSeconds": probe.get("periodSeconds", None),
            "timeoutSeconds": probe.get("timeoutSeconds", None),
            "successThreshold": probe.get("successThreshold", None),
            "failureThreshold": probe.get("failureThreshold", None),
        }
        httpGet = self._convert_http_probe_action(probe, tier)
        if httpGet is not None:
            result["httpGet"] = httpGet
        tcpSocket = self._convert_tcp_probe_action(probe, tier)
        if tcpSocket is not None:
            result["tcpSocket"] = tcpSocket
        return result

    def _convert_tcp_probe_action(self, probe, tier):
        probeAction = {}
        if probe.get("probeAction", {}).get("type") == "TCPSocketAction":
            probeAction = {
                "port": 8080 if tier == "Enterprise" else 1025,
            }
        else:
            probeAction = None
        # print(f"probeAction: {probeAction}")
        return probeAction

    def _convert_http_probe_action(self, probe, tier):
        probeAction = {}
        if probe.get("probeAction", {}).get("type") == "HTTPGetAction":
            probeAction = {
                "scheme": probe.get("probeAction", {}).get("scheme"),
                "port": 8080 if tier == "Enterprise" else 1025,
                "path": probe.get("probeAction", {}).get("path"),
            }
        else:
            probeAction = None
        # print(f"probeAction: {probeAction}")
        return probeAction

    def _get_ingress(self, source, tier):
        ingress = source['properties'].get('ingressSettings')
        if ingress is None:
            return None
        return {
            "targetPort": 8080 if tier == "Enterprise" else 1025,
            "transport": ingress.get('backendProtocol').replace("Default", "auto"),
            "sessionAffinity": ingress.get('sessionAffinity').replace("Cookie", "sticky").replace("None", "none")
        }
