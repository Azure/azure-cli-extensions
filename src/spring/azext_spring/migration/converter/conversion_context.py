import os

from abc import ABC, abstractmethod
from knack.log import get_logger
from .base_converter import ConverterTemplate, SourceDataWrapper
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
    def __init__(self, source):
        self.data_wrapper = SourceDataWrapper(source)
        self.converters = []

    def add_converter(self, converter: ConverterTemplate):
        self.converters.append(converter)

    def get_converter(self, converter_type: type):
        for converter in self.converters:
            if isinstance(converter, converter_type):
                return converter
        raise ValueError(f"Unknown converter type: {converter_type}")

    def run_converters(self):
        converted_contents = {}
        # Cert Converter
        certs = self.get_converter(CertConverter).convert_many()
        converted_contents.update(certs)
        for cert in certs.keys():
            logger.debug(f"converted_contents for cert {cert}:\n{converted_contents.get(cert)}")

        # Environment Converter
        converted_contents.update(self.get_converter(EnvironmentConverter).convert())
        logger.debug(f"converted_contents for environment:\n{converted_contents.get(self.get_converter(EnvironmentConverter).get_template_name())}")

        # Gateway Converter
        if self.data_wrapper.is_support_gateway():
            converted_contents.update(self.get_converter(GatewayConverter).convert())
            logger.debug(f"converted_contents for gateway:\n{converted_contents.get(self.get_converter(GatewayConverter).get_template_name())}")

        # Config Server and ACS Converter
        if self.data_wrapper.is_support_ssoconfigserver():
            converted_contents.update(self.get_converter(ConfigServerConverter).convert())
            logger.debug(f"converted_contents for config server:\n{converted_contents.get(self.get_converter(ConfigServerConverter).get_template_name())}")
        elif self.data_wrapper.is_support_acs():
            converted_contents.update(self.get_converter(ACSConverter).convert())
            logger.debug(f"converted_contents for Application Configuration Service:\n{converted_contents.get(self.get_converter(ACSConverter).get_template_name())}")

        # Live View Converter
        if self.data_wrapper.is_support_sba():
            converted_contents.update(self.get_converter(LiveViewConverter).convert())
            logger.debug(f"converted_contents for Live View:\n{converted_contents.get(self.get_converter(LiveViewConverter).get_template_name())}")

        # Service Registry and Eureka Converter
        if self.data_wrapper.is_enterprise_tier():
            if self.data_wrapper.is_support_service_registry():
                converted_contents.update(self.get_converter(ServiceRegistryConverter).convert())
                logger.debug(f"converted_contents for Service Registry:\n{converted_contents.get(self.get_converter(ServiceRegistryConverter).get_template_name())}")
        else: # Basic Tier or Standard Tier
            converted_contents.update(self.get_converter(EurekaConverter).convert())
            logger.debug(f"converted_contents for Eureka:\n{converted_contents.get(self.get_converter(EurekaConverter).get_template_name())}")

        # App Converter
        apps = self.get_converter(AppConverter).convert_many()
        converted_contents.update(apps)
        for app in apps.keys():
            logger.debug(f"converted_contents for App {app}:\n{converted_contents.get(app)}")        

        # Param Converter
        converted_contents.update(self.get_converter(ParamConverter).convert())
        logger.debug(f"converted_contents for Param:\n{converted_contents.get(self.get_converter(ParamConverter).get_template_name())}")

        # ReadMe Converter
        converted_contents.update(self.get_converter(ReadMeConverter).convert())
        logger.debug(f"converted_contents for ReadMe:\n{converted_contents.get(self.get_converter(ReadMeConverter).get_template_name())}")

        # Main Converter
        converted_contents.update(self.get_converter(MainConverter).convert())
        logger.debug(f"converted_contents for Main:\n{converted_contents.get(self.get_converter(MainConverter).get_template_name())}")
        return converted_contents

    def save_to_files(self, converted_contents, output_path):
        logger.debug(f"Start to save the converted content to files in folder {os.path.abspath(output_path)}...")
        os.makedirs(os.path.abspath(output_path), exist_ok=True)

        for filename, content in converted_contents.items():
            output_filename = os.path.join(output_path, filename)
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                logger.info(f"Generating the file {output_filename}...")
                output_file.write(content)



