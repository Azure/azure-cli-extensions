from .base_converter import ConverterTemplate

class GatewayConverter(ConverterTemplate):
    DEFAULT_NAME = "default"

    def __init__(self, client, resource_group, service):
        super().__init__()
        self.client = client
        self.resource_group = resource_group
        self.service = service

    def load_source(self, source):
        self.source = source
        secret_envs_dict = self.client.gateways.list_env_secrets(self.resource_group, self.service, self.DEFAULT_NAME)
        self.source['secretEnvs'] = secret_envs_dict

    def calculate_data(self):
        gatewayName = f"gateway"
        configurations = self._get_configurations(self.source)
        replicas = min(2, self.source['gateway']['sku']['capacity'])
        routes = self._get_routes(self.source['routes'])

        self.data = {
            "gatewayName": gatewayName,
            "configurations": configurations,
            "replicas": replicas,
            "routes": routes,
        }

    def _get_configurations(self, source):
        configurations = []
        for key, value in source['gateway']['properties']['environmentVariables']['properties'].items():
            configurations.append({
                "propertyName": key,
                "value": value,
            })
        for key, value in source['secretEnvs'].items():
            configurations.append({
                "propertyName": key,
                "value": value,
            })
        return configurations

    def _get_routes(self, routes):
        aca_routes = []
        for route in routes:
            aca_id = route['name'].split('/')[-1]
            aca_uri = self._get_uri_from_route(route)
            for r in route['properties']['routes']:
                aca_routes.append({
                    "id": aca_id,
                    "uri": r.get('uri', aca_uri),
                    "predicates": r.get('predicates'),
                    "filters": r.get('filters'),
                    "order": r.get('order') or 0,
                })
        return aca_routes

    def _get_uri_from_route(self, route):
        app_resource_id = route['properties']['appResourceId']
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
