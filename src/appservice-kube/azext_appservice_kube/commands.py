# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_plans


def transform_web_output(web):
    props = ['name', 'state', 'location', 'resourceGroup', 'defaultHostName', 'appServicePlanId', 'ftpPublishingUrl']
    result = {k: web[k] for k in web if k in props}
    # to get width under control, also the plan usually is in the same RG
    result['appServicePlan'] = result.pop('appServicePlanId').split('/')[-1]
    return result


def ex_handler_factory(creating_plan=False):
    def _polish_bad_errors(ex):
        import json
        from knack.util import CLIError
        try:
            if 'text/plain' in ex.response.headers['Content-Type']:  # HTML Response
                detail = ex.response.text
            else:
                detail = json.loads(ex.response.text)['Message']
                if creating_plan:
                    if 'Requested features are not supported in region' in detail:
                        detail = ("Plan with linux worker is not supported in current region. For " +
                                  "supported regions, please refer to https://docs.microsoft.com/"
                                  "azure/app-service-web/app-service-linux-intro")
                    elif 'Not enough available reserved instance servers to satisfy' in detail:
                        detail = ("Plan with Linux worker can only be created in a group " +
                                  "which has never contained a Windows worker, and vice versa. " +
                                  "Please use a new resource group. Original error:" + detail)
            ex = CLIError(detail)
        except Exception:  # pylint: disable=broad-except
            pass
        raise ex
    return _polish_bad_errors


def load_command_table(self, _):
    appservice_plan_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.web.operations#AppServicePlansOperations.{}',
        client_factory=cf_plans
    )

    appservice_kube_custom = CliCommandType(operations_tmpl='azext_appservice_kube.custom#{}')

    with self.command_group('appservice kube', is_preview=True) as g:
        g.custom_show_command('show', 'show_kube_environments')
        g.custom_wait_command('wait', 'show_kube_environments')
        g.custom_command('list', 'list_kube_environments')
        g.custom_command('create', 'create_kube_environment', supports_no_wait=True)
        g.custom_command('update', 'update_kube_environment', supports_no_wait=True)
        g.custom_command('delete', 'delete_kube_environment', supports_no_wait=True, confirmation=True)

    with self.command_group('appservice plan', appservice_plan_sdk) as g:
        g.custom_command('create', 'create_app_service_plan', supports_no_wait=True,
                         exception_handler=ex_handler_factory(creating_plan=True))

        g.custom_command('update', 'update_app_service_plan', supports_no_wait=True)

        g.show_command('show', 'get')
        g.custom_command('list', 'list_app_service_plans')

    with self.command_group('webapp') as g:
        g.custom_command('list-runtimes', 'list_runtimes_kube')
        g.custom_command('create', 'create_webapp', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_webapp', table_transformer=transform_web_output)
        g.custom_command('scale', 'scale_webapp')
        g.custom_command('restart', 'restart_webapp')
        g.generic_update_command('update', getter_name='get_webapp', setter_name='set_webapp',
                                 custom_func_name='update_webapp', command_type=appservice_kube_custom)

    with self.command_group('webapp config ssl') as g:
        g.custom_command('bind', 'bind_ssl_cert')
        g.custom_command('unbind', 'unbind_ssl_cert')

    with self.command_group('webapp deployment source') as g:
        g.custom_command('config-zip', 'enable_zip_deploy_webapp')

    with self.command_group('functionapp') as g:
        g.custom_command('create', 'create_functionapp', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_webapp', table_transformer=transform_web_output)
        g.custom_command('restart', 'restart_webapp')

    with self.command_group('functionapp config container') as g:
        g.custom_command('set', 'update_container_settings_functionapp')

    with self.command_group('functionapp deployment source') as g:
        g.custom_command('config-zip', 'enable_zip_deploy_functionapp')
