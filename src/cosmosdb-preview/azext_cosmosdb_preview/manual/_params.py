
from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)

from azext_cosmosdb_preview.action import (
    AddDataTransferDataSource,
    AddDataTransferDataSink
)

def load_arguments(self, _):
    with self.argument_context('cosmosdb data-transfer-job create2') as c:
            c.argument('resource_group_name', resource_group_name_type)
            c.argument('account_name', type=str, help='Cosmos DB database account name.')
            c.argument('job_name', type=str, help='Name of the Data Transfer Job')
            c.argument('source', action=AddDataTransferDataSource, nargs='+', help='Source component of Data Transfer job', arg_group='Component')
            c.argument('destination', action=AddDataTransferDataSink, nargs='+', help='Destination component of Data Transfer job', arg_group='Component')

    with self.argument_context('cosmosdb service list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('account_name', type=str, help='Cosmos DB database account name.')

    with self.argument_context('cosmosdb service show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('account_name', type=str, help='Cosmos DB database account name.', id_part='name')
        c.argument('service_name', options_list=['--service-name'], type=str, help='Cosmos DB service '
                   'name.', id_part='child_name_1')

    with self.argument_context('cosmosdb service create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('account_name', type=str, help='Cosmos DB database account name.')
        c.argument('service_name', options_list=['--service-name'], type=str, help='Cosmos DB service '
                   'name.')
        c.argument('instance_size', arg_type=get_enum_type(['Cosmos.D4s', 'Cosmos.D8s', 'Cosmos.D16s']),
                   help='Instance type for the service.')
        c.argument('instance_count', type=int, help='Instance count for the service.')
        c.argument('service_type', arg_type=get_enum_type(['SqlDedicatedGateway', 'DataTransferService',
                                                           'GraphAPICompute']), help='ServiceType for the service.')

    with self.argument_context('cosmosdb service delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('account_name', type=str, help='Cosmos DB database account name.', id_part='name')
        c.argument('service_name', options_list=['--service-name'], type=str, help='Cosmos DB service '
                   'name.', id_part='child_name_1')

    with self.argument_context('cosmosdb service wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('account_name', type=str, help='Cosmos DB database account name.', id_part='name')
        c.argument('service_name', options_list=['--service-name'], type=str, help='Cosmos DB service '
                   'name.', id_part='child_name_1')