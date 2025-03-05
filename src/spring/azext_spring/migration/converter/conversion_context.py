import os

from abc import ABC, abstractmethod
from knack.log import get_logger
from .base_converter import ConverterTemplate
from .environment_converter import EnvironmentConverter
from .app_converter import AppConverter
from .readme_converter import ReadMeConverter
from .main_converter import MainConverter
from .param_converter import ParamConverter
from .gateway_converter import GatewayConverter
from .eureka_converter import EurekaConverter
from .service_registry_converter import ServiceRegistryConverter
from .config_server_converter import ConfigServerConverter
from .acs_converter import ACSConverter
from .live_view_converter import LiveViewConverter
from .cert_converter import CertConverter

logger = get_logger(__name__)

# Context Class
class ConversionContext:
    def __init__(self):
        self.converters = []

    def add_converter(self, converter: ConverterTemplate):
        self.converters.append(converter)

    def get_converter(self, converter_type: type):
        for converter in self.converters:
            if isinstance(converter, converter_type):
                return converter
        raise ValueError(f"Unknown converter type: {converter_type}")

    def set_params_for_converter(self, converter_type, params):
        for converter in self.converters:
            if isinstance(converter, converter_type):
                converter.set_params(params)

    def run_converters(self, source):
        converted_contents = {}
        source_wrapper = SourceDataWrapper(source)
        asa_service = source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring')[0]
        asa_apps = source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/apps')
        storages = source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/storages')

        # Environment Converter
        is_vnet = self._is_vnet(asa_service)
        is_enterprise = self._is_enterprise_tier(asa_service)
        asa_service['isVnet'] = is_vnet
        asa_service['apps'] = asa_apps
        asa_service['storages'] = storages
        

        # Cert Converter
        asa_certs = source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/certificates')
        asa_kv_certs = []
        for cert in asa_certs:
            certName = cert['name'].split('/')[-1]
            if cert['properties'].get('type') == "KeyVaultCertificate":
                asa_kv_certs.append(cert)
                converted_contents[certName+"_"+self.get_converter(CertConverter).get_template_name()] = self.get_converter(CertConverter).convert(cert)
            elif cert['properties'].get('type') == "ContentCertificate":
                converted_contents[certName+"_"+self.get_converter(CertConverter).get_template_name()] = self.get_converter(CertConverter).convert(cert)
        converted_contents[self.get_converter(EnvironmentConverter).get_template_name()] = self.get_converter(EnvironmentConverter).convert(asa_service)
        # Managed components Converter
        managed_components = {
            'gateway': False,
            'config': False,
            'eureka': False,
            'sba': False,
        }
        converted_contents = self._convert_gateway(source_wrapper, converted_contents, managed_components)
        converted_contents = self._convert_config_server_and_ACS(source_wrapper, converted_contents, managed_components)
        converted_contents = self._convert_live_view(source_wrapper, converted_contents, managed_components)
        converted_contents = self._convert_eureka_and_service_registry(source_wrapper, converted_contents, asa_service, managed_components)

        asa_deployments = source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/apps/deployments')
        for app_source in asa_apps:
            appName = app_source['name'].split('/')[-1]
            app_source['deployments'] = [deployment for deployment in asa_deployments if deployment['name'].startswith(f"{app_source['name']}/")]
            app_source['managedComponents'] = managed_components
            app_source['isEnterprise'] = is_enterprise
            app_source['storages'] = storages
            converted_contents[appName+"_"+self.get_converter(AppConverter).get_template_name()] = self.get_converter(AppConverter).convert(app_source)

        # Param, readme and main Converter
        full_source = {
            "asa": asa_service,
            "apps": asa_apps,
            "certs": asa_kv_certs,
            "managedComponents": managed_components,
            "isVnet": is_vnet,
            "inEnterprise": is_enterprise,
            "storages": storages,
        }

        converted_contents[self.get_converter(ParamConverter).get_template_name()] = self.get_converter(ParamConverter).convert(full_source)
        converted_contents[self.get_converter(ReadMeConverter).get_template_name()] = self.get_converter(ReadMeConverter).convert(full_source)
        converted_contents[self.get_converter(MainConverter).get_template_name()] = self.get_converter(MainConverter).convert(full_source)

        return converted_contents

    def save_to_files(self, converted_contents, output_path):
        logger.debug(f"Start to save the converted content to files in folder {os.path.abspath(output_path)}...")
        os.makedirs(os.path.abspath(output_path), exist_ok=True)

        for filename, content in converted_contents.items():
            output_filename = os.path.join(output_path, filename)
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                logger.info(f"Generating the file {output_filename}...")
                output_file.write(content)

    def _convert_gateway(self, source_wrapper, converted_contents, managed_components):
        for gateway in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways'):
            managed_components['gateway'] = True
            gateway_key = self.get_converter(GatewayConverter).get_template_name()
            routes = []
            for gateway_route in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways/routeConfigs'):
                routes.append(gateway_route)
            gateway_source = {
                "gateway": gateway,
                "routes": routes,
            }
            converted_contents[gateway_key] = self.get_converter(GatewayConverter).convert(gateway_source)
            logger.info(f"converted_contents for gateway: {converted_contents[gateway_key]}")
        return converted_contents

    def _convert_config_server_and_ACS(self, source_wrapper, converted_contents, managed_components):
        enabled_config_server = False

        for config_server in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/configServers'):
            managed_components['config'] = True
            enabled_config_server = True
            config_key = self.get_converter(ConfigServerConverter).get_template_name()
            converted_contents[config_key] = self.get_converter(ConfigServerConverter).convert(config_server)
            logger.debug(f"converted_contents for config server: {converted_contents[config_key]}")

        if not enabled_config_server:
            for acs in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/configurationServices'):
                managed_components['config'] = True
                config_key = self.get_converter(ACSConverter).get_template_name()
                converted_contents[config_key] = self.get_converter(ACSConverter).convert(acs)
                logger.debug(f"converted_contents for Application Configuration Service: {converted_contents[config_key]}")

        return converted_contents

    def _convert_live_view(self, source_wrapper, converted_contents, managed_components):
        for live_view in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/applicationLiveViews'):
            managed_components['sba'] = True
            live_view_key = self.get_converter(LiveViewConverter).get_template_name()
            converted_contents[live_view_key] = self.get_converter(LiveViewConverter).convert(live_view)
            logger.info(f"converted_contents for Live View: {converted_contents[live_view_key]}")
        return converted_contents

    def _convert_eureka_and_service_registry(self, source_wrapper, converted_contents, asa_service, managed_components):
        is_enterprise_tier = self._is_enterprise_tier(asa_service)
        for service_registry in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/serviceRegistries'):
            managed_components['eureka'] = True
            eureka_key = self.get_converter(ServiceRegistryConverter).get_template_name()
            converted_contents[eureka_key] = self.get_converter(ServiceRegistryConverter).convert(service_registry)
            logger.info(f"converted_contents for Service Registry: {converted_contents[eureka_key]}")
            return converted_contents

        if not is_enterprise_tier:
            managed_components['eureka'] = True
            eureka_key = self.get_converter(EurekaConverter).get_template_name()
            converted_contents[eureka_key] = self.get_converter(EurekaConverter).convert(None)
        return converted_contents

    def _is_enterprise_tier(self, asa_service):
        return asa_service['sku']['tier'] == 'Enterprise'

    def _is_vnet(self, asa_service):
        networkProfile = asa_service['properties'].get('networkProfile')
        if networkProfile is None:
            return False
        return networkProfile.get('appSubnetId') is not None

class SourceDataWrapper:
    def __init__(self, source):
        self.source = source

    def get_resources_by_type(self, resource_type):
        return [resource for resource in self.source['resources'] if resource['type'] == resource_type]
