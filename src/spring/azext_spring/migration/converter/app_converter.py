from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Container App
class AppConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = []
        for resource in source:
            self.source.append(resource)

    def calculate_data(self):
        self.data.apps = []
        for app in self.source:
            self.data.apps.append({
                "containerAppName": app["name"],
                "containerImage": self.params["container_image"],
                "targetPort": self.params["target_port"],
                "cpuCore": app['properties']["cpu_core"],
                "memorySize": app["memory_size"],
                "minReplicas": app["min_replicas"],
                "maxReplicas": app["max_replicas"],
            })

    def get_template_name(self):
        return "app.bicep"