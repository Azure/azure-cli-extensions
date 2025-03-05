from .base_converter import ConverterTemplate

class LiveViewConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data(input):
            # TODO: Implement the extract_data method
            return input
        super().__init__(input, extract_data)

    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        name = "admin"
        configurations = []
        replicas = 1

        self.data = {
            "sbaName": name,
            "configurations": configurations,
            "replicas": replicas
        }

    def get_template_name(self):
        return "spring_boot_admin.bicep"
    

