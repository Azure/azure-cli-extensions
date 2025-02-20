from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class MainConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source
        self.apps = source["apps"]
        self.managedComponents = source["managedComponents"]
        self.certs = source["certs"]

    def calculate_data(self):
        self.data["isVnet"] = self.source.get("isVnet", False)
        self.data.setdefault("certs", [])
        for item in self.certs:
            certName = item['name'].split('/')[-1]
            moduleName = "cert_" + certName.replace("-", "_")
            templateName = f"{certName}_cert.bicep"
            certData = {
                "certName": certName,
                "moduleName": moduleName,
                "templateName": templateName,
            }
            self.data["certs"].append(certData)

        self.data.setdefault("apps", [])
        for item in self.apps:
            appName = item['name'].split('/')[-1]
            moduleName = appName.replace("-", "_")
            templateName = f"{appName}_app.bicep"
            appData = {
                "appName": appName,
                "moduleName": moduleName,
                "templateName": templateName,
                "containerAppImageName": "containerImageFor_"+appName.replace("-", "_"),
            }
            self.data["apps"].append(appData)

        for name, value in self.managedComponents.items():
            self.data[name] = value

    def get_template_name(self):
        return "main.bicep"