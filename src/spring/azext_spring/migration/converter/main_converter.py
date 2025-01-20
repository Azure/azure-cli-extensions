from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class MainConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = []
        for resource in source:
            print("resource: ", resource)
            self.source.append(resource)

    def calculate_data(self):
        self.data.setdefault("apps", [])
        for app in self.source:
            self.data["apps"].append({
                "name": app["name"],
            })
            print("app: ", app)
        print(self.data["apps"])

    def get_template_name(self):
        return "main.bicep"