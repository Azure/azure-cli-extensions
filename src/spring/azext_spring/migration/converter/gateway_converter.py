# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from .base_converter import BaseConverter

logger = get_logger(__name__)


class GatewayConverter(BaseConverter):
    DEFAULT_NAME = "default"

    def __init__(self, source, client, resource_group, service):
        def transform_data():
            if self.wrapper_data.is_support_gateway():
                gateway = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways')[0]
                routes = []
                for gateway_route in self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways/routeConfigs'):
                    routes.append(gateway_route)
                secretEnvs = self.client.gateways.list_env_secrets(self.resource_group, self.service, self.DEFAULT_NAME)
                configurations = self._get_configurations(gateway, secretEnvs)
                replicas = 2
                if gateway.get('sku', {}).get('capacity') is not None:
                    replicas = min(2, gateway['sku']['capacity'])
                routes = self._get_routes(routes)
                self._check_features(gateway.get('properties', {}))
                self._check_custom_domains()
                return {
                    "routes": routes,
                    "gatewayName": "gateway",
                    "configurations": configurations,
                    "replicas": replicas,
                }
            else:
                return None
        self.client = client
        self.resource_group = resource_group
        self.service = service
        super().__init__(source, transform_data)

    def _get_configurations(self, gateway, secretEnvs):
        configurations = []
        if gateway.get('properties', {}).get('environmentVariables', {}).get('properties') is not None:
            for key, value in gateway['properties']['environmentVariables']['properties'].items():
                if key.startswith("spring.cloud.gateway") or key.startswith("logging"):
                    configurations.append({
                        "propertyName": key,
                        "value": value,
                    })
                else:
                    logger.warning(f"Mismatch: The environment variable '{key}' is not supported in gateway for Spring in Azure Container Apps, see allowed configuration list of Gateway for Spring.")
        if secretEnvs is not None:
            for key, value in secretEnvs.items():
                configurations.append({
                    "propertyName": key,
                    "value": value,
                })
        return configurations

    def _get_routes(self, routes):
        aca_routes = []
        name_counter = {}
        if routes:
            for route in routes:
                base_name = self._get_resource_name(route)
                aca_uri = self._get_uri_from_route(route)
                if route.get('properties', {}).get('routes') is not None:
                    for r in route['properties']['routes']:
                        count = name_counter.get(base_name, 0) + 1
                        name_counter[base_name] = count
                        aca_routes.append({
                            "id": f"{base_name}_{count}",
                            "uri": r.get('uri', aca_uri),
                            "predicates": r.get('predicates') if r.get('predicates') else [],
                            "filters": self._get_filters(base_name, r),
                            "order": r.get('order') or 0,
                        })
        return aca_routes

    def _get_uri_from_route(self, route):
        app_resource_id = route.get('properties', {}).get('appResourceId')
        if app_resource_id:
            app_name = self._get_app_name_from_app_resource_id(app_resource_id)
            return f"http://{app_name}"
        return

    def _get_app_name_from_app_resource_id(self, app_resource_id):
        start = app_resource_id.rfind("'")
        previous_comma = app_resource_id.rfind(",", 0, start)
        return app_resource_id[previous_comma + 3:start]

    def _get_filters(self, route_name, r):
        filters = []
        if r.get('filters'):
            for f in r.get('filters'):
                if 'cors' in f.lower():
                    logger.warning(f"Action Needed: The cors filter '{f}' of route '{route_name}' is not supported in Gateway for Spring in Azure Container Apps, refer to migration doc for further steps.")
                else:
                    filters.append(f)
        return filters

    def _check_features(self, scg_properties):
        if scg_properties.get('ssoProperties') is not None:
            logger.warning("Mismatch: The SSO feature is not supported of Gateway for Spring in Azure Container Apps.")
        if scg_properties.get('corsProperties') is not None and scg_properties.get('corsProperties') != {}:
            logger.warning("Action Needed: CORS configuration detected, please refer to public doc to migrate CORS feature of Gateway for Spring to Azure Container Apps.")
        if (scg_properties.get('apiMetadataProperties') is not None and scg_properties.get('apiMetadataProperties') != {}):
            logger.warning("Mismatch: API metadata configuration is not supported of Gateway for Spring to Azure Container Apps.")
        if (scg_properties.get('apmTypes') is not None and len(scg_properties.get('apmTypes')) > 0) or (scg_properties.get('apms') is not None and scg_properties.get('apms') != []):
            logger.warning("Mismatch: APM configuration is not supported of Gateway for Spring to Azure Container Apps.")

    def _check_custom_domains(self):
        custom_domains = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways/domains')
        if custom_domains is not None and len(custom_domains) > 0:
            logger.warning("Mismatch: Custom domains of gateway is not supported in Gateway for Spring of Azure Container Apps.")

    def get_template_name(self):
        return "gateway.bicep"
