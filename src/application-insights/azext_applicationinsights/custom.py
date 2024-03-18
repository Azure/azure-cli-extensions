# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, protected-access
# pylint: disable=raise-missing-from
# pylint: disable=too-many-statements, too-many-locals, too-many-branches

import datetime
import isodate
from knack.util import CLIError
from knack.log import get_logger
from msrestazure.azure_exceptions import CloudError
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.core.aaz import has_value, register_command
from azext_applicationinsights.vendored_sdks.applicationinsights.models import ErrorResponseException
from .util import get_id_from_azure_resource, get_query_targets, get_timespan, get_linked_properties
from .aaz.latest.monitor.app_insights.api_key import List as APIKeyList, Create as _APIKeyCreate, Delete as _APIKeyDelete
from .aaz.latest.monitor.app_insights.component.billing import Show as _BillingShow, Update as _BillingUpdate
from .aaz.latest.monitor.app_insights.component.linked_storage import Link as _LinkedStorageAccountLink, Update as _LinkedStorageAccountUpdate, Show as _LinkedStorageAccountShow, Unlink as _LinkedStorageAccountUnlink
from .aaz.latest.monitor.app_insights.component.continues_export import Delete as _ContinuesExportDelete, Show as _ContinuesExportShow, List as _ContinuesExportList
from .aaz.latest.monitor.app_insights.workbook import Create as _WorkbookCreate, Update as _WorkbookUpdate
from .aaz.latest.monitor.app_insights.workbook.identity import Assign as _IdentityAssign, Remove as _IdentityRemove

logger = get_logger(__name__)
HELP_MESSAGE = " Please use `az feature register --name AIWorkspacePreview --namespace microsoft.insights` to register the feature"


def execute_query(cmd, client, application, analytics_query, start_time=None, end_time=None, offset='1h', resource_group_name=None):
    """Executes a query against the provided Application Insights application."""
    from .vendored_sdks.applicationinsights.models import QueryBody
    targets = get_query_targets(cmd.cli_ctx, application, resource_group_name)
    if not isinstance(offset, datetime.timedelta):
        offset = isodate.parse_duration(offset)
    try:
        return client.query.execute(targets[0], QueryBody(query=analytics_query, timespan=get_timespan(cmd.cli_ctx, start_time, end_time, offset), applications=targets[1:]))
    except ErrorResponseException as ex:
        if "PathNotFoundError" in ex.message:
            raise ValueError("The Application Insight is not found. Please check the app id again.")
        raise ex


def get_events(cmd, client, application, event_type, event=None, start_time=None, end_time=None, offset='1h', resource_group_name=None):
    timespan = get_timespan(cmd.cli_ctx, start_time, end_time, offset)
    if event:
        return client.events.get(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), event_type, event, timespan=timespan)
    return client.events.get_by_type(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), event_type, timespan=get_timespan(cmd.cli_ctx, start_time, end_time, offset))


def get_metric(cmd, client, application, metric, start_time=None, end_time=None, offset='1h', interval=None, aggregation=None, segment=None, top=None, orderby=None, filter_arg=None, resource_group_name=None):
    return client.metrics.get(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), metric, timespan=get_timespan(cmd.cli_ctx, start_time, end_time, offset), interval=interval, aggregation=aggregation, segment=segment, top=top, orderby=orderby, filter_arg=filter_arg)


def get_metrics_metadata(cmd, client, application, resource_group_name=None):
    return client.metrics.get_metadata(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name))


def create_or_update_component(cmd, client, application, resource_group_name, location, tags=None,
                               kind="web", application_type='web', workspace_resource_id=None,
                               public_network_access_for_ingestion=None, public_network_access_for_query=None, retention_in_days=None):
    # due to service limitation, we have to do such a hack. We must refract the logic later.
    if workspace_resource_id is None:
        from .vendored_sdks.mgmt_applicationinsights.v2018_05_01_preview.models import ApplicationInsightsComponent
        component = ApplicationInsightsComponent(location=location, kind=kind, application_type=application_type, tags=tags,
                                                 public_network_access_for_ingestion=public_network_access_for_ingestion,
                                                 public_network_access_for_query=public_network_access_for_query,
                                                 retention_in_days=retention_in_days)
        return client.create_or_update(resource_group_name, application, component)

    if retention_in_days is not None:
        raise CLIError("Retention time can be set only when Application Insights is not connected to a Log Analytics workspace.")

    from .vendored_sdks.mgmt_applicationinsights.v2020_02_02_preview.models import ApplicationInsightsComponent
    component = ApplicationInsightsComponent(location=location, kind=kind, application_type=application_type,
                                             tags=tags, workspace_resource_id=workspace_resource_id,
                                             public_network_access_for_ingestion=public_network_access_for_ingestion,
                                             public_network_access_for_query=public_network_access_for_query)
    from ._client_factory import applicationinsights_mgmt_plane_client
    client = applicationinsights_mgmt_plane_client(cmd.cli_ctx, api_version='2020-02-02-preview').components
    try:
        return client.create_or_update(resource_group_name, application, component)
    except CloudError as ex:
        ex.error._message = ex.error._message + HELP_MESSAGE
        raise ex


def _is_workspace_centric(workspace):
    return workspace.properties['features']['enableLogAccessUsingOnlyResourcePermissions'] is False


def _is_resource_centric(workspace):
    return workspace.properties['features']['enableLogAccessUsingOnlyResourcePermissions'] is True


# Here are two cases that need users' consent during APM (Application Performance Management) migration:
# 1. Bind a workspace-centric workspace to a classic AI (no workspace integration).
# 2. Migrate a resource-centric workspace to a workspace-centric workspace for an AI.
def _apm_migration_consent(cmd, new_workspace_resource_id, existing_workspace_resource_id):
    from azure.cli.command_modules.resource.custom import show_resource
    new_workspace = show_resource(cmd, [new_workspace_resource_id])
    if _is_workspace_centric(new_workspace):
        if existing_workspace_resource_id:
            existing_workspace = show_resource(cmd, [existing_workspace_resource_id])
            need_consent = _is_resource_centric(existing_workspace)
        else:  # This is a classic AI which isn't binding to a log analytics workspace.
            need_consent = True

        if need_consent:
            from azure.cli.core.util import user_confirmation
            user_confirmation('Specified workspace is configured with workspace-based access mode and some APM features may be impacted. Consider selecting another workspace or allow resource-based access in the workspace settings. Please refer to https://aka.ms/apm-workspace-access-mode for details. Do you want to continue?')


def update_component(cmd, client, application, resource_group_name, kind=None, workspace_resource_id=None,
                     public_network_access_for_ingestion=None, public_network_access_for_query=None, retention_in_days=None):
    from ._client_factory import applicationinsights_mgmt_plane_client
    if workspace_resource_id is not None:
        if retention_in_days is not None:
            raise CLIError("Retention time can be set only when Application Insights is not connected to a Log Analytics workspace.")
        latest_client = applicationinsights_mgmt_plane_client(cmd.cli_ctx, api_version='2020-02-02-preview').components
        try:
            existing_component = latest_client.get(resource_group_name, application)
        except CloudError as ex:
            ex.error._message = ex.error._message + HELP_MESSAGE
            raise ex

        _apm_migration_consent(cmd, workspace_resource_id, existing_component.workspace_resource_id)

        existing_component.workspace_resource_id = workspace_resource_id or None
    else:
        existing_component = client.get(resource_group_name, application)
    if kind:
        existing_component.kind = kind
    if public_network_access_for_ingestion is not None:
        existing_component.public_network_access_for_ingestion = public_network_access_for_ingestion
    if public_network_access_for_query is not None:
        existing_component.public_network_access_for_query = public_network_access_for_query

    if hasattr(existing_component, 'workspace_resource_id') and existing_component.workspace_resource_id is not None:
        from .vendored_sdks.mgmt_applicationinsights.v2020_02_02_preview.models import IngestionMode
        client = applicationinsights_mgmt_plane_client(cmd.cli_ctx, api_version='2020-02-02-preview').components
        existing_component.ingestion_mode = IngestionMode.LOG_ANALYTICS
        return client.create_or_update(resource_group_name, application, existing_component)

    from .vendored_sdks.mgmt_applicationinsights.v2018_05_01_preview.models import ApplicationInsightsComponent, IngestionMode
    if retention_in_days is not None:
        existing_component.retention_in_days = retention_in_days
    existing_component.ingestion_mode = IngestionMode.APPLICATION_INSIGHTS
    component = ApplicationInsightsComponent(**(vars(existing_component)))
    return client.create_or_update(resource_group_name, application, component)


def update_component_tags(client, application, resource_group_name, tags):
    return client.update_tags(resource_group_name, application, tags)


def connect_webapp(cmd, client, resource_group_name, application, app_service, enable_profiler=None, enable_snapshot_debugger=None):
    from azure.cli.command_modules.appservice.custom import update_app_settings
    from azure.mgmt.core.tools import parse_resource_id, is_valid_resource_id

    app_insights = client.get(resource_group_name, application)
    if app_insights is None or app_insights.instrumentation_key is None:
        raise InvalidArgumentValueError(f"App Insights {application} under resource group {resource_group_name} was not found.")

    settings = [f"APPINSIGHTS_INSTRUMENTATIONKEY={app_insights.instrumentation_key}"]
    if app_insights.connection_string is not None:
        settings.append(f"APPINSIGHTS_CONNECTIONSTRING={app_insights.connection_string}")
    if enable_profiler is True:
        settings.append("APPINSIGHTS_PROFILERFEATURE_VERSION=1.0.0")
    elif enable_profiler is False:
        settings.append("APPINSIGHTS_PROFILERFEATURE_VERSION=disabled")

    if enable_snapshot_debugger is True:
        settings.append("APPINSIGHTS_SNAPSHOTFEATURE_VERSION=1.0.0")
    elif enable_snapshot_debugger is False:
        settings.append("APPINSIGHTS_SNAPSHOTFEATURE_VERSION=disabled")

    if is_valid_resource_id(app_service):
        resource_id = parse_resource_id(app_service)
        app_service = resource_id['name']
        resource_group_name = resource_id['resource_group']  # use the resource group name in id
    return update_app_settings(cmd, resource_group_name, app_service, settings)


def connect_function(cmd, client, resource_group_name, application, app_service):
    from azure.cli.command_modules.appservice.custom import update_app_settings
    from azure.mgmt.core.tools import parse_resource_id, is_valid_resource_id
    app_insights = client.get(resource_group_name, application)
    if app_insights is None or app_insights.instrumentation_key is None:
        raise InvalidArgumentValueError(f"App Insights {application} under resource group {resource_group_name} was not found.")

    settings = [f"APPINSIGHTS_INSTRUMENTATIONKEY={app_insights.instrumentation_key}"]

    if app_insights.connection_string is not None:
        settings.append(f"APPINSIGHTS_CONNECTIONSTRING={app_insights.connection_string}")

    if is_valid_resource_id(app_service):
        resource_id = parse_resource_id(app_service)
        app_service = resource_id['name']
        resource_group_name = resource_id['resource_group']  # use the resource group name in id
    return update_app_settings(cmd, resource_group_name, app_service, settings)


def get_component(client, application, resource_group_name):
    return client.get(resource_group_name, application)


def show_components(cmd, client, application=None, resource_group_name=None):
    from ._client_factory import applicationinsights_mgmt_plane_client
    if application:
        if resource_group_name:
            latest_client = applicationinsights_mgmt_plane_client(cmd.cli_ctx,
                                                                  api_version='2020-02-02-preview').components
            try:
                return latest_client.get(resource_group_name, application)
            except CloudError:
                logger.warning(HELP_MESSAGE)
                return client.get(resource_group_name, application)
        raise CLIError("Application provided without resource group. Either specify app with resource group, or remove app.")
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def delete_component(client, application, resource_group_name):
    return client.delete(resource_group_name, application)


class APIKeyCreate(_APIKeyCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.api_key._required = True
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.read_properties):
            args.read_properties = ['ReadTelemetry', 'AuthenticateSDKControlChannel']
        if not has_value(args.write_properties):
            args.write_properties = []
        linked_read_properties, linked_write_properties = get_linked_properties(self.ctx, args.app, args.resource_group, args.read_properties.to_serialized_data(), args.write_properties.to_serialized_data())
        args.read_properties = linked_read_properties
        args.write_properties = linked_write_properties


@register_command(
    "monitor app-insights api-key show",
)
class APIKeyShow(APIKeyList):
    """
    Get all keys or a specific API key associated with an Application Insights resource.

    :example: Fetch API Key.
        az monitor app-insights api-key show --app demoApp -g demoRg --api-key demo-key
    :example: Fetch API Keys.
        az monitor app-insights api-key show --app demoApp -g demoRg
    """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.api_key = AAZStrArg(
            options=["--api-key"],
            help="Name of the API key to fetch. Can be found using `api-key show`.",
        )
        args_schema.resource_name._options = ['--app', '-a']
        args_schema.resource_name.help = "GUID, app name, or fully-qualified Azure resource name of Application Insights component. " \
                                         "The application GUID may be acquired from the API Access menu item on any Application Insights resource in the Azure portal. " \
                                         "If using an application name, please specify resource group."
        return args_schema

    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        args = self.ctx.args
        if not has_value(args.api_key):
            return output
        result = list(filter(lambda output: output['name'] == args.api_key, output))
        if len(result) == 1:
            return result[0]
        if len(result) > 1:
            return result
        return None


class APIKeyDelete(_APIKeyDelete):
    def pre_operations(self):
        from azure.core.exceptions import ResourceNotFoundError
        args = self.ctx.args
        api_key = None
        try:
            api_key = APIKeyShow(cli_ctx=self.cli_ctx)(command_args={
                "api_key": args.api_key,
                "resource_name": args.app,
                "resource_group": args.resource_group
            })
        except ResourceNotFoundError:
            raise ResourceNotFoundError('--api-key provided but key not found for deletion.')
        if api_key is not None:
            args.api_key = api_key['id'].split('/')[-1]


class BillingShow(_BillingShow):
    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        data_volume_cap = output.get("DataVolumeCap", {})
        if data_volume_cap:
            new_data_volume_cap = {
                "cap": data_volume_cap.get("Cap"),
                "maxHistoryCap": data_volume_cap.get("MaxHistoryCap"),
                "resetTime": data_volume_cap.get("ResetTime"),
                "stopSendNotificationWhenHitCap": data_volume_cap.get("StopSendNotificationWhenHitCap"),
                "stopSendNotificationWhenHitThreshold": data_volume_cap.get("StopSendNotificationWhenHitThreshold"),
                "warningThreshold": data_volume_cap.get("WarningThreshold")
            }
        result = {
            "currentBillingFeatures": output["CurrentBillingFeatures"],
            "dataVolumeCap": new_data_volume_cap
        }
        return result


class BillingUpdate(_BillingUpdate):
    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        data_volume_cap = output.get("DataVolumeCap", {})
        if data_volume_cap:
            data_volume_cap = {
                "cap": data_volume_cap.get("Cap"),
                "maxHistoryCap": data_volume_cap.get("MaxHistoryCap"),
                "resetTime": data_volume_cap.get("ResetTime"),
                "stopSendNotificationWhenHitCap": data_volume_cap.get("StopSendNotificationWhenHitCap"),
                "stopSendNotificationWhenHitThreshold": data_volume_cap.get("StopSendNotificationWhenHitThreshold"),
                "warningThreshold": data_volume_cap.get("WarningThreshold")
            }
        result = {
            "currentBillingFeatures": output["CurrentBillingFeatures"],
            "dataVolumeCap": data_volume_cap
        }
        return result


class LinkedStorageAccountShow(_LinkedStorageAccountShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.storage_type._registered = False
        args_schema.storage_type._required = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.storage_type = "ServiceProfiler"


class LinkedStorageAccountLink(_LinkedStorageAccountLink):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.storage_account = AAZResourceIdArg(
            options=["--storage-account", "-s"],
            help="Name or ID of a linked storage account",
            required=True,
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{}",
            )
        )
        args_schema.linked_storage_account._registered = False
        args_schema.storage_type._registered = False
        args_schema.storage_type._required = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.linked_storage_account = args.storage_account
        args.storage_type = "ServiceProfiler"


class LinkedStorageAccountUpdate(_LinkedStorageAccountUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.storage_account = AAZResourceIdArg(
            options=["--storage-account", "-s"],
            help="Name or ID of a linked storage account",
            required=True,
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{}",
            )
        )
        args_schema.linked_storage_account._registered = False
        args_schema.storage_type._registered = False
        args_schema.storage_type._required = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.linked_storage_account = args.storage_account
        args.storage_type = "ServiceProfiler"


class LinkedStorageAccountUnlink(_LinkedStorageAccountUnlink):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.storage_type._registered = False
        args_schema.storage_type._required = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.storage_type = "ServiceProfiler"


def create_export_configuration(cmd, client, application, resource_group_name, record_types, dest_account,
                                dest_container, dest_sas, dest_sub_id, dest_type='Blob', is_enabled='true'):
    from .vendored_sdks.mgmt_applicationinsights.models import ApplicationInsightsComponentExportRequest
    sc_op = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_STORAGE,
                                    subscription_id=dest_sub_id).storage_accounts
    storage_accounts = list(sc_op.list())
    storage_account = None
    for x in storage_accounts:
        if x.name.lower() == dest_account.lower():
            storage_account = x
            break

    if not storage_account:
        raise CLIError(f"Destination storage account {dest_account} does not exist, "
                       "use 'az storage account list' to get storage account list")

    dest_address = getattr(storage_account.primary_endpoints, dest_type.lower(), '')
    dest_address += dest_container + '?' + dest_sas

    export_config_request = ApplicationInsightsComponentExportRequest(
        record_types=', '.join(record_types) if record_types else None,
        destination_type=dest_type,
        destination_address=dest_address,
        destination_storage_subscription_id=dest_sub_id,
        destination_storage_location_id=storage_account.primary_location,
        destination_account_id=storage_account.id,
        is_enabled=is_enabled,
    )
    return client.create(resource_group_name, application, export_config_request)


def update_export_configuration(cmd, client, application, resource_group_name, export_id, record_types=None,
                                dest_account=None, dest_container=None, dest_sas=None, dest_sub_id=None, dest_type=None,
                                is_enabled=None):
    from .vendored_sdks.mgmt_applicationinsights.models import ApplicationInsightsComponentExportRequest

    export_config_request = ApplicationInsightsComponentExportRequest(
        record_types=', '.join(record_types) if record_types else None,
        is_enabled=is_enabled,
    )

    if dest_sub_id is not None or dest_account is not None or dest_container is not None:
        if not dest_sas:
            raise CLIError("The SAS token for the destination storage container required.")
        pre_config = ExportConfigurationShow(cli_ctx=cmd.cli_ctx)(command_args={
            "id": export_id,
            "app": application,
            "resource_group": resource_group_name
        })
        if dest_sub_id is None:
            dest_sub_id = pre_config.destination_storage_subscription_id
        if dest_account is None:
            if dest_sub_id != pre_config.destination_storage_subscription_id:
                raise CLIError("The destination storage account name required.")
            dest_account = pre_config.storage_name
        if dest_container is None:
            dest_container = pre_config.container_name
        if dest_type is None:
            dest_type = 'Blob'

        sc_op = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_STORAGE,
                                        subscription_id=dest_sub_id).storage_accounts
        storage_accounts = list(sc_op.list())
        storage_account = None
        for x in storage_accounts:
            if x.name.lower() == dest_account.lower():
                storage_account = x
                break

        if not storage_account:
            raise CLIError(f"Destination storage account {dest_account} does not exist, "
                           "use 'az storage account list' to get storage account list")

        dest_address = getattr(storage_account.primary_endpoints, dest_type.lower(), '')
        dest_address += dest_container + '?' + dest_sas
        export_config_request.destination_type = dest_type
        export_config_request.destination_address = dest_address
        export_config_request.destination_storage_subscription_id = dest_sub_id
        export_config_request.destination_storage_location_id = storage_account.primary_location
        export_config_request.destination_account_id = storage_account.id

    return client.update(resource_group_name, application, export_id, export_config_request)


class ExportConfigurationShow(_ContinuesExportShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.id._id_part = ''
        return args_schema

    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        return {key[0].lower() + key[1:]: value for key, value in output.items()}


class ExportConfigurationList(_ContinuesExportList):
    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        return [{key[0].lower() + key[1:]: value for key, value in item.items()} for item in output]


class ExportConfigurationDelete(_ContinuesExportDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.id._id_part = ''
        return args_schema


def list_web_tests(client, component_name=None, resource_group_name=None):
    if component_name is not None and resource_group_name:
        return client.list_by_component(component_name=component_name, resource_group_name=resource_group_name)
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()


def get_web_test(client, resource_group_name, web_test_name):
    return client.get(resource_group_name=resource_group_name, web_test_name=web_test_name)


def create_web_test(client,
                    resource_group_name,
                    web_test_name,
                    location,
                    tags=None,
                    kind=None,
                    synthetic_monitor_id=None,
                    web_test_properties_name_web_test_name=None,
                    description=None,
                    enabled=None,
                    frequency=None,
                    timeout=None,
                    web_test_kind=None,
                    retry_enabled=None,
                    locations=None,
                    content_validation=None,
                    ssl_check=None,
                    ssl_cert_remaining_lifetime_check=None,
                    expected_http_status_code=None,
                    ignore_https_status_code=None,
                    request_url=None,
                    headers=None,
                    http_verb=None,
                    request_body=None,
                    parse_dependent_requests=None,
                    follow_redirects=None,
                    web_test=None):
    web_test_definition = {}
    web_test_definition['location'] = location
    if tags is not None:
        web_test_definition['tags'] = tags
    if kind is not None:
        web_test_definition['kind'] = kind
    else:
        web_test_definition['kind'] = "ping"
    if synthetic_monitor_id is not None:
        web_test_definition['synthetic_monitor_id'] = synthetic_monitor_id
    if web_test_properties_name_web_test_name is not None:
        web_test_definition['web_test_name'] = web_test_properties_name_web_test_name
    if description is not None:
        web_test_definition['description'] = description
    if enabled is not None:
        web_test_definition['enabled'] = enabled
    if frequency is not None:
        web_test_definition['frequency'] = frequency
    else:
        web_test_definition['frequency'] = 300
    if timeout is not None:
        web_test_definition['timeout'] = timeout
    else:
        web_test_definition['timeout'] = 30
    if web_test_kind is not None:
        web_test_definition['web_test_kind'] = web_test_kind
    else:
        web_test_definition['web_test_kind'] = "ping"
    if retry_enabled is not None:
        web_test_definition['retry_enabled'] = retry_enabled
    if locations is not None:
        web_test_definition['locations'] = locations
    web_test_definition['validation_rules'] = {}
    if content_validation is not None:
        web_test_definition['validation_rules']['content_validation'] = content_validation
    if ssl_check is not None:
        web_test_definition['validation_rules']['ssl_check'] = ssl_check
    if ssl_cert_remaining_lifetime_check is not None:
        web_test_definition['validation_rules']['ssl_cert_remaining_lifetime_check'] = ssl_cert_remaining_lifetime_check
    if expected_http_status_code is not None:
        web_test_definition['validation_rules']['expected_http_status_code'] = expected_http_status_code
    if ignore_https_status_code is not None:
        web_test_definition['validation_rules']['ignore_https_status_code'] = ignore_https_status_code
    if len(web_test_definition['validation_rules']) == 0:
        del web_test_definition['validation_rules']
    web_test_definition['request'] = {}
    if request_url is not None:
        web_test_definition['request']['request_url'] = request_url
    if headers is not None:
        web_test_definition['request']['headers'] = headers
    if http_verb is not None:
        web_test_definition['request']['http_verb'] = http_verb
    if request_body is not None:
        web_test_definition['request']['request_body'] = request_body
    if parse_dependent_requests is not None:
        web_test_definition['request']['parse_dependent_requests'] = parse_dependent_requests
    if follow_redirects is not None:
        web_test_definition['request']['follow_redirects'] = follow_redirects
    if len(web_test_definition['request']) == 0:
        del web_test_definition['request']
    web_test_definition['configuration'] = {}
    if web_test is not None:
        web_test_definition['configuration']['web_test'] = web_test
    if len(web_test_definition['configuration']) == 0:
        del web_test_definition['configuration']
    return client.create_or_update(resource_group_name=resource_group_name,
                                   web_test_name=web_test_name,
                                   web_test_definition=web_test_definition)


# pylint: disable=unused-argument
def update_web_test(instance,
                    resource_group_name,
                    web_test_name,
                    location,
                    tags=None,
                    kind=None,
                    synthetic_monitor_id=None,
                    web_test_properties_name_web_test_name=None,
                    description=None,
                    enabled=None,
                    frequency=None,
                    timeout=None,
                    web_test_kind=None,
                    retry_enabled=None,
                    locations=None,
                    content_validation=None,
                    ssl_check=None,
                    ssl_cert_remaining_lifetime_check=None,
                    expected_http_status_code=None,
                    ignore_https_status_code=None,
                    request_url=None,
                    headers=None,
                    http_verb=None,
                    request_body=None,
                    parse_dependent_requests=None,
                    follow_redirects=None,
                    web_test=None):
    instance.location = location
    if tags is not None:
        instance.tags = tags
    if kind is not None:
        instance.kind = kind
    if synthetic_monitor_id is not None:
        instance.synthetic_monitor_id = synthetic_monitor_id
    if web_test_properties_name_web_test_name is not None:
        instance.web_test_name = web_test_properties_name_web_test_name
    if description is not None:
        instance.description = description
    if enabled is not None:
        instance.enabled = enabled
    if frequency is not None:
        instance.frequency = frequency
    if timeout is not None:
        instance.timeout = timeout
    if web_test_kind is not None:
        instance.web_test_kind = web_test_kind
    if retry_enabled is not None:
        instance.retry_enabled = retry_enabled
    if locations is not None:
        instance.locations = locations
    if content_validation is not None:
        instance.validation_rules.content_validation = content_validation
    if ssl_check is not None:
        instance.validation_rules.ssl_check = ssl_check
    if ssl_cert_remaining_lifetime_check is not None:
        instance.validation_rules.ssl_cert_remaining_lifetime_check = ssl_cert_remaining_lifetime_check
    if expected_http_status_code is not None:
        instance.validation_rules.expected_http_status_code = expected_http_status_code
    if ignore_https_status_code is not None:
        instance.validation_rules.ignore_https_status_code = ignore_https_status_code
    if request_url is not None:
        instance.request.request_url = request_url
    if headers is not None:
        instance.request.headers = headers
    if http_verb is not None:
        instance.request.http_verb = http_verb
    if request_body is not None:
        instance.request.request_body = request_body
    if parse_dependent_requests is not None:
        instance.request.parse_dependent_requests = parse_dependent_requests
    if follow_redirects is not None:
        instance.request.follow_redirects = follow_redirects
    if web_test is not None:
        instance.configuration.web_test = web_test
    return instance


def delete_web_test(client, resource_group_name, web_test_name):
    return client.delete(resource_group_name=resource_group_name, web_test_name=web_test_name)


class WorkbookCreate(_WorkbookCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZBoolArg, AAZListArg, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.mi_system_assigned = AAZBoolArg(
            options=["--mi-system-assigned"],
            help="Enable system assigned identity"
        )
        args_schema.mi_user_assigned = AAZListArg(
            options=["--mi-user-assigned"],
            help="Space separated resource IDs to add user-assigned identities.",
        )
        args_schema.mi_user_assigned.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(template="/subscriptions/{subscription}/resourceGroups/{resource_group}"
                                                "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{}")
        )
        args_schema.identity._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.serialized_data):
            args.serialized_data = 'null'
        if args.mi_system_assigned:
            args.identity.type = "SystemAssigned"
        if has_value(args.mi_user_assigned):
            args.identity.type = "UserAssigned" if not args.identity.type else "SystemAssigned,UserAssigned"
            user_assigned_identities = {}
            for identity in args.mi_user_assigned:
                user_assigned_identities.update({
                    identity.to_serialized_data(): {}
                })
            args.identity.user_assigned_identities = user_assigned_identities


class WorkbookUpdate(_WorkbookUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.identity._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.serialized_data):
            args.serialized_data = 'null'


class IdentityAssign(_IdentityAssign):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZBoolArg, AAZListArg, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.system_assigned = AAZBoolArg(
            options=["--system-assigned"],
            help="Enable system assigned identity"
        )
        args_schema.user_assigned = AAZListArg(
            options=["--user-assigned"],
            help="Space separated resource IDs to add user-assigned identities.",
        )
        args_schema.user_assigned.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(template="/subscriptions/{subscription}/resourceGroups/{resource_group}"
                                                "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{}")
        )
        args_schema.type._registered = False
        args_schema.type._required = False
        args_schema.user_assigned_identities._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if args.system_assigned:
            args.type = "SystemAssigned"
        if has_value(args.user_assigned):
            args.type = "UserAssigned" if not args.type else "SystemAssigned,UserAssigned"
            user_assigned_identities = {}
            for identity in args.user_assigned:
                user_assigned_identities.update({
                    identity.to_serialized_data(): {}
                })
            args.user_assigned_identities = user_assigned_identities

    def pre_instance_create(self):
        self.ctx.vars.instance.properties.serialized_data = 'null'
        old_identity = self.ctx.vars.instance.identity
        args = self.ctx.args

        if args.system_assigned:
            args.type = "SystemAssigned" if not old_identity.type or old_identity.type.to_serialized_data() == 'SystemAssigned' else "SystemAssigned,UserAssigned"
        if has_value(args.user_assigned):
            args.type = "UserAssigned" if not old_identity.type or old_identity.type.to_serialized_data() == 'UserAssigned' else "SystemAssigned,UserAssigned"
            if not old_identity.type:
                user_assigned_identities = {}
            else:
                user_assigned_identities = {} if 'UserAssigned' not in old_identity.type.to_serialized_data() else {**old_identity.user_assigned_identities.to_serialized_data()}
            for identity in args.user_assigned:
                user_assigned_identities.update({
                    identity.to_serialized_data(): {}
                })
            args.user_assigned_identities = user_assigned_identities


class IdentityRemove(_IdentityRemove):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZBoolArg, AAZListArg, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.system_assigned = AAZBoolArg(
            options=["--system-assigned"],
            help="Enable system assigned identity"
        )
        args_schema.user_assigned = AAZListArg(
            options=["--user-assigned"],
            help="Space separated resource IDs to add user-assigned identities.",
        )
        args_schema.user_assigned.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(template="/subscriptions/{subscription}/resourceGroups/{resource_group}"
                                                "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{}")
        )
        args_schema.type._registered = False
        args_schema.user_assigned_identities._registered = False
        return args_schema

    def pre_instance_update(self, instance):
        self.ctx.vars.instance.properties.serialized_data = 'null'
        args = self.ctx.args
        if has_value(args.user_assigned):
            user_assigned_identities = instance.user_assigned_identities
            for identity in args.user_assigned:
                user_assigned_identities._data.pop(identity.to_serialized_data(), None)
            args.user_assigned_identities = user_assigned_identities
        if instance.user_assigned_identities and 'SystemAssigned' in instance.type.to_serialized_data():
            args.type = "SystemAssigned,UserAssigned"
        if not instance.user_assigned_identities and 'SystemAssigned' in instance.type.to_serialized_data():
            args.type = 'SystemAssigned'
        if args.system_assigned and instance.user_assigned_identities:
            args.type = 'UserAssigned'
        if args.system_assigned and instance.type.to_serialized_data() == 'SystemAssigned':
            args.type = 'None'
        if not instance.user_assigned_identities and instance.type.to_serialized_data() == 'UserAssigned':
            args.type = 'None'

    def _output(self, *args, **kwargs):
        if not self.ctx.vars.instance.identity.to_serialized_data():
            return {'type': None}
        return self.deserialize_output(self.ctx.selectors.subresource.required(), client_flatten=True)
