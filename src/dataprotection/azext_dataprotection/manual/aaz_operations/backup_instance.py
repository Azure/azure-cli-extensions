from azext_dataprotection.aaz.latest.data_protection.backup_instance import \
    Create as _BackupInstanceCreate, ValidateForBackup as _BackupInstanceValidateForBackup
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.aaz import AAZObjectArg

class BackupInstanceValidateForBackup(_BackupInstanceValidateForBackup):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        
        _args_schema.backup_instance.validation_type._registered = False
        _args_schema.backup_instance.policy_info._registered = False

        _args_schema.backup_instance.data_source_set_info._nullable = True
        _args_schema.backup_instance.datasource_auth_credentials._nullable = True

        # _policy_data_store_param = _args_schema.backup_instance.policy_info.policy_parameters.data_store_parameters_list
        # _policy_data_store_param.Element = AAZObjectArg()
        # _policy_data_store_param.Element.azure_operational_store_parameters = AAZObjectArg(
        #     options=["azure-operational-store-parameters"],
        # )
        # _policy_data_store_param.Element.data_store_type = AAZStrArg(
        #     options=["data-store-type"],
        #     help="type of datastore; Operational/Vault/Archive",
        #     required=True,
        #     enum={"ArchiveStore": "ArchiveStore", "OperationalStore": "OperationalStore", "VaultStore": "VaultStore"},
        # )
        # _policy_data_store_param.Element.resource_group_id = AAZStrArg(
        #     options=["resource-group-id"],
        #     help="Gets or sets the Snapshot Resource Group Uri.",
        # )

        return cls._args_schema

class BackupInstanceCreate(_BackupInstanceCreate):
    
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        _args_schema = cls._args_schema
        _args_schema.backup_instance = AAZObjectArg(
            options=["--backup-instance"],
            arg_group="Parameters",
            help="Backup Instance",
            required=True
        )

        backup_instance = _args_schema.backup_instance
        backup_instance.data_source_info = _args_schema.data_source_info
        backup_instance.data_source_set_info = _args_schema.data_source_set_info
        backup_instance.datasource_auth_credentials = _args_schema.datasource_auth_credentials
        backup_instance.object_type = _args_schema.object_type

        _args_schema.data_source_info._registered = False

        return cls._args_schema

# def dataprotection_backup_instance_validate_for_backup(cmd, vault_name, resource_group_name, backup_instance, no_wait=False):
#     ValidateForBackup(cli_ctx=cmd.cli_ctx)(command_args={
#         "resource_group": resource_group_name,
#         "vault_name": vault_name,
#         "backup_instance": backup_instance['properties']
#     })