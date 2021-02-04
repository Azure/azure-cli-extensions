# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def get_logging(client, timeout=None):
    from azure.core.exceptions import ServiceRequestError
    from knack.util import CLIError
    results = {}
    for (name, service_client) in client.items():
        try:
            if name == 'table':
                results[name] = service_client.get_table_service_properties(timeout=timeout).__dict__['logging']
            else:
                results[name] = service_client.get_service_properties(timeout=timeout).get('analytics_logging', None)
        except ServiceRequestError as ex:
            if ex.message and 'Failed to establish a new connection: [Errno 11001] getaddrinfo failed' in ex.message:
                raise CLIError("Your storage account doesn't support logging for {} service. "
                               "Please change value for --services in your commands.".format(name))
            raise ex
    return results


def set_logging(cmd, client, log, retention, version=None, timeout=None):
    retention_policy = {'enabled': retention != 0, 'days':  retention if retention != 0 else None}
    logging = {'delete': 'd' in log, 'read': 'r' in log, 'write': 'w' in log,
               'version': str(version) if version else u'1.0', 'retention_policy': retention_policy}

    for (name, service_client) in client.items():
        if name == 'table':
            from azure.cli.core.profiles import get_sdk, ResourceType
            t_logging, t_retention_policy = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE, 'Logging',
                                                    'RetentionPolicy',
                                                    mod='common.models')
            table_retention_policy = t_retention_policy(enabled=retention_policy['enabled'],
                                                        days=retention_policy['days'])
            table_logging = t_logging(delete=logging['delete'], read=logging['read'], write=logging['write'],
                                      retention_policy=table_retention_policy)
            service_client.set_table_service_properties(logging=table_logging, timeout=timeout)
        else:
            service_client.set_service_properties(analytics_logging=logging, timeout=timeout)


def disable_logging(cmd, client, timeout=None):
    return set_logging(cmd, client, '', 0, version=None, timeout=timeout)
