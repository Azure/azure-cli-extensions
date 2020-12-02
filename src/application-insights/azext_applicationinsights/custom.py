# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, protected-access

import datetime
import isodate
from knack.util import CLIError
from knack.log import get_logger
from msrestazure.azure_exceptions import CloudError
from azext_applicationinsights.vendored_sdks.applicationinsights.models import ErrorResponseException
from .util import get_id_from_azure_resource, get_query_targets, get_timespan, get_linked_properties
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.profiles import ResourceType

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
        client = applicationinsights_mgmt_plane_client(cmd.cli_ctx, api_version='2020-02-02-preview').components
        return client.create_or_update(resource_group_name, application, existing_component)

    from .vendored_sdks.mgmt_applicationinsights.v2018_05_01_preview.models import ApplicationInsightsComponent
    if retention_in_days is not None:
        existing_component.retention_in_days = retention_in_days
    component = ApplicationInsightsComponent(**(vars(existing_component)))
    return client.create_or_update(resource_group_name, application, component)


def update_component_tags(client, application, resource_group_name, tags):
    return client.update_tags(resource_group_name, application, tags)


def connect_webapp(cmd, resource_group_name, webapp_name, enable_profiler=None, enable_snapshot_debugger=None):
    from azure.cli.command_modules.appservice.custom import update_app_settings

    settings = []
    if enable_profiler is True:
        settings.append("APPINSIGHTS_PROFILERFEATURE_VERSION=1.0.0")
    elif enable_profiler is False:
        settings.append("APPINSIGHTS_PROFILERFEATURE_VERSION=disabled")

    if enable_snapshot_debugger is True:
        settings.append("APPINSIGHTS_SNAPSHOTFEATURE_VERSION=1.0.0")
    elif enable_snapshot_debugger is False:
        settings.append("APPINSIGHTS_SNAPSHOTFEATURE_VERSION=disabled")
    return update_app_settings(cmd, resource_group_name, webapp_name, settings)


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


def create_api_key(cmd, client, application, resource_group_name, api_key, read_properties=None, write_properties=None):
    from .vendored_sdks.mgmt_applicationinsights.models import APIKeyRequest
    if read_properties is None:
        read_properties = ['ReadTelemetry', 'AuthenticateSDKControlChannel']
    if write_properties is None:
        write_properties = ['WriteAnnotations']
        logger.warning('Set write permission to "WriteAnnotations". This default permission will be removed in the future.')
    linked_read_properties, linked_write_properties = get_linked_properties(cmd.cli_ctx, application, resource_group_name, read_properties, write_properties)
    api_key_request = APIKeyRequest(name=api_key,
                                    linked_read_properties=linked_read_properties,
                                    linked_write_properties=linked_write_properties)
    return client.create(resource_group_name, application, api_key_request)


def show_api_key(client, application, resource_group_name, api_key=None):
    if api_key is None:
        return client.list(resource_group_name, application)
    result = list(filter(lambda result: result.name == api_key, client.list(resource_group_name, application)))
    if len(result) == 1:
        return result[0]
    if len(result) > 1:
        return result
    return None


def delete_api_key(client, application, resource_group_name, api_key):
    existing_key = list(filter(lambda result: result.name == api_key, client.list(resource_group_name, application)))
    if existing_key != []:
        return client.delete(resource_group_name, application, existing_key[0].id.split('/')[-1])
    raise CLIError('--api-key provided but key not found for deletion.')


def show_component_billing(client, application, resource_group_name):
    return client.get(resource_group_name=resource_group_name, resource_name=application)


def update_component_billing(client, application, resource_group_name, cap=None, stop_sending_notification_when_hitting_cap=None):
    billing_features = client.get(resource_group_name=resource_group_name, resource_name=application)
    if cap is not None:
        billing_features.data_volume_cap.cap = cap
    if stop_sending_notification_when_hitting_cap is not None:
        billing_features.data_volume_cap.stop_send_notification_when_hit_cap = stop_sending_notification_when_hitting_cap
    return client.update(resource_group_name=resource_group_name,
                         resource_name=application,
                         data_volume_cap=billing_features.data_volume_cap,
                         current_billing_features=billing_features.current_billing_features)


def get_component_linked_storage_account(client, resource_group_name, application):
    return client.get(resource_group_name=resource_group_name, resource_name=application)


def create_component_linked_storage_account(client, resource_group_name, application, storage_account_id):
    return client.create_and_update(resource_group_name=resource_group_name, resource_name=application, linked_storage_account=storage_account_id)


def update_component_linked_storage_account(client, resource_group_name, application, storage_account_id):
    return client.update(resource_group_name=resource_group_name, resource_name=application, linked_storage_account=storage_account_id)


def delete_component_linked_storage_account(client, resource_group_name, application):
    return client.delete(resource_group_name=resource_group_name, resource_name=application)


def list_export_configurations(client, application, resource_group_name):
    return client.list(resource_group_name, application)


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
        raise CLIError("Destination storage account {} does not exist, "
                       "use 'az storage account list' to get storage account list".format(dest_account))

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
        pre_config = get_export_configuration(client, application, resource_group_name, export_id)
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
            raise CLIError("Destination storage account {} does not exist, "
                           "use 'az storage account list' to get storage account list".format(dest_account))

        dest_address = getattr(storage_account.primary_endpoints, dest_type.lower(), '')
        dest_address += dest_container + '?' + dest_sas
        export_config_request.destination_type = dest_type
        export_config_request.destination_address = dest_address
        export_config_request.destination_storage_subscription_id = dest_sub_id
        export_config_request.destination_storage_location_id = storage_account.primary_location
        export_config_request.destination_account_id = storage_account.id

    return client.update(resource_group_name, application, export_id, export_config_request)


def get_export_configuration(client, application, resource_group_name, export_id):
    return client.get(resource_group_name, application, export_id)


def delete_export_configuration(client, application, resource_group_name, export_id):
    return client.delete(resource_group_name, application, export_id)
