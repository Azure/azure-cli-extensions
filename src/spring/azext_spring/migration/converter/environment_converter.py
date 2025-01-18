from converter import ConverterTemplate 

# Concrete Subclass for Container App Environment
class EnvironmentConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source['properties']

    def calculate_data(self):
        self.data = {
            "name": self.source.name,
            "location": self.source.location,
            "log_analytics": f"log-{self.source.name}",

            "containerAppEnvName": self.source["name"],
            "location": self.source["location"],
            "containerAppLogAnalyticsName": self.source["log_analytics"],
        }

    def get_template_name(self):
        return "environment.bicep"