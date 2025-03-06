from .base_converter import ConverterTemplate
from knack.log import get_logger

logger = get_logger(__name__)

class GatewayConverter(ConverterTemplate):
    DEFAULT_NAME = "default"

    def __init__(self, source, client, resource_group, service):
        def extract_data():
            gateway = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways')[0]
            routes = []
            for gateway_route in self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/gateways/routeConfigs'):
                routes.append(gateway_route)
            gatewayName = f"gateway"
            secretEnvs = self.client.gateways.list_env_secrets(self.resource_group, self.service, self.DEFAULT_NAME)
            configurations = self._get_configurations(gateway, secretEnvs)
            replicas = 2
            if gateway.get('sku', {}).get('capacity') is not None:
                replicas = min(2, gateway['sku']['capacity'])
            routes = self._get_routes(routes)                
            return {
                "routes": routes,
                "gatewayName": gatewayName,
                "configurations": configurations,
                "replicas": replicas,
                "routes": routes,                
            }        
        self.client = client
        self.resource_group = resource_group
        self.service = service
        super().__init__(source, extract_data)

    def _get_configurations(self, gateway, secretEnvs):
        configurations = []
        if gateway.get('properties', {}).get('environmentVariables', {}).get('properties') is not None:
            for key, value in gateway['properties']['environmentVariables']['properties'].items():
                configurations.append({
                    "propertyName": key,
                    "value": value,
                })
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
                base_name = route['name'].split('/')[-1]
                aca_uri = self._get_uri_from_route(route)
                if route.get('properties', {}).get('routes') is not None:
                    for r in route['properties']['routes']:
                        count = name_counter.get(base_name, 0) + 1
                        name_counter[base_name] = count
                        aca_routes.append({
                            "id": f"{base_name}_{count}",
                            "uri": r.get('uri', aca_uri),
                            "predicates": r.get('predicates') if r.get('predicates') else [],
                            "filters": r.get('filters') if r.get('filters') else [],
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


    def get_template_name(self):
        return "gateway.bicep"
