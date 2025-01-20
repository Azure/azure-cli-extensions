from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class MainConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = []
        for resource in source:
            self.source.append(resource)

    def calculate_data(self):
        self.data.setdefault("apps", [])
        for item in self.source:
            appName = item['name'].split('/')[-1]
            moduleName = appName.replace("-", "")
            templateName = f"{appName}_app.bicep"

            print(f"appName: {appName}, moduleName: {moduleName}, templateName: {templateName}")

            self.data["apps"].append({
                "appName": appName,
                "moduleName": moduleName,
                "templateName": templateName,
            })

    def get_template_name(self):
        return "main.bicep"