import os

from abc import ABC, abstractmethod
from knack.log import get_logger
from .base_converter import ConverterTemplate
from .environment_converter import EnvironmentConverter
from .app_converter import AppConverter
from .revision_converter import RevisionConverter
from .readme_converter import ReadMeConverter
from .main_converter import MainConverter
from .param_converter import ParamConverter
from .gateway_converter import GatewayConverter
from .eureka_converter import EurekaConverter
from .service_registry_converter import ServiceRegistryConverter
from .config_server_converter import ConfigServerConverter
from .acs_converter import ACSConverter
from .live_view_converter import LiveViewConverter

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
        converted_contents[self.get_converter(MainConverter).get_template_name()] = self.get_converter(MainConverter).convert(
            source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/apps')
        )
        converted_contents[self.get_converter(EnvironmentConverter).get_template_name()] = self.get_converter(EnvironmentConverter).convert(
            source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring')[0]
        )

        asa_service = source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring')[0]

        for app in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/apps'):
            appName = app['name'].split('/')[-1]
            converted_contents[appName+"_"+self.get_converter(AppConverter).get_template_name()] = self.get_converter(AppConverter).convert(app)

        # converted_contents.append(
        #     self.get_converter(RevisionConverter).convert(
        #         source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/apps/deployments')
        #     )
        # )
        converted_contents[self.get_converter(ParamConverter).get_template_name()] = self.get_converter(ParamConverter).convert(None)
        converted_contents[self.get_converter(ReadMeConverter).get_template_name()] = self.get_converter(ReadMeConverter).convert(None)

        converted_contents = self._convert_gateway(source_wrapper, converted_contents)
        converted_contents = self._convert_config_server_and_ACS(source_wrapper, converted_contents)
        converted_contents = self._convert_live_view(source_wrapper, converted_contents)
        converted_contents = self._convert_eureka_and_service_registry(source_wrapper, converted_contents, asa_service)

        return converted_contents

    def save_to_files(self, converted_contents, output_path):
        logger.debug(f"Start to save the converted content to files in folder {os.path.abspath(output_path)}...")
        os.makedirs(os.path.abspath(output_path), exist_ok=True)

        for filename, content in converted_contents.items():
            output_filename = os.path.join(output_path, filename)
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                logger.info(f"Generating the file {output_filename}...")
                output_file.write(content)

    def _convert_gateway(self, source_wrapper, converted_contents):
        for gateway in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways'):
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

    def _convert_config_server_and_ACS(self, source_wrapper, converted_contents):
        enabled_config_server = False

        for config_server in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/configServers'):
            enabled_config_server = True
            config_key = self.get_converter(ConfigServerConverter).get_template_name()
            converted_contents[config_key] = self.get_converter(ConfigServerConverter).convert(config_server)
            logger.debug(f"converted_contents for config server: {converted_contents[config_key]}")

        if not enabled_config_server:
            for acs in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/configurationServices'):
                config_key = self.get_converter(ACSConverter).get_template_name()
                converted_contents[config_key] = self.get_converter(ACSConverter).convert(acs)
                logger.debug(f"converted_contents for Application Configuration Service: {converted_contents[config_key]}")

        return converted_contents

    def _convert_live_view(self, source_wrapper, converted_contents):
        for live_view in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/applicationLiveViews'):
            live_view_key = self.get_converter(LiveViewConverter).get_template_name()
            converted_contents[live_view_key] = self.get_converter(LiveViewConverter).convert(live_view)
            logger.info(f"converted_contents for Live View: {converted_contents[live_view_key]}")
        return converted_contents

    def _convert_eureka_and_service_registry(self, source_wrapper, converted_contents, asa_service):
        is_enterprise_tier = self._is_enterprise_tier(asa_service)
        for service_registry in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/serviceRegistries'):
            eureka_key = self.get_converter(ServiceRegistryConverter).get_template_name()
            converted_contents[eureka_key] = self.get_converter(ServiceRegistryConverter).convert(service_registry)
            logger.info(f"converted_contents for Service Registry: {converted_contents[eureka_key]}")
            return converted_contents

        if not is_enterprise_tier:
            eureka_key = self.get_converter(EurekaConverter).get_template_name()
            converted_contents[eureka_key] = self.get_converter(EurekaConverter).convert()
            return converted_contents

    def _is_enterprise_tier(self, asa_service):
        return asa_service['sku']['tier'] == 'Enterprise'

class SourceDataWrapper:
    def __init__(self, source):
        self.source = source

    def get_resources_by_type(self, resource_type):
        return [resource for resource in self.source['resources'] if resource['type'] == resource_type]
