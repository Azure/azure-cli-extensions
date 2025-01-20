import os

from abc import ABC, abstractmethod
from jinja2 import Template

# Abstract Base Class for Converter
# The converter is a template class that defines the structure of the conversion process
# The responsibility of the converter is to convert the input data into the output data
# The conversion process is divided into three steps:
# 1. Load the input data
# 2. Calculate the output data
# 3. Generate the output data
class ConverterTemplate(ABC):
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
