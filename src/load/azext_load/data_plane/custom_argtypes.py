from knack.arguments import CLIArgumentType
from azure.cli.core.commands import validators
from azure.cli.core.commands.parameters import quotes
from azext_load.data_plane.custom_validator import (
    validate_secrets,
    validate_certificate,
)
from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list,
    resource_group_name_type,
)


quote_text = "Use {} to clear existing {{}}.".format(quotes)

# Common arguments
resource_group = resource_group_name_type

load_test_resource = CLIArgumentType(
    options_list=["--load-test-resource", "--name", "-n"],
    type=str,
    completer=get_resource_name_completion_list("Microsoft.LoadTestService/LoadTests"),
    help="Name or ARM resource ID of the load test resource.",
)

# Common arguments for load test
test_id = CLIArgumentType(
    options_list=["--test-id", "-t"], type=str, help="Test ID of the load test"
)

# Arguments for load test create
env_type = CLIArgumentType(
    # validator=validators.validate_tags,
    nargs="*",
    help="space-separated environment variables: key[=value] [key[=value] ...]. {}".format(
        quote_text.format("environment variables")
    ),
)

secret_type = CLIArgumentType(
    validator=validate_secrets,
    nargs="*",
    help="space-separated secrets: key[=value] [key[=value] ...]. {}".format(
        quote_text.format("secrets")
    ),
)

certificate_type = CLIArgumentType(
    validator=validate_certificate,
    help="a single certificate in 'key[=value]' format. {}".format(
        quote_text.format("certificate")
    ),
    nargs="?",
    const="",
)
