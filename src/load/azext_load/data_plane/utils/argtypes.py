# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azext_load.data_plane.utils import completers, models, utils, validators
from azure.cli.core.commands.parameters import (
    get_generic_completion_list,
    get_resource_name_completion_list,
    quotes,
    resource_group_name_type,
)
from knack.arguments import CLIArgumentType

quote_text = f"Use {quotes} to clear existing {{}}."

# Common arguments
resource_group = resource_group_name_type

load_test_resource = CLIArgumentType(
    options_list=["--load-test-resource", "--name", "-n"],
    type=str,
    required=True,
    completer=get_resource_name_completion_list("Microsoft.LoadTestService/LoadTests"),
    help="Name or ARM resource ID of the Load Testing resource.",
)

custom_no_wait = CLIArgumentType(
    options_list=["--no-wait"],
    action="store_true",
    default=False,
    help="Do not wait for the long-running operation to finish.",
)

force = CLIArgumentType(
    options_list=["--force"],
    action="store_true",
    default=False,
    help="Force run the command. This will create the directory to download files if it does not exist.",
)
#

test_id = CLIArgumentType(
    validator=validators.validate_test_id,
    completer=completers.get_test_id_completion_list(),
    options_list=["--test-id", "-t"],
    type=str,
    help="Test ID of the load test",
)

test_id_no_completer = CLIArgumentType(
    validator=validators.validate_test_id,
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

test_run_id_no_completer = CLIArgumentType(
    validator=validators.validate_test_run_id,
    options_list=["--test-run-id", "-r"],
    type=str,
    help="Test run ID of the load test run",
)

existing_test_run_id = CLIArgumentType(
    validator=validators.validate_test_run_id,
    completer=completers.get_test_run_id_completion_list(),
    options_list=["--existing-test-run-id"],
    type=str,
    help="Test run ID of an existing load test run which should be rerun.",
)

test_plan = CLIArgumentType(
    validator=validators.validate_test_plan_path,
    options_list=["--test-plan"],
    type=str,
    help="Path to the JMeter script.",
)

load_test_config_file = CLIArgumentType(
    validator=validators.validate_load_test_config_file,
    options_list=["--load-test-config-file"],
    type=str,
    help="Path to the load test config file. Refer https://learn.microsoft.com/azure/load-testing/reference-test-config-yaml.",
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
    help="Number of engine instances on which the test should run.",
)

key_vault_reference_identity = CLIArgumentType(
    options_list=["--keyvault-reference-id"],
    type=str,
    help="The identity that will be used to access the key vault.",
)

split_csv = CLIArgumentType(
    validator=validators.validate_split_csv,
    options_list=["--split-csv"],
    type=str,
    help="Split CSV files evenly among engine instances.",
)

subnet_id = CLIArgumentType(
    validator=validators.validate_subnet_id,
    options_list=["--subnet-id"],
    type=str,
    help="Resource ID of the subnet to use for private load test.",
)

test_description = CLIArgumentType(
    options_list=["--description"],
    type=str,
    help="Description of the load test.",
)

test_run_description = CLIArgumentType(
    options_list=["--description"],
    type=str,
    help="Description of the load test run.",
)

env = CLIArgumentType(
    validator=validators.validate_env_vars,
    options_list=["--env"],
    nargs="*",
    help="space-separated environment variables: key[=value] [key[=value] ...]. "
    + quote_text.format("environment variables"),
)

secret = CLIArgumentType(
    validator=validators.validate_secrets,
    options_list=["--secret"],
    nargs="*",
    help="space-separated secrets: key[=value] [key[=value] ...]. Secrets should be stored in Azure Key Vault, and the secret identifier should be provided as the value."
    + quote_text.format("secrets"),
)

certificate = CLIArgumentType(
    validator=validators.validate_certificate,
    options_list=["--certificate"],
    nargs="?",
    help="a single certificate in 'key[=value]' format. The certificate should be stored in Azure Key Vault in PFX format, and the certificate identifier should be provided as the value."
    + quote_text.format("certificate"),
)

dir_path = CLIArgumentType(
    validator=validators.validate_dir_path,
    options_list=["--path"],
    type=str,
    help="Path of the directory to download files.",
)

file_name = CLIArgumentType(
    options_list=["--file-name"],
    type=str,
    help="Name of the file.",
)

file_path = CLIArgumentType(
    validator=validators.validate_file_path,
    options_list=["--path"],
    type=str,
    help="Path to the file to upload.",
)

file_type = CLIArgumentType(
    validator=validators.validate_file_type,
    completer=get_generic_completion_list(
        utils.get_enum_values(models.AllowedFileTypes)
    ),
    options_list=["--file-type"],
    type=str,
    help=f"Type of file to be uploaded. Allowed values: {', '.join(utils.get_enum_values(models.AllowedFileTypes))}",
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
    help="Fully qualified resource ID of the App Component. For example, subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.LoadTestService/loadtests/{resName}",
)

app_component_name = CLIArgumentType(
    options_list=["--app-component-name"],
    type=str,
    help="Name of the app component. Refer https://learn.microsoft.com/cli/azure/resource#az-resource-show",
)

app_component_type = CLIArgumentType(
    validator=validators.validate_app_component_type,
    options_list=["--app-component-type"],
    type=str,
    help="Type of resource of the app component. Refer https://learn.microsoft.com/cli/azure/resource#az-resource-show",
)

app_component_kind = CLIArgumentType(
    options_list=["--app-component-kind"],
    type=str,
    help="Kind of the app component. Refer https://learn.microsoft.com/cli/azure/resource#az-resource-show",
)

server_metric_id = CLIArgumentType(
    validator=validators.validate_metric_id,
    options_list=["--metric-id"],
    type=str,
    help="Fully qualified ID of the server metric. Refer https://docs.microsoft.com/en-us/rest/api/monitor/metric-definitions/list#metricdefinition",
)

server_metric_name = CLIArgumentType(
    options_list=["--metric-name"],
    type=str,
    help="Name of the metric. Example, requests/duration",
)

server_metric_namespace = CLIArgumentType(
    options_list=["--metric-namespace"],
    type=str,
    help="Namespace of the server metric. Example, microsoft.insights/components",
)

server_metric_aggregation = CLIArgumentType(
    options_list=["--aggregation"],
    type=str,
    help="Aggregation to be applied on the metric.",
)

metric_name = CLIArgumentType(
    options_list=["--metric-name", "--metric-definition-name"],
    type=str,
    help="Name of the metric.",
)

metric_namespace = CLIArgumentType(
    validator=validators.validate_metric_namespaces,
    completer=get_generic_completion_list(
        utils.get_enum_values(models.AllowedMetricNamespaces)
    ),
    options_list=["--metric-namespace"],
    required=True,
    type=str,
    help=f"Namespace of the metric. Allowed values: {', '.join(utils.get_enum_values(models.AllowedMetricNamespaces))}",
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
    completer=get_generic_completion_list(
        utils.get_enum_values(models.AllowedIntervals)
    ),
    options_list=["--interval"],
    type=str,
    help=f"ISO 8601 formatted interval. Allowed values: {', '.join(utils.get_enum_values(models.AllowedIntervals))}",
)

aggregation = CLIArgumentType(
    options_list=["--aggregation"],
    type=str,
    help="Operation used to aggregate the metrics",
)

dimension_filters = CLIArgumentType(
    validator=validators.validate_dimension_filters,
    options_list=["--dimension-filters"],
    nargs="*",
    help=(
        "space and comma-separated dimension filters: key1[=value1] key1[=value2] key2[=value3] format ...]. "
        "* is supported as a wildcard for both key and value. "
        "Example: `--dimension-filters key1=value1 key2=*`, `--dimension-filters *`"
    ),
)
