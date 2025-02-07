import os

from azure.cli.command_modules.resource._client_factory import (_resource_client_factory)
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from jinja2 import Environment, FileSystemLoader
from .converter.conversion_context import ConversionContext
from .converter.environment_converter import EnvironmentConverter
from .converter.app_converter import AppConverter
from .converter.revision_converter import RevisionConverter
from .converter.gateway_converter import GatewayConverter
from .converter.eureka_converter import EurekaConverter
from .converter.service_registry_converter import ServiceRegistryConverter
from .converter.config_server_converter import ConfigServerConverter
from .converter.acs_converter import ACSConverter
from .converter.live_view_converter import LiveViewConverter
from .converter.readme_converter import ReadMeConverter
from .converter.main_converter import MainConverter
from .converter.param_converter import ParamConverter

logger = get_logger(__name__)


def migration_aca_start(cmd, client, resource_group, service):
    # API calls
    logger.info("Start export ARM template for ASA service...")
    asa_arm = export_asa_arm_template(cmd, resource_group, service)

    # Create context and add converters
    context = ConversionContext()
    context.add_converter(MainConverter())
    context.add_converter(EnvironmentConverter())
    context.add_converter(AppConverter())
    context.add_converter(RevisionConverter())
    context.add_converter(GatewayConverter(client, resource_group, service))
    context.add_converter(EurekaConverter())
    context.add_converter(ServiceRegistryConverter())
    context.add_converter(ConfigServerConverter())
    context.add_converter(ACSConverter())
    context.add_converter(LiveViewConverter())
    context.add_converter(ReadMeConverter())
    context.add_converter(ParamConverter())

    # Define the parameters for the Bicep template and output the Bicep files
    logger.info("Start to generate ACA bicep files based on parameters...")

    # Prepare bicep parameters
    main_bicep_params = get_aca_bicep_params(asa_arm)

    # Set parameters for EnvironmentConverter such as workload profile
    context.set_params_for_converter(EnvironmentConverter, main_bicep_params)

    # Run all converters
    logger.info("Start to run all converters...")
    converted_contents = context.run_converters(asa_arm)

    # Save each line of converted content to a separate file
    context.save_to_files(converted_contents, os.path.join("output",""))
    logger.info("Succeed to generate Bicep files")


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


def get_aca_bicep_params(asa_arm):
    return {"key1": "value1"}
