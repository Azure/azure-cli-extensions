# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.command_modules.resource._client_factory import (_resource_client_factory)
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from .converter.conversion_context import ConversionContext
from .converter.environment_converter import EnvironmentConverter
from .converter.app_converter import AppConverter
from .converter.gateway_converter import GatewayConverter
from .converter.eureka_converter import EurekaConverter
from .converter.service_registry_converter import ServiceRegistryConverter
from .converter.config_server_converter import ConfigServerConverter
from .converter.acs_converter import ACSConverter
from .converter.live_view_converter import LiveViewConverter
from .converter.readme_converter import ReadMeConverter
from .converter.main_converter import MainConverter
from .converter.param_converter import ParamConverter
from .converter.cert_converter import CertConverter

logger = get_logger(__name__)


def migration_aca_start(cmd, client, resource_group, service, output_folder):
    logger.info("Getting your Azure Spring Apps service...")
    logger.debug("Start to export ARM template for Azure Spring Apps service...")
    asa_arm = export_asa_arm_template(cmd, resource_group, service)

    # Create context and add converters
    context = ConversionContext(asa_arm)
    context.register_converter(MainConverter)
    context.register_converter(EnvironmentConverter)
    context.register_converter(AppConverter)
    context.register_converter(lambda param: GatewayConverter(param, client, resource_group, service))
    context.register_converter(EurekaConverter)
    context.register_converter(ServiceRegistryConverter)
    context.register_converter(ConfigServerConverter)
    context.register_converter(ACSConverter)
    context.register_converter(LiveViewConverter)
    context.register_converter(ReadMeConverter)
    context.register_converter(ParamConverter)
    context.register_converter(CertConverter)

    # Run all converters
    logger.warning("Converting resources to Azure Container Apps...")
    converted_contents = context.run_converters()

    logger.debug("Start to save the converted content to files...")
    # Save each line of converted content to a separate file
    context.save_to_files(converted_contents, output_folder)
    logger.warning(f"Successfully generated the Bicep files in folder '{output_folder}'. Please review the files and follow the instructions in the `README.md` for the next steps.")


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
