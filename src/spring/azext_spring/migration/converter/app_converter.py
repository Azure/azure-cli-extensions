from converter import ConverterTemplate

# Concrete Converter Subclass for Container App
class AppConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source['properties']

    def calculate_data(self):
        self.data = {
            "name": self.source.name,
            "container_image": "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest",
            "target_port": 80,
            "cpu_core": "0.5",
            "memory_size": "1",
            "min_replicas": 1,
            "max_replicas": 5,

            "containerAppName": self.source.["name"],
            "containerImage": self.source.["container_image"],
            "targetPort": self.source.["target_port"],
            "cpuCore": self.source.["cpu_core"],
            "memorySize": self.source.["memory_size"],
            "minReplicas": self.source.["min_replicas"],
            "maxReplicas": self.source.["max_replicas"],
        }

    def get_template_name(self):
        return "app.bicep"