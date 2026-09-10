from azure.cli.core import AzCommandsLoader


class AlrsCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        from azext_alrs._client_factory import cf_alrs

        alrs_custom = CliCommandType(
            operations_tmpl="azext_alrs.commands.registry#{}",
            client_factory=cf_alrs,
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=alrs_custom)

    def load_command_table(self, args):
        from azure.cli.core.aaz import load_aaz_command_table

        from azext_alrs.commands import load_command_table

        load_aaz_command_table(self, "azext_alrs.aaz", args)
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_alrs.commands import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = AlrsCommandsLoader
