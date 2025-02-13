from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class MainConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source
        self.apps = source["apps"]
        self.managedComponents = source["managedComponents"]

    def calculate_data(self):
        self.data.setdefault("apps", [])
        for item in self.apps:
            appName = item['name'].split('/')[-1]
            moduleName = appName.replace("-", "")
            templateName = f"{appName}_app.bicep"

            self.data["apps"].append({
                "appName": appName,
                "moduleName": moduleName,
                "templateName": templateName,
            })
        for name, value in self.managedComponents.items():
            self.data[name] = value

    def get_template_name(self):
        return "main.bicep"