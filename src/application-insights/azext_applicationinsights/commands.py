# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from azure.cli.core.commands import CliCommandType

from azext_applicationinsights._client_factory import (
    cf_events,
    cf_metrics,
    cf_query,
    cf_components,
    cf_export_configuration,
    cf_web_test
)


def load_command_table(self, _):

    metrics_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.vendored_sdks.applicationinsights.operations.metrics_operations#MetricsOperations.{}',
        client_factory=cf_metrics
    )

    events_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.vendored_sdks.applicationinsights.operations.events_operations#EventsOperations.{}',
        client_factory=cf_events
    )

    query_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.vendored_sdks.applicationinsights.operations.query_operations#QueryOperations.{}',
        client_factory=cf_query
    )

    components_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.vendored_sdks.mgmt_applicationinsights.operations.components_operations#ComponentsOperations.{}',
        client_factory=cf_components
    )

    components_custom_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.custom#{}',
        client_factory=cf_components
    )

    export_configurations_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.vendored_sdks.mgmt_applicationinsights.operations.export_configurations_operations#ExportConfigurationsOperations.{}',
        client_factory=cf_export_configuration
    )

    export_configurations_custom_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.custom#{}',
        client_factory=cf_export_configuration
    )

    web_test_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.vendored_sdks.mgmt_applicationinsights.v2018_05_01_preview.operations#WebTestsOperations.{}',
        client_factory=cf_web_test
    )

    web_test_custom_sdk = CliCommandType(
        operations_tmpl='azext_applicationinsights.custom#{}',
        client_factory=cf_web_test
    )

    with self.command_group('monitor app-insights component', command_type=components_sdk, custom_command_type=components_custom_sdk) as g:
        g.custom_command('create', 'create_or_update_component')
        g.custom_command('update', 'update_component')
        g.custom_show_command('show', 'show_components')
        g.custom_command('delete', 'delete_component')
        g.custom_command('update-tags', 'update_component_tags')
        g.custom_command('connect-webapp', 'connect_webapp')
        g.custom_command('connect-function', 'connect_function')

    with self.command_group('monitor app-insights component billing'):
        from .custom import BillingShow, BillingUpdate
        self.command_table['monitor app-insights component billing show'] = BillingShow(loader=self)
        self.command_table['monitor app-insights component billing update'] = BillingUpdate(loader=self)

    with self.command_group('monitor app-insights api-key'):
        from .custom import APIKeyCreate, APIKeyShow, APIKeyDelete
        self.command_table['monitor app-insights api-key create'] = APIKeyCreate(loader=self)
        self.command_table['monitor app-insights api-key show'] = APIKeyShow(loader=self)
        self.command_table['monitor app-insights api-key delete'] = APIKeyDelete(loader=self)

    with self.command_group('monitor app-insights metrics', metrics_sdk) as g:
        g.custom_show_command('show', 'get_metric')
        g.custom_command('get-metadata', 'get_metrics_metadata')

    with self.command_group('monitor app-insights events', events_sdk) as g:
        g.custom_show_command('show', 'get_events')

    with self.command_group('monitor app-insights', query_sdk) as g:
        g.custom_command('query', 'execute_query')

    with self.command_group('monitor app-insights component linked-storage'):
        from .custom import LinkedStorageAccountLink, LinkedStorageAccountUpdate, LinkedStorageAccountShow, LinkedStorageAccountUnlink
        self.command_table['monitor app-insights component linked-storage link'] = LinkedStorageAccountLink(loader=self)
        self.command_table['monitor app-insights component linked-storage update'] = LinkedStorageAccountUpdate(loader=self)
        self.command_table['monitor app-insights component linked-storage show'] = LinkedStorageAccountShow(loader=self)
        self.command_table['monitor app-insights component linked-storage unlink'] = LinkedStorageAccountUnlink(loader=self)

    with self.command_group('monitor app-insights component continues-export'):
        from .custom import ExportConfigurationShow, ExportConfigurationDelete, ExportConfigurationList
        self.command_table['monitor app-insights component continues-export show'] = ExportConfigurationShow(loader=self)
        self.command_table['monitor app-insights component continues-export list'] = ExportConfigurationList(loader=self)
        self.command_table['monitor app-insights component continues-export delete'] = ExportConfigurationDelete(loader=self)

    with self.command_group('monitor app-insights component continues-export', command_type=export_configurations_sdk, custom_command_type=export_configurations_custom_sdk) as g:
        g.custom_command('create', 'create_export_configuration')
        g.custom_command('update', 'update_export_configuration')

    with self.command_group('monitor app-insights web-test', command_type=web_test_sdk, custom_command_type=web_test_custom_sdk) as g:
        g.custom_command('list', 'list_web_tests')
        g.custom_show_command('show', 'get_web_test')
        g.custom_command('create', 'create_web_test')
        g.generic_update_command('update', custom_func_name='update_web_test', setter_arg_name='web_test_definition')
        g.custom_command('delete', 'delete_web_test', confirmation=True)
