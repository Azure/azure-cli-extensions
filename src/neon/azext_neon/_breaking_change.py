
from azure.cli.core.breaking_change import register_command_group_deprecate
from azure.cli.core.breaking_change import register_other_breaking_change

register_command_group_deprecate('az neon')

message = """Deprecation Notice: The Neon Azure Native Integration is being deprecated and will
reach end of life on January 31, 2026. Transfer your projects to a Neon managed organization
today. Migration documentation is available at https://neon.com/docs/import/migrate-from-azure-native"""

register_other_breaking_change('az neon', message)
