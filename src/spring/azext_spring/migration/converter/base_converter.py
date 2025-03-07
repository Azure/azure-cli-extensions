import hashlib
import os

from knack.log import get_logger
from abc import ABC, abstractmethod
from jinja2 import Template

logger = get_logger(__name__)

# Abstract Base Class for Converter
# The converter is a template class that defines the structure of the conversion process
# The responsibility of the converter is to convert the source data into the output data
class ConverterTemplate(ABC):
    def __init__(self, source, transform_data):
        self.wrapper_data = SourceDataWrapper(source)
        self.data = transform_data()

    def convert(self):
        outputs = {}
        outputs[self.get_template_name()] =self.generate_output(self.data)
        return outputs

    def convert_many(self):
        outputs = {}
        for item in self.data:
            name = item['name'].split('/')[-1]
            data = self.transform_data_item(item)
            outputs[name+"_"+self.get_template_name()] = self.generate_output(data)
        return outputs

    @abstractmethod
    def get_template_name(self):
        pass

    def generate_output(self, data):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_name = self.get_template_name()
        with open(f"{script_dir}/templates/{template_name}.j2") as file:
            template = Template(file.read())
        return template.render(data=data)

# Base Converter Class
# The BaseConverter class provides common utility methods that can be used by all concrete converter classes
class BaseConverter(ConverterTemplate):
    # Extracts the resource name from a resource ID string in Azure ARM template format
    # Format: [resourceId('Microsoft.AppPlatform/Spring/<ResourceType>', '<parent_resource_name>', '<resource_name>')]
    # Example input: [resourceId('Microsoft.AppPlatform/Spring/storages', 'sample-service', 'storage1')]
    # Returns: 'storage1'
    def _get_resource_name(self, resource_id):
        # Extract content between square brackets
        content = resource_id.strip('[]').strip('resourceId()')
        # Split by comma and get the last parameter
        params = content.split(',')
        # Return the last parameter stripped of quotes and whitespace
        result = params[-1].strip().strip("'") if params else ''
        # print(f"Resource name: {result}")
        return result

    def _get_storage_name(self, disk_props):
        storage_id = disk_props.get('storageId', '')
        return self._get_resource_name(storage_id) if storage_id else ''

    def _get_storage_account_name(self, disk_props):
        storages = self.wrapper_data.get_storages()
        storage_map = {
            storage['name'].split('/')[-1]: storage['properties']['accountName'] 
            for storage in storages
        }
        storage_name = self._get_storage_name(disk_props)
        return storage_map.get(storage_name, '')

    def _get_storage_unique_name(self, disk_props):
        storage_name = self._get_storage_name(disk_props)
        account_name = self._get_storage_account_name(disk_props)
        share_name = disk_props.get('customPersistentDiskProperties', '').get('shareName', '')
        mount_path = disk_props.get('customPersistentDiskProperties').get('mountPath')
        readOnly = disk_props.get('customPersistentDiskProperties', False).get('readOnly', False)
        access_mode = 'ReadOnly' if readOnly else 'ReadWrite'
        storage_unique_name = f"{storage_name}|{account_name}|{share_name}|{mount_path}|{access_mode}"
        hash_value = hashlib.md5(storage_unique_name.encode()).hexdigest()[:16]  # Take first 16 chars of hash
        result = f"{storage_name}{hash_value}"
        return result[:32]  # Ensure total length is no more than 32

    # get param name of paramContainerAppImageName
    def _get_param_name_of_container_image(self, app):
        appName = app['name'].split('/')[-1]
        return "containerImageOf_"+appName.replace("-", "_")

    # get param name of paramTargetPort
    def _get_param_name_of_target_port(self, app):
        appName = app['name'].split('/')[-1]
        return "targetPortOf_"+appName.replace("-", "_")
    
    # get param name of paramContainerAppEnvStorageAccountKey
    def _get_param_name_of_storage_account_key(self, disk_props):
        storage_unique_name = self._get_storage_unique_name(disk_props)
        return "containerAppEnvStorageAccountKeyOf_" + storage_unique_name

class SourceDataWrapper:
    def __init__(self, source):
        self.source = source

    def get_resources_by_type(self, resource_type):
        return [resource for resource in self.source['resources'] if resource['type'] == resource_type]
    
    def is_support_feature(self, feature):
        return any(resource['type'] == feature for resource in self.source['resources'])

    def is_support_configserver(self):
        return self.is_support_ssoconfigserver() or self.is_support_acs()

    def is_support_ssoconfigserver(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/configServers')
    
    def is_support_acs(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/configurationServices')
    
    def is_support_eureka(self):
        return self.is_support_serviceregistry() or not self.is_enterprise_tier()
    
    def is_support_serviceregistry(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/serviceRegistries')

    def is_support_sba(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/applicationLiveViews')
    
    def is_support_gateway(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/gateways/routeConfigs')
    
    def get_asa_service(self):
        return self.get_resources_by_type('Microsoft.AppPlatform/Spring')[0]
    
    def get_apps(self):
        return self.get_resources_by_type('Microsoft.AppPlatform/Spring/apps')
    
    def get_deployments(self):
        return self.get_resources_by_type('Microsoft.AppPlatform/Spring/apps/deployments')
        
    def get_deployments_by_app(self, app_name):
        deployments = self.get_deployments()
        return [deployment for deployment in deployments if deployment['name'].startswith(f"{app_name}/")]

    def is_enterprise_tier(self):
        return self.get_asa_service()['sku']['tier'] == 'Enterprise'

    def is_vnet(self):
        networkProfile = self.get_asa_service()['properties'].get('networkProfile')
        if networkProfile is None:
            return False
        return networkProfile.get('appSubnetId') is not None
    
    def get_certificates(self):
        return self.get_resources_by_type('Microsoft.AppPlatform/Spring/certificates')

    def get_keyvault_certificates(self):
        return self.get_certificates_by_type("KeyVaultCertificate")
    
    def get_content_certificates(self):
        return self.get_certificates_by_type("ContentCertificate")
    
    def get_certificates_by_type(self, type):
        certs = []
        for cert in self.get_certificates():
            if cert['properties'].get('type') == type:
                certs.append(cert)
        return certs
    
    def get_storages(self):
        return self.get_resources_by_type('Microsoft.AppPlatform/Spring/storages')