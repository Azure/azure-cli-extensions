import re

from knack.log import get_logger
from .base_converter import ConverterTemplate

logger = get_logger(__name__)

# Concrete Converter Subclass for Container App
class AppConverter(ConverterTemplate):
    
    DEFAULT_MOUNT_OPTIONS = "uid=0,gid=0,file_mode=0777,dir_mode=0777"

    def load_source(self, source):
        self.source = source
        self.managed_components = source['managedComponents']
        self.is_enterprise = source['isEnterprise']
        # print(f"App source: {self.source}")

    def calculate_data(self):
        appName = self.source['name'].split('/')[-1]
        envName = self.source['name'].split('/')[0]
        moduleName = appName.replace("-", "_")
        serviceBinds = self._get_service_bind(self.source, envName)
        deployments = self._get_deployments(self.source)
        blueDeployment = deployments[0] if len(deployments) > 0 else {}
        greenDeployment = deployments[1] if len(deployments) > 1 else {}
        tier = blueDeployment.get('sku', {}).get('tier')
        ingress = self._get_ingress(self.source, tier)
        isPublic = self.source['properties'].get('public')
        identity = self.source.get('identity')
        storages = self.source.get('storages')
        # print(f"App name: {appName}, Module name: {moduleName}, Ingress: {ingress}, IsPublic: {isPublic}, Identity: {identity}")
        volumeMounts = []
        volumes = []
        if 'properties' in self.source and 'customPersistentDisks' in self.source['properties']:
            disks = self.source['properties']['customPersistentDisks']
            storage_map = {
                storage['name'].split('/')[-1]: storage['properties']['accountName'] 
                for storage in storages
            }
            for disk_props in disks:
                # print(f"Disk props: {disk_props}")
                storage_id = disk_props.get('storageId', '')
                storage_name = self._get_resource_name(storage_id) if storage_id else ''
                # print("Storage name: ", storage_name)
                mountOptions = self.DEFAULT_MOUNT_OPTIONS
                if disk_props.get('customPersistentDiskProperties').get('mountOptions') is not None and \
                    len(disk_props.get('customPersistentDiskProperties').get('mountOptions')) > 0:
                    mountOptions = ""
                    for option in disk_props.get('customPersistentDiskProperties').get('mountOptions'):
                        mountOptions += ("," if mountOptions != "" else "") + option  
                account_name = storage_map.get(storage_name, '')
                mount_path = disk_props.get('customPersistentDiskProperties').get('mountPath')
                readOnly = disk_props.get('customPersistentDiskProperties', False).get('readOnly', False)
                share_name = disk_props.get('customPersistentDiskProperties', '').get('shareName', '')
                access_mode = 'ReadOnly' if readOnly else 'ReadWrite'
                storage_unique_name = self._get_storage_unique_name(storage_name, account_name, share_name, mount_path, access_mode)
                # print("Mount options: ", mountOptions)
                volumeMounts.append({
                    "volumeName": storage_name,
                    "mountPath": mount_path,
                })
                volumes.append({
                    "volumeName": storage_name,
                    "storageName": storage_unique_name,
                    "mountOptions": mountOptions,
                })
        # print("Volume mounts: ", volumeMounts)
        # print("Volumes: ", volumes)
        self.data = {
            "containerAppName": appName,
            "containerAppImageName": "containerImageFor_"+appName.replace("-", "_"),
            "targetPort": "targetPortFor_"+appName.replace("-", "_"),
            "moduleName": moduleName,
            "ingress": ingress,
            "isPublic": isPublic,
            "minReplicas": 1,
            "maxReplicas": blueDeployment.get("capacity", 5),
            "serviceBinds": serviceBinds,
            "blue": blueDeployment,
            "green": greenDeployment,
            "isBlueGreen": len(deployments) > 1,
            "identity": identity,
            "volumeMounts": volumeMounts,
            "volumes": volumes,
        }

    def get_template_name(self):
        return "app.bicep"
    
    def get_app_name(input_string):
        return input_string.split('/')[-1]

    def _get_service_bind(self, source, envName):
        enable_sba = self.managed_components['sba']
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
        if self.is_enterprise != True and self.managed_components['config'] == True:
            # standard tier enabled config server and bind all apps automatically
            service_bind.append({
                "name": "bind-config",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'config')"
            })
        if addon.get('serviceRegistry') is not None and addon['serviceRegistry'].get('resourceId') is not None:
            service_bind.append({
                "name": "bind-eureka",
                "serviceId": f"resourceId('Microsoft.App/managedEnvironments/javaComponents', '{envName}', 'eureka')"
            })
        if self.is_enterprise != True and self.managed_components['eureka'] == True:
            # standard tier enabled eureka server and bind all apps automatically
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
            startup_probe = deployment.get('properties', {}).get('deploymentSettings', {}).get('startupProbe', {})
            resource_requests = deployment.get('properties', {}).get('deploymentSettings', {}).get('resourceRequests', {})
            cpuCore = float(resource_requests.get("cpu").replace("250m", "0.25").replace("500m", "0.5"))
            memorySize = resource_requests.get("memory")
            tier = deployment.get('sku', {}).get('tier')
            scale = deployment.get('properties', {}).get('deploymentSettings', {}).get('scale', {})
            capacity = deployment.get('sku', {}).get('capacity')
            deployment = {
                "name": deployment_name,
                "env": self._convert_env(env),
                "livenessProbe": self._convert_probe(liveness_probe, tier),
                "readinessProbe": self._convert_probe(readiness_probe, tier),
                "startupProbe": self._convert_probe(startup_probe, tier),
                "cpuCore": cpuCore,
                "memorySize": self._get_memory_by_cpu(cpuCore) or memorySize,
                "scale": self._convert_scale(scale),
                "capacity": capacity,
            }
            deployments.append(deployment)

        # print(f"deployments: {deployments}")
        return deployments

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
            logger.debug(f"Probe is disabled")
            return None
        result = {}
        initialDelaySeconds = probe.get("initialDelaySeconds", None)
        if initialDelaySeconds is not None:
            if initialDelaySeconds > 60: # Container 'undefined' 'Type' probe's InitialDelaySeconds must be in the range of ['0', '60'].
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
            logger.warning(f"Mismatch: The ExecAction {execAction} is not supported in Azure Container Apps.")
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

    def _get_ingress(self, source, tier):
        ingress = source['properties'].get('ingressSettings')
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
