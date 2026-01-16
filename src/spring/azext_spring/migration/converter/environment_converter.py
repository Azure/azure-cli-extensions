# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from .base_converter import BaseConverter

logger = get_logger(__name__)


# Concrete Subclass for Container App Environment
class EnvironmentConverter(BaseConverter):

    def __init__(self, source):
        def transform_data():
            asa_service = self.wrapper_data.get_asa_service()
            name = self._get_resource_name(asa_service)
            certs = self.wrapper_data.get_keyvault_certificates()
            data = {
                "containerAppEnvName": name,
                "containerAppLogAnalyticsName": f"log-{name}",
                "storages": self._get_app_storage_configs(),
            }
            if self._need_identity(certs):
                data["identity"] = {
                    "type": "SystemAssigned",
                }
            if self.wrapper_data.is_vnet():
                data["vnetConfiguration"] = {
                    "internal": str(True).lower(),
                }

            asa_zone_redundant = asa_service['properties'].get('zoneRedundant', False)
            if asa_zone_redundant is not None:
                if asa_zone_redundant is True and self.wrapper_data.is_vnet() is False:
                    logger.warning("Mismatch: Zone redundant is only supported in VNet environment for Azure Container Apps.")
                    data["zoneRedundant"] = str(False).lower()
                else:
                    data["zoneRedundant"] = str(asa_zone_redundant).lower()

            asa_maintenance_window = asa_service['properties'].get('maintenanceScheduleConfiguration', None)
            if asa_maintenance_window:
                aca_maintenance_window = [{
                    "weekDay": asa_maintenance_window['day'],
                    "startHourUtc": asa_maintenance_window['hour'],
                    "durationHours": 8,
                }]
                data["scheduledEntries"] = aca_maintenance_window
            return data
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "environment.bicep"

    def _need_identity(self, certs):
        if certs is not None and len(certs) > 0:
            return True
        return False
