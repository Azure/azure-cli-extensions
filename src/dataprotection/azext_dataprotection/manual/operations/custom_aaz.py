from azext_dataprotection.aaz.latest.data_protection.backup_vault import \
    List as _DataprotectionBackupVaultList

class DataprotectionBackupVaultList(_DataprotectionBackupVaultList):

    def pre_operations(self):
        print("In custom pre_operations")
        args = self.ctx.args
        print(dir(args))
        print(args._data)
        print(args.to_serialized_data)
        if 'resource_group' in args._data.keys():
            print(args._data['resource_group'])
        # if args._data['resource_group']:
        #     print(args._data['resource_group'])