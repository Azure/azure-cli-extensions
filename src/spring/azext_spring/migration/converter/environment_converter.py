from .base_converter import ConverterTemplate

# Concrete Subclass for Container App Environment
class EnvironmentConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        self.data = {
            "containerAppEnvName": self.source['name'],
            "location": self.source['location'],
            "containerAppLogAnalyticsName": f"log-{self.source['name']}",
        }

    def get_template_name(self):
        return "environment.bicep"