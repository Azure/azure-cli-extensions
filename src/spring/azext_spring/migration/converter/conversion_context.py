import os

from abc import ABC, abstractmethod
from jinja2 import Template
from .base_converter import ConverterTemplate
from .environment_converter import EnvironmentConverter
from .app_converter import AppConverter
from .revision_converter import RevisionConverter
from .readme_converter import ReadMeConverter
from .main_converter import MainConverter
from .param_converter import ParamConverter
from .gateway_converter import GatewayConverter

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

        for gateway in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways'):
            gateway_name = gateway['name'].split('/')[-1]
            gateway_key = gateway_name+"_"+self.get_converter(GatewayConverter).get_template_name()
            routes = []
            for gateway_route in source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways/routeConfigs'):
                routes.append(gateway_route)
            gateway_source = {
                "gateway": gateway,
                "routes": routes,
            }
            converted_contents[gateway_key] = self.get_converter(GatewayConverter).convert(gateway_source)
            print("converted_contents for gateway: \n", converted_contents[gateway_key])
            break

        return converted_contents

    def save_to_files(self, converted_contents, output_path):
        print("Start to save the converted content to files ...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        for filename, content in converted_contents.items():
            output_filename = os.path.join(output_path, filename)
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                print(f"Start to generate the {output_filename} file ...")
                output_file.write(content)

class SourceDataWrapper:
    def __init__(self, source):
        self.source = source

    def get_resources_by_type(self, resource_type):
        return [resource for resource in self.source['resources'] if resource['type'] == resource_type]