# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argcomplete.completers import FilesCompleter
from knack.arguments import CLIArgumentType

# pylint: disable=import-error,no-name-in-module
from azure.cli.core.commands.parameters import resource_group_name_type

from ._managed_connection import AUTH_MODES as MANAGED_AUTH_MODES


def load_arguments(self, _):
    path_type = CLIArgumentType(options_list=['--path'], completer=FilesCompleter(), help='Project root path.')
    port_type = CLIArgumentType(options_list=['--port'], type=int, help='Local runtime port.')
    host_key_type = CLIArgumentType(options_list=['--host-key'], help='Master key for a local host that requires one. Sent as an x-functions-key header.')
    target_context_type = CLIArgumentType(options_list=['--context'], help='Named Logic Apps CLI context used to resolve target coordinates.')
    app_name_type = CLIArgumentType(options_list=['--name', '-n'], help='Name of the Logic App Standard site.')
    workflow_type = CLIArgumentType(options_list=['--workflow'], help='Workflow name.')
    trigger_type = CLIArgumentType(options_list=['--trigger'], help='Trigger name.')
    run_id_type = CLIArgumentType(options_list=['--run-id'], help='Workflow run id.')

    for command in ('create', 'run'):
        with self.argument_context('logicapp test ' + command) as c:
            c.argument('path', arg_type=path_type, help='Existing local Standard project. Defaults to the named/active local context, then current directory. An explicit path bypasses the implicit active context.')
            c.argument('context', arg_type=target_context_type, help='Named local project context. Cloud contexts cannot supply a local test project.')
            c.argument('workflow', arg_type=workflow_type, required=True, help='One explicit local workflow directory name.')

    with self.argument_context('logicapp test create') as c:
        c.argument('output_path', options_list=['--output-path'], completer=FilesCompleter(), help='New test directory. Relative paths use the selected project; default Tests/WORKFLOW. Existing directories are refused, not overwritten. No restore or execution.')
        c.argument('trigger', arg_type=trigger_type, help='Existing workflow trigger to mock. Required only when more than one trigger exists.')

    with self.argument_context('logicapp test run') as c:
        c.argument('test_project', options_list=['--test-project'], completer=FilesCompleter(), help='Existing native MSTest .csproj. Explicit relative inputs use shell CWD. Defaults to the selected project Tests/WORKFLOW/Workflow.Tests.csproj.')
        c.argument('accept_sdk_terms', options_list=['--accept-sdk-terms'], action='store_true', help='Acknowledge the Microsoft Logic Apps Tests SDK 1.0.3 use, data collection and update terms for this invocation. Does not authorize redistribution.')
        c.argument('trust_project', options_list=['--trust-project'], action='store_true', help='Acknowledge that the reviewed project, restore/build targets and test code can execute arbitrary code and contact services. Mocking and private caches are not a sandbox.')
        c.argument('restore', options_list=['--restore'], action='store_true', help='Explicitly allow native NuGet restore into project-private caches. Existing lockfiles use locked mode. Without this flag build/test use --no-restore.')
        c.argument('nuget_config', options_list=['--nuget-config'], completer=FilesCompleter(), help='Reviewed NuGet configuration used only with --restore. Explicit relative inputs use shell CWD; default NuGet.Config next to the test project. No inherited user feed/credential configuration is selected by the CLI.')
        c.argument('timeout', options_list=['--timeout'], type=int, default=300, help='Total native toolchain/restore/build/test deadline, 1-3600 seconds. Identity-checked cleanup can take additional time.')
        c.argument('report_path', options_list=['--report-path'], completer=FilesCompleter(), help='Optional new sanitized .json report; relative paths use the selected local project. Parent must exist. Existing destinations are refused. Raw local TRX is not exported.')

    with self.argument_context('logicapp test plan') as c:
        c.argument('path', arg_type=path_type, help='Existing local Standard project. Overrides the local context path; defaults to the named/active local context, then current directory. Cloud contexts cannot supply a local project.')
        c.argument('context', arg_type=target_context_type, help='Named local project context. Defaults to the active context when --path is omitted. No runtime or cloud operation is performed.')
        c.argument('workflow', arg_type=workflow_type, required=True, help='One explicit local workflow directory name.')
        c.argument('test_project', options_list=['--test-project'], completer=FilesCompleter(), help='Optional existing .csproj to inspect as XML only; otherwise inspect the default test create project when present. No MSBuild/import evaluation or test discovery.')
        c.argument('report_path', options_list=['--report-path'], completer=FilesCompleter(), help='Optional .json report. Relative paths use the selected local project; absolute paths are unchanged. Parent must exist. Default stdout only; no directories are created.')
        c.argument('force', options_list=['--force'], action='store_true', help='Replace an existing regular report only. Requires --report-path; cannot authorize SDK restore or execution.')
        c.argument('strict', options_list=['--strict'], action='store_true', help='Exit 4 for blocked execution gates after successful planning. Default exit 0 means plan generated, not tests passed; SDK execution stays blocked.')

    with self.argument_context('logicapp test results show') as c:
        c.argument('result_file', options_list=['--result-file'], required=True, completer=FilesCompleter(), help='Saved foundation preflight or sanitized test run JSON report. Raw SDK/TRX files are not accepted. Embedded paths are never followed.')
        c.argument('workflow_file', options_list=['--workflow-file'], completer=FilesCompleter(), help='Optional explicit local workflow.json for byte identity comparison. No automatic report-path traversal or rerun.')

    with self.argument_context('logicapp project create') as c:
        c.argument('path', arg_type=path_type, required=True, help='Directory to create or adopt.')
        c.argument('workflow', arg_type=workflow_type, help='Initial workflow name.')
        c.argument('workflow_kind', options_list=['--workflow-kind'], choices=['Stateful', 'Stateless'], help='Kind for initial workflow. Defaults to Stateful.')
        c.argument('adopt', options_list=['--adopt'], action='store_true', help='Allow a non-empty unrecognized directory.')
        c.argument('force', options_list=['--force'], action='store_true', help='Overwrite command-owned files.')

    with self.argument_context('logicapp context create') as c:
        c.argument('name', options_list=['--name'], required=True, help='Context name.')
        c.argument('path', arg_type=path_type, help='Local project directory.')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('logic_app_name', options_list=['--logic-app-name'], help='Deployed Logic App Standard site name.')
        c.argument('port', arg_type=port_type, default=None, help='Local runtime port. Defaults to 7071 for local contexts.')
        c.argument('use', options_list=['--use'], action='store_true', help='Make context active.')

    with self.argument_context('logicapp context use') as c:
        c.argument('name', options_list=['--name'], required=True, help='Registered context name.')

    with self.argument_context('logicapp context show') as c:
        c.argument('name', options_list=['--name'], help='Saved context name. Defaults to the active context.')

    with self.argument_context('logicapp context update') as c:
        c.argument('name', options_list=['--name'], required=True, help='Existing saved context name, not the Logic App name.')
        c.argument('kind', options_list=['--kind'], choices=['local', 'cloud'], help='Target kind. Required for a local/cloud transition, together with complete new coordinates.')
        c.argument('path', arg_type=path_type, help='New local path; need not exist yet. Omitted fields are retained.')
        c.argument('port', arg_type=port_type, help='New local port. Required with --path when switching from cloud to local.')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('logic_app_name', options_list=['--logic-app-name'], help='New deployed Logic App name. Required with --resource-group when switching to cloud.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Confirm editing the active target without prompting. Does not bypass validation or concurrent-change checks.')

    with self.argument_context('logicapp context delete') as c:
        c.argument('name', options_list=['--name'], required=True, help='Saved shortcut to delete; no project or Azure resource is deleted.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Confirm shortcut deletion without prompting. Active deletion clears selection without choosing a replacement.')

    with self.argument_context('logicapp workflow create') as c:
        c.argument('path', arg_type=path_type, help='Existing project root. Defaults to local context path or current directory.')
        c.argument('workflow', arg_type=workflow_type, required=True, help='Name of the workflow to add.')
        c.argument('kind', options_list=['--kind'], choices=['Stateful', 'Stateless'], help='Workflow kind. Defaults to Stateful, or the kind in --file.')
        c.argument('file', options_list=['--file'], completer=FilesCompleter(), help='Existing workflow.json or bare definition to use instead of the starter template.')
        c.argument('force', options_list=['--force'], action='store_true', help='Replace the workflow if it already exists. Not safe to retry without it.')
        c.argument('context', arg_type=target_context_type, help='Named local project context. Cloud contexts are refused, not replaced by another local target.')

    for command in ('list', 'show', 'export', 'set', 'delete', 'enable', 'disable'):
        with self.argument_context('logicapp workflow ' + command) as c:
            _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)
            if command == 'list':
                _pagination_args(c, 'workflows', token_help='Client-side offset token from nextContinuationToken. Inventory is read completely on each call before paging.')
            else:
                c.argument('workflow', arg_type=workflow_type, required=True)
            if command == 'export':
                c.argument('output_path', options_list=['--output-path'], required=True, completer=FilesCompleter(), help='Destination .json file for one workflow. Not a full app export. Definitions can contain authored secrets.')
                c.argument('force', options_list=['--force'], action='store_true', help='Atomically replace an existing regular output file.')
            if command in ('set', 'delete'):
                c.argument('if_match', options_list=['--if-match'], help='Exact ETag from workflow show/export. Refuse a stale edit. Wildcards and weak ETags are rejected; ETags are always checked even when omitted.')
                c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Do not prompt for confirmation. Does not bypass revision checks or non-atomic acknowledgement.')
                c.argument('allow_non_atomic', options_list=['--allow-non-atomic'], action='store_true', help='Required acknowledgement that VFS mutations are not transactional and cannot guarantee rollback or prevent every race.')
            if command == 'set':
                c.argument('file', options_list=['--file'], required=True, completer=FilesCompleter(), help='Complete authored workflow.json replacing the existing workflow, with the same Stateful/Stateless kind. Not a bare definition or partial patch.')
            if command in ('enable', 'disable'):
                c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Do not prompt for confirmation. Does not bypass snapshot checks or non-atomic acknowledgement.')
                c.argument('allow_non_atomic', options_list=['--allow-non-atomic'], action='store_true', help='Required acknowledgement that App Service replaces the complete app settings map. Concurrent unrelated changes can be lost despite preflight/readback.')

    with self.argument_context('logicapp connection create') as c:
        c.argument('path', arg_type=path_type, help='Existing project root. Defaults to local context path or current directory.')
        c.argument('name', options_list=['--name', '-n'], required=True, help='Connection name as referenced by workflows. With --managed-api this is the Logic App name instead, and the connection is named by --connection-name.')
        c.argument('connector', options_list=['--connector'], required=True, help="Service provider connector, for example 'serviceBus'.")
        c.argument('secret', options_list=['--secret'], help='App setting NAME that will hold a secret. The value is read from standard input and never from the command line. Omit for identity-based connections.')
        c.argument('secret_parameter', options_list=['--secret-parameter'], help='Parameter path the secret binds to. Defaults to connectionString.')
        c.argument('parameter', options_list=['--parameter'], nargs='+', action='append', help="Connection parameter as NAME=VALUE, repeatable. Use dots to nest, for example authProvider.Type=ManagedServiceIdentity. Values must not be secrets.")
        c.argument('app_setting', options_list=['--app-setting'], nargs='+', action='append', help='Non-secret app setting as NAME=VALUE, repeatable. Written to local.settings.json for parameters sourced from app configuration.')
        c.argument('parameter_set', options_list=['--parameter-set'], help='Connector parameter set name. Defaults to connectionString.')
        c.argument('force', options_list=['--force'], action='store_true', help='Replace an existing connection or app setting.')
        c.argument('no_gitignore', options_list=['--no-gitignore'], action='store_true', help='Do not add local.settings.json to .gitignore.')
        c.argument('context', arg_type=target_context_type, help='Named local project context. Cloud contexts are refused; unavailable in legacy --managed-api mode.')
        c.argument('managed_api', options_list=['--managed-api'], action='store_true', help='Deprecated compatibility mode. Prefer connection managed create --name CONNECTION --logic-app-name APP. Legacy --name still means the app.')
        c.argument('resource_group_name', arg_type=resource_group_name_type, help='Resource group of the Logic App. Required with --managed-api.')
        c.argument('connection_name', options_list=['--connection-name'], help='Name of the managed API connection to create. Required with --managed-api.')
        c.argument('location', options_list=['--location', '-l'], help='Azure location for the connection and its managed API. Required with --managed-api.')
        c.argument('auth_mode', options_list=['--auth-mode'], choices=list(MANAGED_AUTH_MODES), help='Authentication the connection uses. oauth opens a browser for consent. Required with --managed-api.')
        c.argument('display_name', options_list=['--display-name'], help='Display name for the connection. Defaults to --connection-name.')
        c.argument('user_assigned_identity', options_list=['--user-assigned-identity'], help='Resource id of a user-assigned identity already assigned to the app. Defaults to the system-assigned identity.')
        c.argument('no_browser', options_list=['--no-browser'], action='store_true', arg_group='OAuth consent', help='Print the consent URL instead of launching a browser. The command still listens for the redirect, so the browser must be able to reach this machine on loopback. Only with --auth-mode oauth.')
        c.argument('consent_timeout', options_list=['--consent-timeout'], type=int, arg_group='OAuth consent', help='Seconds to wait for browser consent before failing. Default 300. Connection/access-policy resources may be retained; inspect them before retrying. Only with --auth-mode oauth.')

    with self.argument_context('logicapp connection managed create') as c:
        c.argument('name', options_list=['--name', '-n'], required=True, help='Managed API connection name.')
        c.argument('logic_app_name', options_list=['--logic-app-name'], help='Deployed Logic App Standard site. Alternatively select a local --path or local/cloud --context.')
        c.argument('path', arg_type=path_type, help='Existing local project to wire. Azure scope comes from command overrides or local.settings.json, not context metadata.')
        c.argument('context', arg_type=target_context_type, help='Saved local project or deployed app. Defaults to the active context when no explicit target is supplied.')
        c.argument('resource_group_name', arg_type=resource_group_name_type, help='Azure resource group for the connection. Required for a deployed target; overrides local WORKFLOWS_RESOURCE_GROUP_NAME.')
        c.argument('connector', options_list=['--connector'], required=True, help='Managed API connector name or ARM managedApis id.')
        c.argument('location', options_list=['--location', '-l'], help='Azure connection location. Required for a deployed target; overrides local WORKFLOWS_LOCATION_NAME.')
        c.argument('auth_mode', options_list=['--auth-mode'], required=True, choices=list(MANAGED_AUTH_MODES), help='Connector backend authentication. Local projects support raw, service-principal or oauth; runtime-to-connection authentication uses a separate development key.')
        c.argument('display_name', options_list=['--display-name'], help='Display name. Defaults to --name.')
        c.argument('parameter', options_list=['--parameter'], nargs='+', action='append', help='Non-secret NAME=VALUE connection parameter, repeatable.')
        c.argument('secret_parameter', options_list=['--secret-parameter'], help='Secret parameter name. The value is read from standard input, never the command line.')
        c.argument('parameter_set', options_list=['--parameter-set'], help='Connector parameter set name.')
        c.argument('user_assigned_identity', options_list=['--user-assigned-identity'], help='Resource id of an identity already assigned to the app. Defaults to the system identity.')
        c.argument('no_browser', options_list=['--no-browser'], action='store_true', help='Print the OAuth consent URL instead of opening a browser. Loopback callback still required.')
        c.argument('consent_timeout', options_list=['--consent-timeout'], type=int, help='OAuth consent timeout in seconds, default 300. On failure resources may be retained; inspect before retrying.')
        c.argument('force', options_list=['--force'], action='store_true', help='Replace existing managed connection wiring with revision and ownership checks.')

    with self.argument_context('logicapp connection acl list') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Resource group containing the connection.')
        c.argument('connection', options_list=['--connection'], required=True, help='Managed API connection name.')

    with self.argument_context('logicapp connection acl show') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Resource group containing the connection.')
        c.argument('connection', options_list=['--connection'], required=True, help='Managed API connection name.')
        c.argument('policy', options_list=['--policy'], required=True, help='Access policy name.')

    with self.argument_context('logicapp connection acl add') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Resource group containing the connection.')
        c.argument('connection', options_list=['--connection'], required=True, help='Managed API connection name. Must be a V2 connection; V1 connections cannot accept access policies.')
        c.argument('object_id', options_list=['--object-id'], required=True, help='Entra object id (principal id) of the identity being granted access.')
        c.argument('tenant_id', options_list=['--tenant-id'], help='Tenant of the principal. Defaults to the signed-in tenant.')
        c.argument('policy', options_list=['--policy'], help='Access policy name. Defaults to the object id.')
        c.argument('location', options_list=['--location', '-l'], help='Access policy location. Defaults to the connection location.')

    with self.argument_context('logicapp connection acl remove') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Resource group containing the connection.')
        c.argument('connection', options_list=['--connection'], required=True, help='Managed API connection name.')
        c.argument('policy', options_list=['--policy'], required=True, help='Access policy name to remove.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Do not prompt for confirmation.')

    with self.argument_context('logicapp connection list') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Name of resource group containing the Logic App Standard site.')
        c.argument('name', arg_type=app_name_type, required=True)
        _pagination_args(c, 'connections')
        c.argument('show_runtime_urls', options_list=['--show-runtime-urls'], action='store_true', help='Show connection runtime URLs. Default redacts them.')

    with self.argument_context('logicapp connection show') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Name of resource group containing the Logic App Standard site.')
        c.argument('name', arg_type=app_name_type, required=True)
        c.argument('connection', options_list=['--connection'], required=True, help='Connection name in connections.json.')
        c.argument('connection_class', options_list=['--class'], choices=['serviceProviderConnections', 'managedApiConnections'], help='Connection class to search.')
        c.argument('show_runtime_urls', options_list=['--show-runtime-urls'], action='store_true', help='Show connection runtime URLs. Default redacts them.')

    with self.argument_context('logicapp connection test') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Name of resource group containing the Logic App Standard site.')
        c.argument('name', arg_type=app_name_type, required=True)
        c.argument('connection', options_list=['--connection'], required=True, help='Connection name or ARM Microsoft.Web/connections id.')
        c.argument('connection_class', options_list=['--class'], choices=['serviceProviderConnections', 'managedApiConnections'], help='Connection class to search when --connection is a name.')

    with self.argument_context('logicapp connection delete') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Name of resource group containing the Logic App Standard site.')
        c.argument('name', arg_type=app_name_type, required=True)
        c.argument('connection', options_list=['--connection'], required=True, help='Connection name in connections.json.')
        c.argument('connection_class', options_list=['--class'], choices=['serviceProviderConnections', 'managedApiConnections'], help='Connection class to search. Required only when the same name exists in both classes.')
        c.argument('keep_resource', options_list=['--keep-resource'], action='store_true', help='Keep the ARM connection resource. Remove only access policies exclusively owned by this app; shared user-assigned identity policies are retained. Managed API connections only.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Do not prompt for confirmation.')

    with self.argument_context('logicapp workflow validate') as c:
        c.argument('path', arg_type=path_type, help='Project root. Defaults to local context path or current directory.')
        c.argument('workflow', arg_type=workflow_type, help='Validate one workflow.')
        c.argument('all', options_list=['--all'], action='store_true', help='Validate every workflow.')
        c.argument('with_runtime', options_list=['--with-runtime'], action='store_true', help='Also run runtime-backed validation.')
        c.argument('fail_on_warning', options_list=['--fail-on-warning'], action='store_true', help='Warnings cause a non-zero exit.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp deployment package') as c:
        c.argument('path', arg_type=path_type, help='Project root.')
        c.argument('output_path', options_list=['--output-path'], required=True, completer=FilesCompleter(), help='Destination zip path.')
        c.argument('manifest', options_list=['--manifest'], completer=FilesCompleter(), help='Manifest path.')
        c.argument('force', options_list=['--force'], action='store_true', help='Overwrite archive and manifest.')

    with self.argument_context('logicapp dependency check') as c:
        c.argument('kind', options_list=['--kind'], action='append', choices=['core-tools', 'node', 'dotnet', 'azurite', 'bundle'], help='Limit dependencies checked. Repeat for multiple kinds.')
        c.argument('path', arg_type=path_type, help='Project root whose local.settings.json decides whether Azurite is required. Defaults to the active context.')
        c.argument('context', arg_type=target_context_type)

    with self.argument_context('logicapp dependency install') as c:
        c.argument('kind', options_list=['--kind'], action='append', choices=['core-tools', 'node', 'dotnet', 'azurite', 'bundle'], help='Limit dependencies installed. Repeat for multiple kinds. Defaults to all installable kinds. dotnet is accepted but refused with guidance.')
        c.argument('version', options_list=['--version'], help='Install a specific version instead of the latest published. Requires exactly one --kind.')
        c.argument('target_dir', options_list=['--target-dir'], help='Directory to install into. Defaults to LA_DEPENDENCIES_PATH, or ~/.azurelogicapps/dependencies.')
        c.argument('source_url', options_list=['--source-url'], help='Download the archive from this URL instead of the publisher default, or for azurite, the npm registry to install from instead of registry.npmjs.org. Requires exactly one --kind. Publisher checksums are not verified for a custom source.')
        c.argument('gh_token', options_list=['--gh-token'], help='GitHub token used when resolving the latest Functions Core Tools release, to survive anonymous rate limits.')
        c.argument('force', options_list=['--force'], action='store_true', help='Reinstall even when the requested version is already present and intact.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Do not prompt for confirmation.')

    with self.argument_context('logicapp dependency uninstall') as c:
        c.argument('kind', options_list=['--kind'], action='append', choices=['core-tools', 'node', 'dotnet', 'azurite', 'bundle'], help='Limit dependencies removed. Repeat for multiple kinds. Defaults to all installable kinds. dotnet is accepted but refused with guidance.')
        c.argument('target_dir', options_list=['--target-dir'], help='Directory to remove from. Defaults to LA_DEPENDENCIES_PATH, or ~/.azurelogicapps/dependencies.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Do not prompt for confirmation.')

    with self.argument_context('logicapp connector list') as c:
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)
        c.argument('workflow_kind', options_list=['--workflow-kind'], choices=['Stateful', 'Stateless'], help='Filter by workflow kind if supported.')
        _pagination_args(c, 'connectors')

    with self.argument_context('logicapp connector show') as c:
        c.argument('connector', options_list=['--connector'], required=True, help='Connector id or name.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp connector operation list') as c:
        c.argument('connector', options_list=['--connector'], required=True, help='Connector id or name.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)
        c.argument('kind', options_list=['--kind'], choices=['action', 'trigger', 'all'], help='Filter operations by kind. Defaults to all.')
        c.argument('search', options_list=['--search'], help='Client-side text filter over operation name, id, summary and description.')
        _pagination_args(c, 'operations')

    with self.argument_context('logicapp connector operation show') as c:
        c.argument('connector', options_list=['--connector'], required=True, help='Connector id or name.')
        c.argument('operation', options_list=['--operation'], required=True, help='Operation id or name.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp connector managed list') as c:
        c.argument('location', options_list=['--location', '-l'], required=True, help='Azure location whose managed connector catalog is queried.')
        c.argument('search', options_list=['--search', '--query-text'], help='Client-side text filter over connector name and display metadata.')
        _pagination_args(c, 'connectors')

    with self.argument_context('logicapp connector managed show') as c:
        c.argument('location', options_list=['--location', '-l'], help='Azure location. Required when --connector is a name.')
        c.argument('connector', options_list=['--connector'], required=True, help='Managed API name or ARM managedApis id.')

    with self.argument_context('logicapp connector managed operation list') as c:
        c.argument('connector', options_list=['--connector'], required=True, help='Managed API name or ARM managedApis id.')
        c.argument('location', options_list=['--location', '-l'], help='Azure location. Required when --connector is a name.')
        c.argument('kind', options_list=['--kind'], choices=['action', 'trigger', 'all'], help='Filter operations by kind. Defaults to all.')
        c.argument('search', options_list=['--search'], help='Client-side text filter over operation name and display metadata.')
        _pagination_args(c, 'operations')

    with self.argument_context('logicapp connector managed operation show') as c:
        c.argument('connector', options_list=['--connector'], required=True, help='Managed API name or ARM managedApis id.')
        c.argument('operation', options_list=['--operation'], required=True, help='Operation name or id.')
        c.argument('location', options_list=['--location', '-l'], help='Azure location. Required when --connector is a name.')

    with self.argument_context('logicapp runtime doctor') as c:
        c.argument('path', arg_type=path_type, help='Local project root. Defaults to active local context or current directory.')
        c.argument('context', arg_type=target_context_type, help='Named local context. Cannot combine with --path or --port.')
        c.argument('port', arg_type=port_type, default=None, help='Local host port. Defaults to saved context port or 7071.')
        c.argument('probe_timeout', options_list=['--probe-timeout'], type=int, default=2, help='Per-probe timeout in seconds, 1 to 10. No downloads or service starts.')
        c.argument('strict', options_list=['--strict'], action='store_true', help='Also exit 2 for optional failed, warning or unknown checks.')

    with self.argument_context('logicapp runtime start') as c:
        c.argument('path', arg_type=path_type, help='Project root to run.')
        c.argument('port', arg_type=port_type, default=None, help='Listener port. Defaults to the saved local context port, otherwise 7071.')
        c.argument('background', options_list=['--background'], action='store_true', help='Detach and record process identity for stop.')
        c.argument('ready_timeout', options_list=['--ready-timeout'], type=int, default=30, help='Seconds to wait for the management endpoint to answer when running in the background. 0 returns immediately without waiting.')
        c.argument('no_azurite', options_list=['--no-azurite'], action='store_true', help='Do not start the Azurite storage emulator. By default it is started when the project uses development storage and nothing is already serving on port 10000.')

    with self.argument_context('logicapp runtime show') as c:
        c.argument('port', arg_type=port_type, default=None, help='Local runtime port to inspect. Defaults to the saved local context port, otherwise 7071.')

    with self.argument_context('logicapp runtime stop') as c:
        c.argument('port', arg_type=port_type, default=None, help='Stop CLI-started runtime on this port. Defaults to the saved local context port, otherwise 7071. Ignored with --all.')
        c.argument('all', options_list=['--all'], action='store_true', help='Stop all runtimes previously started by this CLI.')

    with self.argument_context('logicapp run start') as c:
        c.argument('workflow', arg_type=workflow_type, required=True)
        c.argument('trigger', arg_type=trigger_type, required=True)
        c.argument('payload_file', options_list=['--payload-file'], completer=FilesCompleter(), help='JSON payload file.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    for command in ('wait', 'cancel'):
        with self.argument_context('logicapp run ' + command) as c:
            c.argument('workflow', arg_type=workflow_type, required=True)
            c.argument('run_id', arg_type=run_id_type, required=True)
            _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)
            c.argument('timeout', options_list=['--timeout'], type=int, default=300,
                       help='Observation deadline in seconds (1-86400). Timeout never cancels a run. Defaults to 300.')
            c.argument('interval', options_list=['--interval'], type=int, default=5,
                       help='Polling interval in seconds (1-300), no greater than timeout. Defaults to 5.')
            if command != 'wait':
                c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Skip interactive confirmation.')
            if command == 'cancel':
                c.argument('wait', options_list=['--wait'], action='store_true',
                           help='Wait for observed Cancelled status, not just POST acknowledgement.')

    with self.argument_context('logicapp run resubmit') as c:
        c.argument('workflow', arg_type=workflow_type, required=True)
        c.argument('run_id', arg_type=run_id_type, required=True)
        c.argument('action', options_list=['--action'], required=True,
                   help='One executed action in the completed source run; requires runtime canResubmit=true.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true',
                   help='Skip confirmation of a new execution and potentially repeated external effects.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp trigger history resubmit') as c:
        c.argument('workflow', arg_type=workflow_type, required=True)
        c.argument('trigger', arg_type=trigger_type, required=True)
        c.argument('history_name', options_list=['--history-name'], required=True,
                   help='Exact retained fired trigger history to replay. Does not require a readable associated run.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Skip confirmation of potentially duplicated external effects.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp run show') as c:
        c.argument('workflow', arg_type=workflow_type, required=True)
        c.argument('run_id', arg_type=run_id_type, required=True)
        c.argument('show_content_urls', options_list=['--show-content-urls'], action='store_true', help='Emit SAS-bearing content-link URIs. Default redacts URI values.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp run list') as c:
        c.argument('workflow', arg_type=workflow_type, required=True)
        c.argument('status', options_list=['--status'], help='Filter by run status, for example Failed or Succeeded.')
        _pagination_args(
            c, 'runs',
            token_help='Server-side continuation token returned as nextContinuationToken by a previous run list '
                       'call; sent to the service as native $skiptoken and treated as opaque by the CLI. Do not '
                       'derive the token yourself.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp run action') as c:
        c.argument('workflow', arg_type=workflow_type, required=True)
        c.argument('run_id', arg_type=run_id_type, required=True)
        c.argument('action', options_list=['--action'], help='Name of the action inside the run, as it appears in the workflow definition.')
        c.argument('show_content_urls', options_list=['--show-content-urls'], action='store_true', help='Emit SAS-bearing content-link URIs. Default redacts URI values.')
        _target_args(c, resource_group_name_type, app_name_type, port_type, host_key_type, target_context_type)

    with self.argument_context('logicapp run action list') as c:
        _pagination_args(c, 'actions')

    with self.argument_context('logicapp run action show') as c:
        c.argument('action', options_list=['--action'], required=True, help='Name of the action inside the run, as it appears in the workflow definition.')

    with self.argument_context('logicapp run action show-content') as c:
        c.argument('action', options_list=['--action'], required=True, help='Name of the action inside the run, as it appears in the workflow definition.')
        c.argument('content', options_list=['--content'], choices=['inputs', 'outputs'], help='Which recorded payload to download. Defaults to outputs, which is where action failure detail appears.')
        c.argument('max_bytes', options_list=['--max-bytes'], type=int, help='Download at most this many bytes of the payload.')

    with self.argument_context('logicapp identity') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, required=True, help='Name of resource group containing the Logic App Standard site.')
        c.argument('name', arg_type=app_name_type, required=True)
        c.argument('system_assigned', options_list=['--system-assigned'], action='store_true', help='Apply the change to the system-assigned managed identity.')
        c.argument('user_assigned', options_list=['--user-assigned'], nargs='+', action='append', help='One or more full resource ids of user-assigned managed identities. Repeatable.')


def _pagination_args(c, noun, token_help=None):
    """The one pagination surface every paged command uses.

    ``--next-token`` is primary with ``--continuation-token`` as an alias, matching the
    core ``logicapp`` commands. Before this was centralised the extension shipped three
    different spellings across seven commands while every response came back keyed
    ``nextContinuationToken``, so a token copied from one command was rejected by another.
    """
    c.argument('max_items', options_list=['--max-items'], type=int, arg_group='Pagination',
               help='Maximum number of {} to return in this page.'.format(noun))
    c.argument('next_token', options_list=['--next-token', '--continuation-token'], arg_group='Pagination',
               help=token_help or 'Token returned as nextContinuationToken by a previous call, to fetch the next page.')


def _target_args(c, rg_name_type, app_name_type, port_type, host_key_type, target_context_type):
    c.argument('resource_group_name', arg_type=rg_name_type, help='Name of resource group containing the Logic App Standard site.')
    c.argument('name', arg_type=app_name_type)
    c.argument('local', options_list=['--local'], action='store_true', help='Target a local Logic Apps runtime instead of a deployed app.')
    c.argument('port', arg_type=port_type, default=None, help='Local runtime port. Requires --local when supplied on the command line.')
    c.argument('host_key', arg_type=host_key_type)
    c.argument('context', arg_type=target_context_type)
