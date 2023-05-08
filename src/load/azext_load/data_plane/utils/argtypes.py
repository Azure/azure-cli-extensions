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

display_name = CLIArgumentType(
    options_list=["--display-name"],
    type=str,
    help="Display name of the load test.",
)

engine_instances = CLIArgumentType(
    options_list=["--engine-instances"],
    type=int,
    help="Number of engine instances to use for the load test.",
)

key_vault_reference_identity = CLIArgumentType(
    options_list=["--key-vault-reference-identity"],
    type=str,
    help="The identity that will be used to access the key vault.",
)

load_test_config_file = CLIArgumentType(
    options_list=["--load-test-config-file"],
    type=str,
    help="Path to the load test config file.",
)

subnet_id = CLIArgumentType(
    options_list=["--subnet-id"],
    type=str,
    help="ID of the subnet to use for the load test incase of private network.",
)

test_description = CLIArgumentType(
    options_list=["--test-description"],
    type=str,
    help="Description of the load test.",
)

test_plan = CLIArgumentType(
    options_list=["--test-plan"],
    type=str,
    help="Path to the test plan file.",
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

path = CLIArgumentType(
    options_list=["--path"],
    type=str,
    help="Path to the directory containing downloaded files.",
)

app_component_id = CLIArgumentType(
    validator=validators.validate_app_component_id,
    options_list=["--app-component-id"],
    type=str,
    help="Fully qualified ID of the app component resource.",
)

app_component_name = CLIArgumentType(
    options_list=["--app-component-name"],
    type=str,
    help="Name of the app component.",
)

app_component_type = CLIArgumentType(
    options_list=["--app-component-type"],
    type=str,
    help="Type of resource of the app component.",
)

app_component_kind = CLIArgumentType(
    options_list=["--app-component-kind"],
    type=str,
    help="Kind of the app component.",
)

metric_id = CLIArgumentType(
    validator=validators.validate_metric_id,
    options_list=["--metric-id"],
    type=str,
    help="Fully qualified ID of the server metric.",
)

metric_name = CLIArgumentType(
    options_list=["--metric-name"],
    type=str,
    help="Name of the server metric.",
)

metric_namespace = CLIArgumentType(
    options_list=["--metric-namespace"],
    type=str,
    help="Namespace of the server metric.",
)

aggregation = CLIArgumentType(
    options_list=["--aggregation"],
    type=str,
    help="Aggregation of the server metric.",
)
