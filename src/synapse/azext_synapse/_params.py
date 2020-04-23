# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from azext_synapse.constant import SparkBatchLanguage, SparkStatementLanguage
from azure.cli.core.commands.parameters import name_type, tags_type, get_three_state_flag, get_enum_type, \
    resource_group_name_type
from azure.cli.core.util import get_json_object
from ._validators import validate_storage_account


# pylint: disable=too-many-statements
def load_arguments(self, _):
    # synapse spark
    for scope in ['batch', 'session', 'session-statement']:
        with self.argument_context('synapse spark ' + scope) as c:
            c.argument('workspace_name', help='The name of the workspace.')
            c.argument('spark_pool_name', help='The name of the spark pool.')

    for scope in ['synapse spark batch', 'synapse spark session']:
        with self.argument_context(scope + ' create') as c:
            c.argument('job_name', arg_type=name_type, help='The spark batch or session job name.')
            c.argument('reference_files', nargs='+', help='The array of files URI.')
            c.argument('configuration', type=get_json_object, help='The configuration of spark batch job.')
            c.argument('executors', help='The number of executors.')
            c.argument('executor_size', arg_type=get_enum_type(['Small', 'Medium']), help='The executor size')
            c.argument('tags', arg_type=tags_type)
            c.argument('detailed', action='store_true',
                       help='Optional query parameter specifying whether detailed response is returned beyond plain livy.')

        with self.argument_context(scope + ' list') as c:
            c.argument('from_index', help='Optional parameter specifying which index the list should begin from.')
            c.argument('detailed', action='store_true',
                       help='Optional query parameter specifying whether detailed response is returned beyond plain livy.')
            c.argument('size',
                       help='The size of the returned list.By default it is 20 and that is the maximum.')

    with self.argument_context('synapse spark batch create') as c:
        c.argument('main_definition_file', help='The URI of file.')
        c.argument('main_class_name', help='The class name.')
        c.argument('command_line_arguments', nargs='+', help='The arguments of the job.')
        c.argument('archives', nargs='+', help='The array of archives.')

    with self.argument_context('synapse spark batch create') as c:
        c.argument('language', arg_type=get_enum_type(SparkBatchLanguage, default=SparkBatchLanguage.Scala),
                   help='The spark batch job language.')

    for scope in ['show', 'cancel']:
        with self.argument_context('synapse spark batch ' + scope) as c:
            c.argument('batch_id', options_list=['--id'], arg_group='Spark Batch',
                       help='The id of the spark batch job.')

    with self.argument_context('synapse spark batch show') as c:
        c.argument('detailed', action='store_true',
                   help='Optional query parameter specifying whether detailed response is returned beyond plain livy.')

    for scope in ['show', 'cancel', 'reset-timeout']:
        with self.argument_context('synapse spark session ' + scope) as c:
            c.argument('session_id', options_list=['--id'], arg_group='Spark Session',
                       help='The id of the spark session job.')

    with self.argument_context('synapse spark session show') as c:
        c.argument('detailed', action='store_true',
                   help='Optional query parameter specifying whether detailed response is returned beyond plain livy.')

    with self.argument_context('synapse spark session-statement') as c:
        c.argument('session_id', help='The id of spark session job.')

    for scope in ['show', 'cancel']:
        with self.argument_context('synapse spark session-statement ' + scope) as c:
            c.argument('statement_id', options_list=['--id'], arg_group="Spark Session-statement",
                       help='The id of the statement.')

    with self.argument_context('synapse spark session-statement create') as c:
        c.argument('code', help='The code of spark statement.')
        c.argument('code_file', help='The file that contains the code.')
        c.argument('language', arg_type=get_enum_type(SparkStatementLanguage), help='The language of spark statement.')

    # synapse workspace
    for scope in ['synapse workspace', 'synapse spark pool', 'synapse sql pool', 'synapse workspace firewall-rule']:
        with self.argument_context(scope) as c:
            c.argument('resource_group_name', arg_type=resource_group_name_type, id_part='resource_group')

    for scope in ['show', 'create', 'update', 'delete']:
        with self.argument_context('synapse workspace ' + scope) as c:
            c.argument('workspace_name', arg_type=name_type, id_part='name', help='The workspace name.')

    for scope in ['create', 'update']:
        with self.argument_context('synapse workspace ' + scope) as c:
            c.argument('sql_admin_login_password', options_list=['--sql-admin-login-password', '-p'],
                       help='The sql administrator login password.')
            c.argument('tags', arg_type=tags_type)

    with self.argument_context('synapse workspace create') as c:
        c.argument("storage_account", validator=validate_storage_account,
                   help='The data lake storage account name or resource id.')
        c.argument('file_system', help='The file system of the data lake storage account.')
        c.argument('sql_admin_login_user', options_list=['--sql-admin-login-user', '-u'],
                   help='The sql administrator login user name.')

    with self.argument_context('synapse workspace check-name') as c:
        c.argument('name', arg_type=name_type, help='The name you wanted to check.')

    # synapse spark pool
    with self.argument_context('synapse spark pool') as c:
        c.argument('workspace_name', id_part='name', help='The workspace name.')

    with self.argument_context('synapse spark pool list') as c:
        c.argument('workspace_name', id_part=None, help='The workspace name.')

    for scope in ['show', 'create', 'update', 'delete']:
        with self.argument_context('synapse spark pool ' + scope) as c:
            c.argument('spark_pool_name', arg_type=name_type, id_part='child_name_1',
                       help='The name of the spark pool.')

    with self.argument_context('synapse spark pool create') as c:
        # Node
        c.argument('node_count', arg_group='Node', help='The number of node.')
        c.argument('node_size_family', arg_group='Node', help='The node size family.')
        c.argument('node_size', arg_group='Node', arg_type=get_enum_type(['Small', 'Medium', 'Large']),
                   help='The node size.')

        # AutoScale
        c.argument('enable_auto_scale', arg_type=get_three_state_flag(), arg_group='AutoScale',
                   help='The flag of enabling auto scale.')
        c.argument('max_node_count', arg_group='AutoScale', help='The max node count.')
        c.argument('min_node_count', arg_group='AutoScale', help='The min node count.')

        # AutoPause
        c.argument('enable_auto_pause', arg_type=get_three_state_flag(), arg_group='AutoPause',
                   help='The flag of enabling auto pause.')
        c.argument('delay_in_minutes', arg_group='AutoPause', help='The delay time.')

        # Environment Configuration
        c.argument('library_requirements_file', arg_group='Environment Configuration',
                   help='The library requirements file.')

        # Default Folder
        c.argument('spark_events_folder', arg_group='Default Folder', help='The spark events folder.')
        c.argument('default_spark_log_folder', arg_group='Default Folder', help='The default spark log folder.')

        # Component Version
        c.argument('spark_version', arg_group='Component Version', help='The supported spark version is 2.4 now.')

        c.argument('tags', arg_type=tags_type)

    with self.argument_context('synapse spark pool update') as c:
        c.argument('tags', arg_type=tags_type)
        # Node
        c.argument('node_count', arg_group='Node', help='The number of node.')
        c.argument('node_size_family', arg_group='Node', help='The node size family.')

        c.argument('node_size', arg_group='Node', arg_type=get_enum_type(['Small', 'Medium', 'Large']),
                   help='The node size.')
        # AutoScale
        c.argument('enable_auto_scale', arg_type=get_three_state_flag(), arg_group='AutoScale',
                   help='The flag of enabling auto scale.')
        c.argument('max_node_count', arg_group='AutoScale', help='The max node count.')
        c.argument('min_node_count', arg_group='AutoScale', help='The min node count.')

        # AutoPause
        c.argument('enable_auto_pause', arg_type=get_three_state_flag(), arg_group='AutoPause',
                   help='The flag of enabling auto pause.')
        c.argument('delay_in_minutes', arg_group='AutoPause', help='The delay time.')

        # Environment Configuration
        c.argument('library_requirements_file', arg_group='Environment Configuration',
                   help='The library requirements file.')
        c.argument('force', arg_type=get_three_state_flag(), help='The flag of force operation.')

    # synapse sql pool
    with self.argument_context('synapse sql pool') as c:
        c.argument('workspace_name', id_part='name', help='The workspace name.')

    with self.argument_context('synapse sql pool list') as c:
        c.argument('workspace_name', id_part=None, help='The workspace name.')

    for scope in ['show', 'create', 'delete', 'update', 'pause', 'resume']:
        with self.argument_context('synapse sql pool ' + scope) as c:
            c.argument('sql_pool_name', arg_type=name_type, id_part='child_name_1', help='The SQL pool name.')

    with self.argument_context('synapse sql pool create') as c:
        c.argument('max_size_bytes', help='The max size bytes.')
        c.argument('sku_name', options_list=['--performance-level'], help='The performance level.')
        c.argument('sku_tier', help='The sku tier.')
        c.argument('source_database_id', help='The source database id.')
        c.argument('recoverable_database_id', help='The recoverable database id.')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('synapse sql pool update') as c:
        c.argument('sku_name', options_list=['--performance-level'], help='The performance level.')
        c.argument('tags', arg_type=tags_type)

    # synapse workspace firewall-rule
    with self.argument_context('synapse workspace firewall-rule') as c:
        c.argument('workspace_name', id_part='name', help='The workspace name.')

    with self.argument_context('synapse workspace firewall-rule list') as c:
        c.argument('workspace_name', id_part=None, help='The workspace name.')

    for scope in ['show', 'create', 'delete']:
        with self.argument_context('synapse workspace firewall-rule ' + scope) as c:
            c.argument('rule_name', arg_type=name_type, id_part='child_name_1', help='The IP firewall rule name')

    with self.argument_context('synapse workspace firewall-rule create') as c:
        c.argument('start_ip_address', help='The start IP address of the firewall rule. Must be IPv4 format.')
        c.argument('end_ip_address', help='The end IP address of the firewall rule. Must be IPv4 format. '
                                          'Must be greater than or equal to startIpAddress.')
