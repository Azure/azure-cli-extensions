from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Gateway
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
        print(f"source: {self.source}")

    def calculate_data(self):
        gatewayName = self.source['gateway']['name'].split('/')[-1]
        self.data = {
            "gatewayName": gatewayName,
            "configurations": [
                {
                    "propertyName": "spring.cloud.gateway.xxx",
                    "value": "abcd",
                },
                {
                    "propertyName": "spring.cloud.gateway.yyy",
                    "value": "efgh",
                }
            ],
            "replicas": 2,
            "routes": [
                {
                    "id": "route1",
                    "uri": "http://localhost:8080",
                    "predicates": [
                        "/api/v1/**",
                        "/api/v2/**"
                    ],
                    "filters": [
                        "AddRequestHeader=Host, example.com",
                        "AddRequestParameter=example, example.com"
                    ],
                    "order": 1
                },
                {
                    "id": "route2",
                    "uri": "http://localhost:8081",
                    "predicates": [
                        "/api/v3/**",
                        "/api/v4/**"
                    ],
                    "filters": [ "AddRequestHeader=Host, example.com", "AddRequestParameter=example, example.com"],
                    "order": 2
                }
            ]
        }

    def get_template_name(self):
        return "gateway.bicep"