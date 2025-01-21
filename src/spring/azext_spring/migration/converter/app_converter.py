from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Container App
class AppConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        appName = self.source['name'].split('/')[-1]
        moduleName = appName.replace("-", "")
        self.data = {
            "containerAppName": appName,
            "moduleName": moduleName,
            "containerImage": "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest",
            "targetPort": "80",
            "cpuCore": "0.5",
            "memorySize": "1",
            "minReplicas": 1,
            "maxReplicas": 5
        }

    def get_template_name(self):
        return "app.bicep"
    
    def get_app_name(input_string):
        return input_string.split('/')[-1]