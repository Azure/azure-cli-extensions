import hashlib
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

    def _get_storage_unique_name(self, storage_name, account_name, share_name, mount_path, access_mode):
        storage_unique_name = f"{storage_name}|{account_name}|{share_name}|{mount_path}|{access_mode}"
        hash_value = hashlib.md5(storage_unique_name.encode()).hexdigest()[:16]  # Take first 16 chars of hash
        result = f"{storage_name}{hash_value}"
        return result[:32]  # Ensure total length is no more than 32