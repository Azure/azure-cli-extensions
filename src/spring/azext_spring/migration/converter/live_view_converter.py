from .base_converter import ConverterTemplate

class LiveViewConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            live_view = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/applicationLiveViews')[0]
            name = "admin"
            configurations = []
            replicas = 1
            return {
                "sbaName": name,
                "configurations": configurations,
                "replicas": replicas
            }
        super().__init__(input, extract_data)

    def get_template_name(self):
        return "spring_boot_admin.bicep"
    

