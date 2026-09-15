from azure.cli.core import AzCommandsLoader


class AprCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        from azext_apr._client_factory import cf_apr

        apr_custom = CliCommandType(
            operations_tmpl="azext_apr.commands.registry#{}",
            client_factory=cf_apr,
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=apr_custom)

    def load_command_table(self, args):
        from azure.cli.core.aaz import load_aaz_command_table

        from azext_apr.commands import load_command_table

        load_aaz_command_table(self, "azext_apr.aaz", args)
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_apr.commands import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = AprCommandsLoader
