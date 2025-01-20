import os

from abc import ABC, abstractmethod
from jinja2 import Template
from .base_converter import ConverterTemplate
from .environment_converter import EnvironmentConverter
from .app_converter import AppConverter
from .revision_converter import RevisionConverter
from .readme_converter import ReadMeConverter
from .main_converter import MainConverter

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
        converted_contents = []
        source_wrapper = SourceDataWrapper(source)
        # converted_contents.append(self.get_converter(MainConverter).convert(None))
        converted_contents.append(
            self.get_converter(EnvironmentConverter).convert(
                source_wrapper.get_resources_by_type('Microsoft.AppPlatform/Spring')[0]
            )
        )
        # converted_contents.append(
        #     self.get_converter(AppConverter).convert(
        #         source_wrapper.get_resources_by_type('Microsoft.AppPlatform/apps')
        #     )
        # )
        # converted_contents.append(
        #     self.get_converter(RevisionConverter).convert(
        #         source_wrapper.get_resources_by_type('Microsoft.AppPlatform/apps/deployments')
        #     )
        # )
        converted_contents.append(self.get_converter(ReadMeConverter).convert(None))
        return converted_contents

    def save_to_files(self, converted_contents, output_path):
        print("Start to save the converted content to files ...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        for i, content in enumerate(converted_contents):
            filename = f"{output_path}/export_script_{i+1}.bicep"
            with open(filename, 'w', encoding='utf-8') as output_file:
                print("Start to generate the {filename} file ...")
                output_file.write(content)

class SourceDataWrapper:
    def __init__(self, source):
        self.source = source

    def get_resources_by_type(self, resource_type):
        return [resource for resource in self.source['resources'] if resource['type'] == resource_type]