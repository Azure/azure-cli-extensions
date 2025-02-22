from .base_converter import ConverterTemplate

# Concrete Subclass for Container App Environment
class EnvironmentConverter(ConverterTemplate):
    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        name = self.source['name'].split('/')[-1]
        apps = self.source.get('apps')
        self.data = {
            "containerAppEnvName": name,
            "containerAppLogAnalyticsName": f"log-{name}",
            "identity": {
                "type": self._get_identity_type(apps),
                "userAssignedIdentities": self._get_user_assigned_identity_list(apps),
            }
        }

        isVnet = self.source['isVnet']
        if isVnet:
            self.data["vnetConfiguration"] = {
                "internal": str(True).lower(),
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

    def _get_identity_type(self, apps):
        type = None
        hasUserAssignedIdentity = False
        hasSystemAssignedIdentity = False
        for app in apps:
            if app.get('identity') is not None:
                if 'SystemAssigned' in app['identity'].get('type'):
                    hasSystemAssignedIdentity = True
                elif 'UserAssigned' in app['identity'].get('type'):
                    hasUserAssignedIdentity = True
        if hasUserAssignedIdentity and hasSystemAssignedIdentity:
            type = "SystemAssigned,UserAssigned"
        elif hasUserAssignedIdentity:
            type = "UserAssigned"
        elif hasSystemAssignedIdentity:
            type = "SystemAssigned"
        return type
    
    def _get_user_assigned_identity_list(self, apps):
        user_assigned_identities = []
        for app in apps:
            if app.get('identity') is not None:
                if 'UserAssigned' in app['identity'].get('type'):
                    if app.get('identity').get('userAssignedIdentities') is not None:
                        for id in app['identity']['userAssignedIdentities']:
                            user_assigned_identities.append(id)
        return user_assigned_identities
