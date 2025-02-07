from .base_converter import ConverterTemplate

class LiveViewConverter(ConverterTemplate):

    def __init__(self):
        super().__init__()

    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        name = self.source['name'].split('/')[-1]
        configurations = []
        replicas = 1

        self.data = {
            "sbaName": name,
            "configurations": configurations,
            "replicas": replicas
        }

    def get_template_name(self):
        return "spring_boot_admin.bicep"
    

