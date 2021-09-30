from azure.cli.core.commands import CliCommandType
from azext_cosmosdb_preview.generated._client_factory import (
    cf_data_transfer_job
)

def load_command_table(self, _):
    cosmosdb_data_transfer_job = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.cosmodb.operations._data_transfer_jobs_operations#DataTransferJobsOperations.{}',
        client_factory=cf_data_transfer_job,
    )
    with self.command_group(
            'cosmosdb data-transfer-job', cosmosdb_data_transfer_job, client_factory=cf_data_transfer_job
        ) as g:
            g.custom_command('create2', 'cosmosdb_data_transfer_job_create2')