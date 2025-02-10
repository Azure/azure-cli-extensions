from .base_converter import ConverterTemplate

# Concrete Subclass for Container App Environment
class EnvironmentConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        name = self.source['name'].split('/')[-1]
        self.data = {
            "containerAppEnvName": name,
            "containerAppLogAnalyticsName": f"log-{name}",
        }

        asa_zone_redundant = self.source['properties'].get('zoneRedundant')
        if asa_zone_redundant is not None:
            self.data["zoneRedundant"] = str(asa_zone_redundant).lower()

        asa_maintenance_window = self.source['properties'].get('maintenanceScheduleConfiguration')
        if asa_maintenance_window:
            aca_maintenance_window = [{
                "weekDay": asa_maintenance_window['day'],
                "startHourUtc": asa_maintenance_window['hour'],
                "durationHours": 8,
            }]
            self.data["scheduledEntries"] = aca_maintenance_window

    def get_template_name(self):
        return "environment.bicep"