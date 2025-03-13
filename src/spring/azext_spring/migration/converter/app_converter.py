# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from .base_converter import BaseConverter

logger = get_logger(__name__)


# Concrete Converter Subclass for Container App
class AppConverter(BaseConverter):

    DEFAULT_MOUNT_OPTIONS = "uid=0,gid=0,file_mode=0777,dir_mode=0777"

    def __init__(self, source):
        def transform_data():
            return self.wrapper_data.get_apps()
        super().__init__(source, transform_data)

    def transform_data_item(self, app):
        blueDeployment = self.wrapper_data.get_blue_deployment_by_app(app)
        blueDeployment = self._transform_deployment(blueDeployment)
        greenDeployment = self.wrapper_data.get_green_deployment_by_app(app)
        greenDeployment = self._transform_deployment(greenDeployment)
        if self.wrapper_data.is_support_blue_green_deployment(app):
            logger.warning(f"Action Needed: you should manually deploy the deployment '{greenDeployment.get('name')}' of app '{app.get('name')}' in Azure Container Apps.")
        tier = blueDeployment.get('sku', {}).get('tier')
        serviceBinds = self._get_service_bind(app)
        ingress = self._get_ingress(app, tier)
        isPublic = app['properties'].get('public')
        identity = app.get('identity')
        volumeMounts = []
        volumes = []
        if 'properties' in app and 'customPersistentDisks' in app['properties']:
            disks = app['properties']['customPersistentDisks']
            for disk_props in disks:
                volume_name = self._get_storage_name(disk_props)
                volumeMounts.append({
                    "volumeName": volume_name,
                    "mountPath": self._get_storage_mount_path(disk_props),
                })
                volumes.append({
                    "volumeName": volume_name,
                    "storageName": self._get_storage_unique_name(disk_props),
                    "mountOptions": self._get_mount_options(disk_props),
                })
        return {
            "containerAppName": self._get_resource_name(app),
            "paramContainerAppImageName": self._get_param_name_of_container_image(app),
            "paramTargetPort": self._get_param_name_of_target_port(app),
            "moduleName": self._get_app_module_name(app),
            "ingress": ingress,
            "isPublic": isPublic,
            "minReplicas": 1,
            "maxReplicas": blueDeployment.get("capacity", 5),
            "serviceBinds": serviceBinds,
            "blue": blueDeployment,
            "green": greenDeployment,
            "isBlueGreen": self.wrapper_data.is_support_blue_green_deployment(app),
            "identity": identity,
            "volumeMounts": volumeMounts,
            "volumes": volumes,
        }

    def get_template_name(self):
        return "app.bicep"

    def _get_service_bind(self, app):
        service_bind = []
        envName = self._get_parent_resource_name(app)
        if self.wrapper_data.is_support_configserver_for_app(app):
            service_bind.append({
                "name": "bind-config",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'config')"
            })
        if self.wrapper_data.is_enterprise_tier() is not True and self.wrapper_data.is_support_ossconfigserver():
            # standard tier enabled config server and bind all apps automatically
            service_bind.append({
                "name": "bind-config",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'config')"
            })
        if self.wrapper_data.is_support_serviceregistry_for_app(app):
            service_bind.append({
                "name": "bind-eureka",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'eureka')"
            })
        if self.wrapper_data.is_enterprise_tier() is not True and self.wrapper_data.is_support_eureka():
            # standard tier enabled eureka server and bind all apps automatically
            service_bind.append({
                "name": "bind-eureka",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'eureka')"
            })
        if self.wrapper_data.is_support_sba():
            service_bind.append({
                "name": "bind-sba",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'admin')"
            })
        return service_bind

    def _transform_deployment(self, deployment):
        if deployment is None or deployment == {}:
            return
        env = deployment.get('properties', {}).get('deploymentSettings', {}).get('environmentVariables', {})
        liveness_probe = deployment.get('properties', {}).get('deploymentSettings', {}).get('livenessProbe', {})
        readiness_probe = deployment.get('properties', {}).get('deploymentSettings', {}).get('readinessProbe', {})
        startup_probe = deployment.get('properties', {}).get('deploymentSettings', {}).get('startupProbe', {})
        resource_requests = deployment.get('properties', {}).get('deploymentSettings', {}).get('resourceRequests', {})
        cpuCore = float(resource_requests.get("cpu").replace("250m", "0.25").replace("500m", "0.5"))
        memorySize = resource_requests.get("memory")
        tier = deployment.get('sku', {}).get('tier')
        scale = deployment.get('properties', {}).get('deploymentSettings', {}).get('scale', {})
        capacity = deployment.get('sku', {}).get('capacity')
        return {
            "name": self._get_resource_name(deployment),
            "env": self._convert_env(env),
            "livenessProbe": self._convert_probe(liveness_probe, tier, deployment),
            "readinessProbe": self._convert_probe(readiness_probe, tier, deployment),
            "startupProbe": self._convert_probe(startup_probe, tier, deployment),
            "cpuCore": cpuCore,
            "memorySize": self._get_memory_by_cpu(cpuCore, memorySize, deployment) or memorySize,
            "scale": self._convert_scale(scale),
            "capacity": capacity,
        }

    def _convert_env(self, env):
        env_list = []
        for key, value in env.items():
            env_list.append({
                "name": key,
                "value": value
            })
        return env_list

    # A Container App must add up to one of the following CPU - Memory combinations:
    # [cpu: 0.25, memory: 0.5Gi]; [cpu: 0.5, memory: 1.0Gi]; [cpu: 0.75, memory: 1.5Gi]; [cpu: 1.0, memory: 2.0Gi]; [cpu: 1.25, memory: 2.5Gi]; [cpu: 1.5, memory: 3.0Gi]; [cpu: 1.75, memory: 3.5Gi]; [cpu: 2.0, memory: 4.0Gi]; [cpu: 2.25, memory: 4.5Gi]; [cpu: 2.5, memory: 5.0Gi]; [cpu: 2.75, memory: 5.5Gi]; [cpu: 3, memory: 6.0Gi]; [cpu: 3.25, memory: 6.5Gi]; [cpu: 3.5, memory: 7Gi]; [cpu: 3.75, memory: 7.5Gi]; [cpu: 4, memory: 8Gi]
    def _get_memory_by_cpu(self, cpu, asa_memory_size, deployment):
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
        if cpu_memory_map.get(cpu, None) is None:
            logger.warning(f"Mismatch: The CPU '{cpu}' and Memory '{asa_memory_size}' combination of app '{deployment.get('name')}' is not supported in Azure Container Apps.")
        elif asa_memory_size != cpu_memory_map.get(cpu, None):
            logger.warning(f"Mismatch: The Memory '{asa_memory_size}' of app '{deployment.get('name')}' is not supported in Azure Container Apps. Converting it to '{cpu_memory_map.get(cpu, None)}'.")

        return cpu_memory_map.get(cpu, None)

    # create a method _convert_probe to convert the probe from the source to the target format
    def _convert_probe(self, probe, tier, deployment):
        if probe is None:
            return None
        if probe.get("disableProbe") is True:
            logger.debug("Probe is disabled")
            return None
        result = {}
        initialDelaySeconds = probe.get("initialDelaySeconds", None)
        if initialDelaySeconds is not None:
            if initialDelaySeconds > 60:  # Container 'undefined' 'Type' probe's InitialDelaySeconds must be in the range of ['0', '60'].
                logger.warning(f"Mismatch: The initialDelaySeconds '{initialDelaySeconds}' of health probe of app '{deployment.get('name')}' must be in the range of ['0', '60'] in Azure Container Apps. Converting it to 60.")
                initialDelaySeconds = 60
            result['initialDelaySeconds'] = initialDelaySeconds
        periodSeconds = probe.get("periodSeconds", None)
        if periodSeconds is not None:
            result['periodSeconds'] = periodSeconds
        timeoutSeconds = probe.get("timeoutSeconds", None)
        if timeoutSeconds is not None:
            result['timeoutSeconds'] = timeoutSeconds
        successThreshold = probe.get("successThreshold", None)
        if successThreshold is not None:
            result['successThreshold'] = successThreshold
        failureThreshold = probe.get("failureThreshold", None)
        if failureThreshold is not None:
            result['failureThreshold'] = failureThreshold
        httpGet = self._convert_http_probe_action(probe, tier)
        if httpGet is not None:
            result["httpGet"] = httpGet
        tcpSocket = self._convert_tcp_probe_action(probe, tier)
        if tcpSocket is not None:
            result["tcpSocket"] = tcpSocket
        execAction = self._convert_exec_probe_action(probe, tier)
        if execAction is not None:
            logger.warning(f"Mismatch: The ExecAction '{execAction}' of health probe is not supported in Azure Container Apps.")
        return None if result == {} else result

    def _convert_exec_probe_action(self, probe, tier):
        probeAction = {}
        if probe.get("probeAction", {}).get("type") == "ExecAction":
            probeAction = {
                "command": probe.get("probeAction", {}).get("command"),
            }
        else:
            probeAction = None
        return probeAction

    def _convert_tcp_probe_action(self, probe, tier):
        probeAction = {}
        if probe.get("probeAction", {}).get("type") == "TCPSocketAction":
            probeAction = {
                "port": 8080 if tier == "Enterprise" else 1025,
            }
        else:
            probeAction = None
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
        return probeAction

    def _get_ingress(self, app, tier):
        ingress = app['properties'].get('ingressSettings')
        if ingress is None:
            return None
        return {
            "targetPort": 8080 if tier == "Enterprise" else 1025,
            "transport": ingress.get('backendProtocol').replace("Default", "auto"),
            "sessionAffinity": ingress.get('sessionAffinity').replace("Cookie", "sticky").replace("None", "none")
        }

    def _convert_scale(self, scale):
        return {
            "minReplicas": scale.get("minReplicas", 1),
            "maxReplicas": scale.get("maxReplicas", 5),
            "rules": scale.get("rules", [])
        }
