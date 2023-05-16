from azext_load.data_plane.utils import validators, completers
from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list,
    quotes,
    resource_group_name_type,
    get_generic_completion_list
)
from knack.arguments import CLIArgumentType

quote_text = "Use {} to clear existing {{}}.".format(quotes)

# Common arguments
resource_group = resource_group_name_type

load_test_resource = CLIArgumentType(
    options_list=["--load-test-resource", "--name", "-n"],
    type=str,
    required=True,
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

test_run_id = CLIArgumentType(
    validator=validators.validate_test_run_id,
    completer=completers.get_test_run_id_completion_list(),
    options_list=["--test-run-id", "-r"],
    type=str,
    help="Test run ID of the load test run",
)

existing_test_run_id = CLIArgumentType(
    validator=validators.validate_test_run_id,
    completer=completers.get_test_run_id_completion_list(),
    options_list=["--existing-test-run-id"],
    type=str,
    help="Test run ID of an existing load test run",
)

test_display_name = CLIArgumentType(
    options_list=["--display-name"],
    type=str,
    help="Display name of the load test.",
)

test_run_display_name = CLIArgumentType(
    options_list=["--display-name"],
    type=str,
    help="Display name of the load test run.",
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

test_run_description = CLIArgumentType(
    options_list=["--description"],
    type=str,
    help="Description of the load test run.",
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
    validator=validators.validate_path,
    options_list=["--path"],
    type=str,
    help="Path to the directory to download files.",
)

test_run_input = CLIArgumentType(
    options_list=["--input"],
    action="store_true",
    default=False,
    help="Download the input files zip.",
)

test_run_log = CLIArgumentType(
    options_list=["--log"],
    action="store_true",
    default=False,
    help="Download the log files zip.",
)

test_run_results = CLIArgumentType(
    options_list=["--result"],
    action="store_true",
    default=False,
    help="Download the results files zip.",
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
    validator=validators.validate_app_component_type,
    options_list=["--app-component-type"],
    type=str,
    help="Type of resource of the app component.",
)

app_component_kind = CLIArgumentType(
    options_list=["--app-component-kind"],
    type=str,
    help="Kind of the app component.",
)

server_metric_id = CLIArgumentType(
    validator=validators.validate_metric_id,
    options_list=["--metric-id"],
    type=str,
    help="Fully qualified ID of the server metric.",
)

server_metric_name = CLIArgumentType(
    options_list=["--metric-name"],
    type=str,
    help="Name of the server metric.",
)

server_metric_namespace = CLIArgumentType(
    options_list=["--metric-namespace"],
    type=str,
    help="Namespace of the server metric.",
)

server_metric_aggregation = CLIArgumentType(
    options_list=["--aggregation"],
    type=str,
    help="Aggregation of the server metric.",
)

metric_name = CLIArgumentType(
    options_list=["--metric-name"],
    type=str,
    help="Name of the metric.",
)

metric_namespace = CLIArgumentType(
    options_list=["--metric-namespace"],
    type=str,
    help="Namespace of the metric.",
)

metric_dimension = CLIArgumentType(
    options_list=["--metric-dimension"],
    type=str,
    help="Value of the metric dimension.",
)

start_iso_time = CLIArgumentType(
    validator=validators.validate_start_iso_time,
    options_list=["--start-time"],
    type=str,
    help="ISO 8601 formatted start time.",
)

end_iso_time = CLIArgumentType(
    validator=validators.validate_end_iso_time,
    options_list=["--end-time"],
    type=str,
    help="ISO 8601 formatted end time.",
)

interval = CLIArgumentType(
    validator=validators.validate_interval,
    completer=get_generic_completion_list(validators.allowed_intervals),
    options_list=["--interval"],
    type=str,
    help=f"ISO 8601 formatted interval. Allowed values: {', '.join(validators.allowed_intervals)}",
)
