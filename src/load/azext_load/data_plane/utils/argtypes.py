from azext_load.data_plane.utils import validators, completers
from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list,
    quotes,
    resource_group_name_type,
)
from knack.arguments import CLIArgumentType

quote_text = "Use {} to clear existing {{}}.".format(quotes)

# Common arguments
resource_group = resource_group_name_type

load_test_resource = CLIArgumentType(
    options_list=["--load-test-resource", "--name", "-n"],
    type=str,
    completer=get_resource_name_completion_list("Microsoft.LoadTestService/LoadTests"),
    help="Name or ARM resource ID of the load test resource.",
)
#

test_id = CLIArgumentType(
    validator=validators.validate_test_id,
    completer=completers.get_test_id_completion_list(),
    options_list=["--test-id", "-t"],
    type=str,
    help="Test ID of the load test",
)

env = CLIArgumentType(
    validator=validators.validate_env_vars,
    nargs="*",
    help="space-separated environment variables: key[=value] [key[=value] ...]. {}".format(
        quote_text.format("environment variables")
    ),
)

secret = CLIArgumentType(
    validator=validators.validate_secrets,
    nargs="*",
    help="space-separated secrets: key[=value] [key[=value] ...]. {}".format(
        quote_text.format("secrets")
    ),
)

certificate = CLIArgumentType(
    validator=validators.validate_certificate,
    nargs="?",
    help="a single certificate in 'key[=value]' format. {}".format(
        quote_text.format("certificate")
    ),
)

app_component_id = CLIArgumentType(
    validator=validators.validate_app_component_id,
    options_list=["--app-component-id"],
    type=str,
    help="Fully qualified ID of the app component resource.",
)

metric_id = CLIArgumentType(
    validator=validators.validate_metric_id,
    options_list=["--metric-id"],
    type=str,
    help="Fully qualified ID of the server metric.",
)
