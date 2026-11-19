from knack.util import CLIError

from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id

from azure.cli.command_modules.appservice._client_factory import web_client_factory
from azure.cli.command_modules.appservice._constants import LINUX_OS_NAME

_DOTNET_TEN_UNSUPPORTED_MESSAGE = ('.NET 10 (DOTNET-ISOLATED|10.0) is not supported on Linux Consumption plans. '
                                   'Use a Flex Consumption plan or choose a supported runtime version.')


def _is_dotnet_ten_linux_fx_version(linux_fx_version):
    if not linux_fx_version:
        return False
    normalized = linux_fx_version.strip().upper()
    if not normalized.startswith('DOTNET-ISOLATED|'):
        return False
    return normalized.split('|', 1)[1].strip().startswith('10')


def _is_dotnet_ten_runtime(runtime, runtime_version):
    if not runtime or runtime_version is None:
        return False
    if runtime.lower() != 'dotnet-isolated':
        return False
    return str(runtime_version).strip().startswith('10')


def _get_plan(cmd, resource_group_name, plan):
    if not resource_group_name or not plan:
        return None

    client = web_client_factory(cmd.cli_ctx)
    if is_valid_resource_id(plan):
        parsed = parse_resource_id(plan)
        return client.app_service_plans.get(parsed['resource_group'], parsed['name'])

    return client.app_service_plans.get(resource_group_name, plan)


def _is_linux_consumption_plan(plan):
    if not plan:
        return False

    sku = getattr(plan, 'sku', None)
    return bool(getattr(plan, 'reserved', False) and sku and getattr(sku, 'name', '').upper() == 'Y1')


def validate_dotnet_ten_runtime_for_create(namespace):
    runtime = getattr(namespace, 'runtime', None)
    runtime_version = getattr(namespace, 'runtime_version', None)
    if not _is_dotnet_ten_runtime(runtime, runtime_version):
        return

    os_type = getattr(namespace, 'os_type', None)
    is_linux = bool(os_type and os_type.lower() == LINUX_OS_NAME)
    if not is_linux:
        return

    if getattr(namespace, 'consumption_plan_location', None):
        raise CLIError(_DOTNET_TEN_UNSUPPORTED_MESSAGE)

    plan = _get_plan(namespace.cmd, getattr(namespace, 'resource_group_name', None), getattr(namespace, 'plan', None))
    if _is_linux_consumption_plan(plan):
        raise CLIError(_DOTNET_TEN_UNSUPPORTED_MESSAGE)


def validate_dotnet_ten_linux_fx_version_for_config_set(namespace):
    if not _is_dotnet_ten_linux_fx_version(getattr(namespace, 'linux_fx_version', None)):
        return

    client = web_client_factory(namespace.cmd.cli_ctx)
    resource_group_name = getattr(namespace, 'resource_group_name', None)
    name = getattr(namespace, 'name', None)
    slot = getattr(namespace, 'slot', None)
    webapp = client.web_apps.get(resource_group_name, name, slot=slot) if slot else client.web_apps.get(resource_group_name, name)

    if not getattr(webapp, 'reserved', False):
        return

    plan = _get_plan(namespace.cmd, resource_group_name, webapp.server_farm_id)
    if _is_linux_consumption_plan(plan):
        raise CLIError(_DOTNET_TEN_UNSUPPORTED_MESSAGE)
