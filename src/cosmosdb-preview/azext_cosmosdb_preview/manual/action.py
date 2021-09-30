import argparse
from collections import defaultdict
from knack.util import CLIError

def GetDataTransferAzureBlobComponent(properties, component_name):
    d = {}
    for k in properties:
        kl = k.lower()
        v = properties[k]

        if kl == 'container-name':
            d['container_name'] = v[0]

        elif kl == 'endpoint-url':
            d['endpoint_url'] = v[0]

        else:
            raise CLIError(
                'Unsupported Key {} is provided for {} component. All'
                ' possible keys are: container-name, connection'.format(k, component_name)
            )
    d['component'] = 'AzureBlobStorage'
    return d

def GetDataTransferCosmosCassandraComponent(properties, component_name):
    d = {}
    for k in properties:
        kl = k.lower()
        v = properties[k]

        if kl == 'keyspace-name':
            d['keyspace_name'] = v[0]

        elif kl == 'table-name':
            d['table_name'] = v[0]

        else:
            raise CLIError(
                'Unsupported Key {} is provided for {} component. All'
                ' possible keys are: keyspace-name, table-name'.format(k, component_name)
            )
    d['component'] = 'CosmosDBCassandra'
    return d

def GetDataTransferComponent(properties, component_name):
    if 'type' not in properties:
        raise CLIError(
            'Missing required key type in {}.'.format(component_name)
            ) 
    component_type = properties['type'][0].lower()
    del properties['type']
    if component_type == 'cosmosdbcassandra':
        return GetDataTransferCosmosCassandraComponent(properties, component_name)
    elif component_type == 'azureblobstorage':
        return GetDataTransferAzureBlobComponent(properties, component_name)
    else:
        raise CLIError(
            'Unsupported type {} is provided for {} component. All'
            ' possible types are: CosmosDBCassandra, AzureBlobStorage'.format(component_type, component_name)
            )

class AddDataTransferDataSource(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.source = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string)) 
        return GetDataTransferComponent(properties, 'source')
        

class AddDataTransferDataSink(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.destination = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        return GetDataTransferComponent(properties, 'destination')