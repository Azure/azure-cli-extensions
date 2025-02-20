from .base_converter import ConverterTemplate

# Concrete Converter Subclass for paramter
class ParamConverter(ConverterTemplate):
    def load_source(self, source):
        self.apps = source['apps']
        self.is_vnet = source['isVnet']

    def calculate_data(self):
        self.data.setdefault("apps", [])
        for item in self.apps:
            appName = item['name'].split('/')[-1]
            self.data["apps"].append({
                "appName": appName,
                "containerAppImageName": "containerImageFor_"+appName.replace("-", "_"),
            })
        self.data["isVnet"] = self.is_vnet

    def get_template_name(self):
        return "param.bicepparam"