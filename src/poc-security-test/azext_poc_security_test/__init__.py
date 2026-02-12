from azure.cli.core import AzCommandsLoader

class PocSecurityTestCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        super().__init__(cli_ctx)

def get_command_modules():
    return []

COMMAND_LOADER_CLS = PocSecurityTestCommandsLoader
