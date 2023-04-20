from azure.cli.core.commands import CliCommandType
from azext_acrquery._client_factory import cf_metadata


def load_command_table(self, _):
    acr_metadata_util = CliCommandType(
        operations_tmpl='azext_acrquery.custom#{}',
        client_factory=cf_metadata)

    with self.command_group('acr', acr_metadata_util) as g:
        g.command('query', 'create_query')
