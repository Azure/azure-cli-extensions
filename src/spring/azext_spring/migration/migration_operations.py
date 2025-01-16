import os

from azure.cli.command_modules.resource._client_factory import (_resource_client_factory)
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from jinja2 import Environment, FileSystemLoader

logger = get_logger(__name__)


def migration_aca_start(cmd, client, resource_group, service):
    # API calls
    print("Start API calls to get ASA service, apps and deployments...")
    asa = get_asa(client, resource_group, service)
    asa_arm = export_asa_arm_template(cmd, resource_group, service)

    # Extract necessary properties from asa_service to aca_env, asa_app to aca_app, asa_deployment to aca_revision
    print("Start to convert ASA resources to ACA resources...")
    aca = convert_asa_to_aca(asa)

    # Define the parameters for the Bicep template and output the Bicep files
    print("Start to generate ACA bicep files based on parameters...")
    # Prepare bicep parameters
    main_bicep_params, env_bicep_params, apps_bicep_params = get_aca_bicep_params(aca)

    output_dir = "output"
    template_dir = "templates"
    script_dir = os.path.dirname(os.path.abspath(__file__))

    env = Environment(loader=FileSystemLoader(os.path.join(script_dir, template_dir)))

    # Generate the Bicep files
    print(env_bicep_params)
    generate_bicep_file(env, "main.bicep.j2", os.path.join(output_dir, "main.bicep"), main_bicep_params)
    generate_bicep_file(env, "environment.bicep.j2", os.path.join(output_dir, "environment.bicep"), env_bicep_params)
    # [print(app) for app in apps_bicep_params]
    [generate_bicep_file(env, "app.bicep.j2", os.path.join(output_dir, f"app-{app['containerAppName']}.bicep"), app) for app in apps_bicep_params]
    print("Succeed to generate Bicep files")

    # Generate readme file
    print("Start to generate the readme file based on parameters...")
    readme_params = {}
    generate_bicep_file(env, "readme_template.j2", os.path.join(output_dir, "readme"), readme_params)
    print("Generated readme file.")


def get_asa(client, resource_group, service):
    asa_service = client.services.get(resource_group, service)
    asa_apps = client.apps.list(resource_group, service)
    asa = {
        "service": asa_service,
        "apps": asa_apps,
    }
    return asa

def export_asa_arm_template(cmd, resource_group, service):
    resources = []
    subscription = get_subscription_id(cmd.cli_ctx)
    service_resource_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}'.format(
        subscription, resource_group, service)
    logger.info("service_resource_id: '%s'", service_resource_id)
    resources.append(service_resource_id)
    options = "SkipAllParameterization,IncludeParameterDefaultValue"

    ExportTemplateRequest = cmd.get_models('ExportTemplateRequest')
    export_template_request = ExportTemplateRequest(resources=resources, options=options)
    
    rcf = _resource_client_factory(cmd.cli_ctx)

    if cmd.supported_api_version(min_api='2019-08-01'):
        result_poller = rcf.resource_groups.begin_export_template(resource_group,
                                                                  parameters=export_template_request)
        result = LongRunningOperation(cmd.cli_ctx)(result_poller)
    else:
        result = rcf.resource_groups.begin_export_template(resource_group,
                                                           parameters=export_template_request)
    return result.template

def convert_asa_to_aca(asa):
    aca_environment = _convert_asa_service_to_aca_environment(asa["service"])
    aca_apps = [_convert_asa_app_to_aca_app(app) for app in asa["apps"]]
    # aca_revisions = [_convert_asa_deployment_to_aca_revision(deployment) for deployment in asa["deployments"]]
    aca = {
        "environment": aca_environment,
        "apps": aca_apps,
        # "revisions": aca_revisions
    }
    return aca


def get_aca_bicep_params(aca):
    main_bicep_params = {}
    env_bicep_params = _get_aca_environment_bicep_params(aca["environment"])
    apps_bicep_params = [_get_aca_app_bicep_params(app) for app in aca["apps"]]  # array of container app parameters
    return main_bicep_params, env_bicep_params, apps_bicep_params


def replace_variables_in_template(template_path, output_path, variables):
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file {template_path} not found")

    with open(template_path, 'r', encoding='utf-8') as template_file:
        content = template_file.read()

    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        content = content.replace(placeholder, f"'{value}'")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(content)


def generate_bicep_file(env, template_name, output_path, variables):
    template = env.get_template(template_name)
    content = template.render(variables)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(content)


def _convert_asa_service_to_aca_environment(asa_service):
    aca_environment = {
        "name": asa_service.name,
        "location": asa_service.location,
        "log_analytics": f"log-{asa_service.name}",
    }
    return aca_environment


def _convert_asa_app_to_aca_app(asa_app):
    aca_app = {
        "name": asa_app.name,
        "container_image": "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest",
        "target_port": 80,
        "cpu_core": "0.5",
        "memory_size": "1",
        "min_replicas": 1,
        "max_replicas": 5,
    }
    return aca_app


def _convert_asa_deployment_to_aca_revision(asa_deployment):
    aca_revision = {
        "name": asa_deployment.name,
        "app": asa_deployment.app_name,
        "cpu_core": "0.5",
        "memory_size": "1",
        "min_replicas": 1,
        "max_replicas": 5,
    }
    return aca_revision


def _get_aca_environment_bicep_params(aca_environment):
    return {
        "containerAppEnvName": aca_environment["name"],
        "location": aca_environment["location"],
        "containerAppLogAnalyticsName": aca_environment["log_analytics"],
    }


def _get_aca_app_bicep_params(aca_app):
    return {
        "containerAppName": aca_app["name"],
        "containerImage": aca_app["container_image"],
        "targetPort": aca_app["target_port"],
        "cpuCore": aca_app["cpu_core"],
        "memorySize": aca_app["memory_size"],
        "minReplicas": aca_app["min_replicas"],
        "maxReplicas": aca_app["max_replicas"],
    }
