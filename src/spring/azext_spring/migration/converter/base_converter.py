# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
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
        self.transform_data = transform_data

    def convert(self):
        result = {}
        self.data = self.transform_data()
        if (isinstance(self.data, list)):
            result = self._convert_many()
            # for key in result.keys():
            #   logger.debug(f"converted contents of {self.__class__.__name__} for {key}:\n{result.get(key)}")
        else:
            result = self._convert_one()
            # logger.debug(f"converted contents of {__class__.__name__}:\n{result.get(self.get_template_name())}")
        return result

    def _convert_one(self):
        outputs = {}
        if self.data is not None and isinstance(self.data, dict):
            outputs[self.get_template_name()] = self.generate_output(self.data)
        return outputs

    def _convert_many(self):
        outputs = {}
        if self.data is not None and isinstance(self.data, list) and len(self.data) > 0:
            for item in self.data:
                name = item['name'].split('/')[-1]
                data = self.transform_data_item(item)
                outputs[name + "_" + self.get_template_name()] = self.generate_output(data)
        return outputs

    @abstractmethod
    def get_template_name(self):
        pass

    def generate_output(self, data):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_name = self.get_template_name().lower()
        with open(f"{script_dir}/templates/{template_name}.j2") as file:
            template = Template(file.read())
        return template.render(data=data)


# Base Converter Class
# The BaseConverter class provides common utility methods that can be used by all concrete converter classes
class BaseConverter(ConverterTemplate):

    # common
    def _get_resource_name(self, resource):
        return resource['name'].split('/')[-1]

    def _get_parent_resource_name(self, resource):
        parts = resource['name'].split('/')
        return parts[-2] if len(parts) > 1 else ''

    # Extracts the resource name from a resource ID string in Azure ARM template format
    # Format: [resourceId('Microsoft.AppPlatform/Spring/<ResourceType>', '<parent_resource_name>', '<resource_name>')]
    # Example input: [resourceId('Microsoft.AppPlatform/Spring/storages', 'sample-service', 'storage1')]
    # Returns: 'storage1'
    def _get_name_from_resource_id(self, resource_id):
        # Extract content between square brackets
        content = resource_id.strip('[]').strip('resourceId()')
        # Split by comma and get the last parameter
        params = content.split(',')
        # Return the last parameter stripped of quotes and whitespace
        result = params[-1].strip().strip("'") if params else ''
        # print(f"Resource name: {result}")
        return result

# storage
    def _get_storage_name(self, disk_props):
        storage_id = disk_props.get('storageId', '')
        return self._get_name_from_resource_id(storage_id) if storage_id else ''

    def _get_storage_mount_path(self, disk_props):
        return disk_props.get('customPersistentDiskProperties').get('mountPath')

    def _get_storage_share_name(self, disk_props):
        return disk_props.get('customPersistentDiskProperties', '').get('shareName', '')

    def _get_storage_access_mode(self, disk_props):
        readOnly = disk_props.get('customPersistentDiskProperties', False).get('readOnly', False)
        return 'ReadOnly' if readOnly else 'ReadWrite'

    def _get_storage_account_name(self, disk_props):
        storages = self.wrapper_data.get_storages()
        storage_map = {
            self._get_resource_name(storage): storage['properties']['accountName']
            for storage in storages
        }
        storage_name = self._get_storage_name(disk_props)
        return storage_map.get(storage_name, '')

    def _get_storage_unique_name(self, disk_props):
        storage_name = self._get_storage_name(disk_props)
        account_name = self._get_storage_account_name(disk_props)
        share_name = self._get_storage_share_name(disk_props)
        mount_path = self._get_storage_mount_path(disk_props)
        access_mode = self._get_storage_access_mode(disk_props)
        storage_unique_name = f"{storage_name}|{account_name}|{share_name}|{mount_path}|{access_mode}"
        hash_value = hashlib.md5(storage_unique_name.encode()).hexdigest()[:16]  # Take first 16 chars of hash
        result = f"{storage_name}{hash_value}"
        return result[:32]  # Ensure total length is no more than 32

    def _get_mount_options(self, disk_props):
        mountOptions = self.DEFAULT_MOUNT_OPTIONS
        if disk_props.get('customPersistentDiskProperties').get('mountOptions') is not None \
                and len(disk_props.get('customPersistentDiskProperties').get('mountOptions')) > 0:
            mountOptions = ""
            for option in disk_props.get('customPersistentDiskProperties').get('mountOptions'):
                mountOptions += ("," if mountOptions != "" else "") + option
        # print("Mount options: ", mountOptions)
        return mountOptions

    def _get_storage_enable_subpath(self, disk_props):
        enableSubPath = disk_props.get('customPersistentDiskProperties', False).get('enableSubPath', False)
        return enableSubPath

# module name
    def _get_app_module_name(self, app):
        appName = self._get_resource_name(app)
        return appName.replace("-", "_")

    def _get_cert_module_name(self, cert):
        certName = self._get_resource_name(cert)
        return "cert_" + certName.replace("-", "_")

# param name
    # get param name of paramContainerAppImageName
    def _get_param_name_of_container_image(self, app):
        appName = self._get_resource_name(app)
        return "containerImageOf_" + appName.replace("-", "_")

    # get param name of paramTargetPort
    def _get_param_name_of_target_port(self, app):
        appName = self._get_resource_name(app)
        return "targetPortOf_" + appName.replace("-", "_")

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
        return self.is_support_ossconfigserver() or self.is_support_acs()

    def is_support_configserver_for_app(self, app):
        return self.is_support_ossconfigserver_for_app(app) or self.is_support_acs_for_app(app)

    def is_support_ossconfigserver(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/configServers')

    def is_support_ossconfigserver_for_app(self, app):
        addon = app['properties'].get('addonConfigs')
        if addon is None:
            return False
        return addon.get('configServer') is not None and addon['configServer'].get('resourceId') is not None

    def is_support_acs(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/configurationServices')

    def is_support_acs_for_app(self, app):
        addon = app['properties'].get('addonConfigs')
        if addon is None:
            return False
        return addon.get('applicationConfigurationService') is not None and addon['applicationConfigurationService'].get('resourceId') is not None

    def is_support_eureka(self):
        return self.is_support_serviceregistry() or not self.is_enterprise_tier()

    def is_support_serviceregistry(self):
        return self.is_support_feature('Microsoft.AppPlatform/Spring/serviceRegistries')

    def is_support_serviceregistry_for_app(self, app):
        addon = app['properties'].get('addonConfigs')
        if addon is None:
            return False
        return addon.get('serviceRegistry') is not None and addon['serviceRegistry'].get('resourceId') is not None

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

    def get_deployments_by_app(self, app):
        deployments = self.get_deployments()
        return [deployment for deployment in deployments if deployment['name'].startswith(f"{app['name']}/")]

    def get_blue_deployment_by_app(self, app):
        deployments = self.get_deployments_by_app(app)
        deployments = [deployment for deployment in deployments if deployment['properties']['active'] is True]
        return deployments[0] if deployments else {}

    def get_green_deployment_by_app(self, app):
        deployments = self.get_deployments_by_app(app)
        deployments = [deployment for deployment in deployments if deployment['properties']['active'] is False]
        return deployments[0] if deployments else {}

    def get_green_deployments(self):
        deployments = self.get_deployments()
        deployments = [deployment for deployment in deployments if deployment['properties']['active'] is False]
        return deployments if deployments else []

    def get_build_results_deployments(self):
        deployments = []
        deployments = self.get_deployments()
        deployments = [deployment for deployment in deployments if deployment['properties'].get('source', {}).get('type', {}) == "BuildResult"]
        return deployments

    def get_container_deployments(self):
        deployments = []
        deployments = self.get_deployments()
        deployments = [deployment for deployment in deployments if deployment['properties'].get('source', {}).get('type', {}) == "Container"]
        return deployments

    def is_support_blue_green_deployment(self, app):
        return len(self.get_deployments_by_app(app)) > 1

    def get_custom_domains(self):
        return self.get_resources_by_type('Microsoft.AppPlatform/Spring/apps/domains')

    def get_custom_domains_by_app(self, app):
        domains = self.get_custom_domains(self)
        return [domain for domain in domains if domain['name'].startswith(f"{app['name']}/")]

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

    def is_enabled_system_assigned_identity_for_app(self, app):
        identity = app.get('identity')
        if identity is None:
            return False
        return identity.get('type') == 'SystemAssigned'
