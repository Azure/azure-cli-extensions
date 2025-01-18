from converter import ConverterTemplate

# Concrete Converter Subclass for Revision
class RevisionConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source['properties']

    def calculate_data(self):
        self.data = {
            "name": self.source.name,
            "app": self.source.app_name,
            "cpu_core": "0.5",
            "memory_size": "1",
            "min_replicas": 1,
            "max_replicas": 5,
        }

    def get_template_name(self):
        return "revision.bicep"