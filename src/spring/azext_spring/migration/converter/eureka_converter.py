from .base_converter import BaseConverter

class EurekaConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            name = "eureka"
            configurations = []
            replicas = 1

            return {
                "eurekaName": name,
                "configurations": configurations,
                "replicas": replicas
            }
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "eureka.bicep"
    

