# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_kube_environments, cf_plans
from ._validators import validate_asp_sku, validate_app_or_slot_exists_in_rg


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

    kube_environments_sdk = CliCommandType(
        operations_tmpl='azext_appservice_kube.vendored_sdks.azure_mgmt_web.operations#KubeEnvironmentsOperations.{}',
        client_factory=cf_kube_environments
    )

    appservice_plan_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.web.operations#AppServicePlansOperations.{}',
        client_factory=cf_plans
    )

    with self.command_group('appservice kube', kube_environments_sdk, is_preview=True) as g:
        g.show_command('show')
        g.wait_command('wait')
        g.custom_command('list', 'list_kube_environments', client_factory=cf_kube_environments)
        g.custom_command('create', 'create_kube_environment', client_factory=cf_kube_environments, supports_no_wait=True)
        g.custom_command('update', 'update_kube_environment', client_factory=cf_kube_environments, supports_no_wait=True)
        g.command('delete', 'delete', supports_no_wait=True, confirmation=True)

    with self.command_group('appservice plan', appservice_plan_sdk) as g:
        g.custom_command('create', 'create_app_service_plan', supports_no_wait=True,
                         exception_handler=ex_handler_factory(creating_plan=True))
        g.generic_update_command('update', custom_func_name='update_app_service_plan', setter_arg_name='app_service_plan',
                                 validator=validate_asp_sku, supports_no_wait=True)

    with self.command_group('webapp') as g:
        g.custom_command('create', 'create_webapp', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_webapp', table_transformer=transform_web_output,
                              validator=validate_app_or_slot_exists_in_rg)
        g.custom_command('up', 'webapp_up', exception_handler=ex_handler_factory())

    with self.command_group('functionapp') as g:
        g.custom_command('create', 'create_function', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_webapp', table_transformer=transform_web_output)
