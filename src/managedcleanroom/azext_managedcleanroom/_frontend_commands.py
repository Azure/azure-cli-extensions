# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Command registration for Analytics Frontend API"""

from azure.cli.core.commands import CliCommandType


def load_frontend_command_table(loader, _):
    """Register all Analytics Frontend API commands

    Registers 26 commands across command groups for frontend collaboration.

    :param loader: Command loader instance
    """

    frontend_custom = CliCommandType(
        operations_tmpl='azext_managedcleanroom._frontend_custom#{}')

    # Base collaboration commands (only list - no --collaboration-id needed)
    with loader.command_group('managedcleanroom frontend collaboration', custom_command_type=frontend_custom) as g:
        g.custom_command('list', 'frontend_collaboration_list')

    # Show command at frontend level (requires --collaboration-id)
    with loader.command_group('managedcleanroom frontend', custom_command_type=frontend_custom) as g:
        g.custom_show_command('show', 'frontend_collaboration_show')

    # Workloads commands
    with loader.command_group('managedcleanroom frontend workloads', custom_command_type=frontend_custom) as g:
        g.custom_command('list', 'frontend_collaboration_workloads_list')

    # Analytics commands
    with loader.command_group('managedcleanroom frontend analytics', custom_command_type=frontend_custom) as g:
        g.custom_show_command('show', 'frontend_collaboration_analytics_show')
        g.custom_command(
            'deploymentinfo',
            'frontend_collaboration_analytics_deploymentinfo')
        g.custom_command(
            'cleanroompolicy',
            'frontend_collaboration_analytics_cleanroompolicy')

    # OIDC commands
    with loader.command_group('managedcleanroom frontend oidc issuerinfo', custom_command_type=frontend_custom) as g:
        g.custom_show_command(
            'show', 'frontend_collaboration_oidc_issuerinfo_show')

    # Invitation commands
    with loader.command_group('managedcleanroom frontend invitation', custom_command_type=frontend_custom) as g:
        g.custom_command('list', 'frontend_collaboration_invitation_list')
        g.custom_show_command('show', 'frontend_collaboration_invitation_show')
        g.custom_command('accept', 'frontend_collaboration_invitation_accept')

    # Dataset commands
    with loader.command_group('managedcleanroom frontend analytics dataset', custom_command_type=frontend_custom) as g:
        g.custom_command('list', 'frontend_collaboration_dataset_list')
        g.custom_show_command('show', 'frontend_collaboration_dataset_show')
        g.custom_command('publish', 'frontend_collaboration_dataset_publish')

    # Consent commands
    with loader.command_group('managedcleanroom frontend consent', custom_command_type=frontend_custom) as g:
        g.custom_command('check', 'frontend_collaboration_consent_check')
        g.custom_command('set', 'frontend_collaboration_consent_set')

    # Query commands
    with loader.command_group('managedcleanroom frontend analytics query', custom_command_type=frontend_custom) as g:
        g.custom_command('list', 'frontend_collaboration_query_list')
        g.custom_show_command('show', 'frontend_collaboration_query_show')
        g.custom_command('publish', 'frontend_collaboration_query_publish')
        g.custom_command('run', 'frontend_collaboration_query_run')

    # Query vote commands
    with loader.command_group(
            'managedcleanroom frontend analytics query vote',
            custom_command_type=frontend_custom) as g:
        g.custom_command('accept', 'frontend_collaboration_query_vote_accept')
        g.custom_command('reject', 'frontend_collaboration_query_vote_reject')

    # Query run history commands
    with loader.command_group(
            'managedcleanroom frontend analytics query runhistory',
            custom_command_type=frontend_custom) as g:
        g.custom_command(
            'list', 'frontend_collaboration_query_runhistory_list')

    # Query run result commands
    with loader.command_group(
            'managedcleanroom frontend analytics query runresult',
            custom_command_type=frontend_custom) as g:
        g.custom_show_command(
            'show', 'frontend_collaboration_query_runresult_show')

    # Audit event commands
    with loader.command_group(
            'managedcleanroom frontend analytics auditevent',
            custom_command_type=frontend_custom) as g:
        g.custom_command('list', 'frontend_collaboration_audit_list')

    # Attestation commands
    with loader.command_group('managedcleanroom frontend attestation', custom_command_type=frontend_custom) as g:
        g.custom_command('cgs', 'frontend_collaboration_attestation_cgs')

    with loader.command_group(
            'managedcleanroom frontend analytics attestationreport',
            custom_command_type=frontend_custom) as g:
        g.custom_command(
            'cleanroom',
            'frontend_collaboration_attestation_cleanroom')

    # Configuration and authentication commands
    with loader.command_group('managedcleanroom frontend', custom_command_type=frontend_custom) as g:
        g.custom_command('configure', 'frontend_configure')
        g.custom_command('login', 'frontend_login')
        g.custom_command('logout', 'frontend_logout')
