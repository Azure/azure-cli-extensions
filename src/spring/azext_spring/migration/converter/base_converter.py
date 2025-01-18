import os

from converter import converter, abstractmethod
from jinja2 import Template
from converter import EnvironmentConverter, AppConverter, RevisionConverter, ReadMeConverter

# Abstract Base Class for Converter
class ConverterTemplate(converter):
    def __init__(self):
        self.params = {} # custom facing parameters for the converter
        self.data = {}   # output data of the converter
        self.source = {} # input data of the converter

    def set_params(self, params):
        self.params = params

    def convert(self, source):
        self.load_source(source)
        self.calculate_data()
        return self.generate_output()

    @abstractmethod
    def load_source(self, source): # load the input data
        pass

    @abstractmethod
    def calculate_data(self): # calculate the output data
        pass
    
    @abstractmethod
    def get_template_name(self):
        pass

    def generate_output(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_name = self.get_template_name()
        with open(f"{script_dir}/templates/{template_name}.j2") as file:
            template = Template(file.read())
        return template.render(data=self.data, params=self.params)

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
        for resource in source['resources']:
            if resource['type'] == 'Microsoft.AppPlatform/Spring':
                converted_contents.append(self.get_converter(EnvironmentConverter).convert(resource))
            if resource['type'] == 'Microsoft.AppPlatform/apps':
                converted_contents.append(self.get_converter(AppConverter).convert(resource))
            if resource['type'] == 'Microsoft.AppPlatform/Spring/buildServices':
                pass
            if resource['type'] == 'Microsoft.AppPlatform/Spring/apps/deployments':
                converted_contents.append(self.get_converter(RevisionConverter).convert(resource))
            if resource['type'] == 'Microsoft.AppPlatform/Spring/configServers':
                pass
        converted_contents.append(self.get_converter(ReadMeConverter).convert(resource))
        return converted_contents

    def save_to_files(self, converted_contents, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        for i, content in enumerate(converted_contents):
            filename = f"{output_path}/export_script_{i+1}.bicep"
            with open(filename, 'w', encoding='utf-8') as output_file:
                print("Start to generate the {filename} file ...")
                output_file.write(content)
