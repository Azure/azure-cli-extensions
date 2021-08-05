from knack.log import get_logger

logger = get_logger(__name__)

def app_get_enterprise(cmd, client, resource_group, service, name):
    app = client.apps.get(resource_group, service, name)
    deployments = client.deployments.list(resource_group, service, name)
    app.properties.activeDeployment = next(x for x in deployments if x.properties.active)
    return app