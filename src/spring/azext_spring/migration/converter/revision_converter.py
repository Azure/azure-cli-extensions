from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Revision
class RevisionConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = []
        for resource in source:
            self.source.append(resource)

    def calculate_data(self):
        self.data.revisions = []
        for revision in self.source:
            self.data.revisions.append({
                "name": revision["properties"]["name"],
                "app": self.source.app_name,
                "cpu_core": "0.5",
                "memory_size": "1",
                "min_replicas": 1,
                "max_replicas": 5,
            })

    def get_template_name(self):
        return "revision.bicep"