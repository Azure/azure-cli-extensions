# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=broad-exception-raised, broad-exception-caught

"""Custom command implementations for Analytics Frontend API"""

from knack.log import get_logger
from ._frontend_auth import get_frontend_client, set_frontend_config, get_frontend_config

logger = get_logger(__name__)


# ============================================================================
# Base Collaboration Commands
# ============================================================================

def frontend_collaboration_list(cmd):
    """List all collaborations

    :param cmd: CLI command context
    :return: List of collaboration IDs
    """
    client = get_frontend_client(cmd)
    return client.collaboration.list()


def frontend_collaboration_show(cmd, collaboration_id):
    """Show collaboration details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: Collaboration details
    """
    client = get_frontend_client(cmd)
    return client.collaboration.id_get(collaboration_id)


# ============================================================================
# Workloads Commands
# ============================================================================

def frontend_collaboration_workloads_list(cmd, collaboration_id):
    """List workloads for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: List of workloads
    """
    client = get_frontend_client(cmd)
    return client.collaboration.workloads_get(collaboration_id)


# ============================================================================
# Analytics Commands
# ============================================================================

def frontend_collaboration_analytics_show(cmd, collaboration_id):
    """Show analytics information for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: Analytics information
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_get(collaboration_id)


def frontend_collaboration_analytics_deploymentinfo(cmd, collaboration_id):
    """Get deployment info for analytics workload

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: Deployment information
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_deployment_info_get(
        collaboration_id)


def frontend_collaboration_analytics_cleanroompolicy(cmd, collaboration_id):
    """Get cleanroom policy for analytics workload

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: Cleanroom policy
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_cleanroompolicy_get(
        collaboration_id)


# ============================================================================
# OIDC Commands
# ============================================================================

def frontend_collaboration_oidc_issuerinfo_show(cmd, collaboration_id):
    """Show OIDC issuer information

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: OIDC issuer information
    """
    client = get_frontend_client(cmd)
    return client.collaboration.oidc_issuer_info_get(collaboration_id)


# ============================================================================
# Invitation Commands
# ============================================================================

def frontend_collaboration_invitation_list(cmd, collaboration_id):
    """List invitations for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: List of invitations
    """
    client = get_frontend_client(cmd)
    return client.collaboration.invitations_get(collaboration_id)


def frontend_collaboration_invitation_show(
        cmd, collaboration_id, invitation_id):
    """Show invitation details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param invitation_id: Invitation identifier
    :return: Invitation details
    """
    client = get_frontend_client(cmd)
    return client.collaboration.invitation_id_get(
        collaboration_id, invitation_id)


def frontend_collaboration_invitation_accept(
        cmd, collaboration_id, invitation_id):
    """Accept an invitation

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param invitation_id: Invitation identifier
    :return: Acceptance result
    """
    client = get_frontend_client(cmd)
    return client.collaboration.invitation_id_accept_post(
        collaboration_id, invitation_id)


# ============================================================================
# Dataset Commands
# ============================================================================

def frontend_collaboration_dataset_list(cmd, collaboration_id):
    """List datasets for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: List of datasets
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_datasets_list_get(collaboration_id)


def frontend_collaboration_dataset_show(cmd, collaboration_id, document_id):
    """Show dataset details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Dataset document identifier
    :return: Dataset details
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_dataset_document_id_get(
        collaboration_id, document_id)


def frontend_collaboration_dataset_publish(
        cmd, collaboration_id, document_id, body):
    """Publish a dataset

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Dataset document identifier
    :param body: Publish configuration JSON (string, dict, or @file)
    :return: Publish result
    """
    import json

    # Handle body parameter - convert string to dict if needed
    if isinstance(body, str):
        body = json.loads(body)

    client = get_frontend_client(cmd)
    return client.collaboration.analytics_dataset_document_id_publish_post(
        collaboration_id, document_id, body)


# ============================================================================
# Consent Commands
# ============================================================================

def frontend_collaboration_consent_check(cmd, collaboration_id, document_id):
    """Check consent document status

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Consent document identifier
    :return: Consent status
    """
    client = get_frontend_client(cmd)
    return client.collaboration.check_consent_document_id_get(
        collaboration_id, document_id)


def frontend_collaboration_consent_set(
        cmd, collaboration_id, document_id, consent_action):
    """Set consent document action

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Consent document identifier
    :param consent_action: Consent action (e.g., 'enable', 'disable')
    :return: Action result
    """
    client = get_frontend_client(cmd)
    return client.collaboration.set_consent_document_id_consent_action_post(
        collaboration_id, document_id, consent_action
    )


# ============================================================================
# Query Commands
# ============================================================================

def frontend_collaboration_query_list(cmd, collaboration_id):
    """List queries for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: List of queries
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_list_get(collaboration_id)


def frontend_collaboration_query_show(cmd, collaboration_id, document_id):
    """Show query details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :return: Query details
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_document_id_get(
        collaboration_id, document_id)


def frontend_collaboration_query_publish(
        cmd, collaboration_id, document_id, body):
    """Publish a query

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param body: Publish configuration JSON (string, dict, or @file)
    :return: Publish result
    """
    import json

    # Handle body parameter - convert string to dict if needed
    if isinstance(body, str):
        body = json.loads(body)

    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_document_id_publish_post(
        collaboration_id, document_id, body)


def frontend_collaboration_query_run(
        cmd,
        collaboration_id,
        document_id,
        body=None):
    """Run a query

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param body: Run configuration JSON (string, dict, or @file). Optional fields:
                 runId (auto-generated if not provided), dryRun, startDate, endDate, useOptimizer
    :return: Run result
    """
    import json
    import uuid

    # Handle body parameter - convert string to dict if needed
    if body and isinstance(body, str):
        body = json.loads(body)

    # Initialize body if not provided
    if not body:
        body = {}

    # Auto-generate runId if not provided
    if 'runId' not in body:
        body['runId'] = str(uuid.uuid4())

    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_document_id_run_post(
        collaboration_id, document_id, body=body)


# ============================================================================
# Query Vote Commands
# ============================================================================

def frontend_collaboration_query_vote_accept(
        cmd, collaboration_id, document_id, body=None):
    """Accept query vote

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param body: Optional vote configuration JSON (string, dict, or @file)
    :return: Vote result
    """
    import json

    # Handle body parameter - convert string to dict if needed
    if body and isinstance(body, str):
        body = json.loads(body)

    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_document_id_vote_accept_post(
        collaboration_id, document_id, body=body
    )


def frontend_collaboration_query_vote_reject(
        cmd, collaboration_id, document_id, body=None):
    """Reject query vote

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param body: Optional vote configuration JSON (string, dict, or @file)
    :return: Vote result
    """
    import json

    # Handle body parameter - convert string to dict if needed
    if body and isinstance(body, str):
        body = json.loads(body)

    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_document_id_vote_reject_post(
        collaboration_id, document_id, body=body
    )


# ============================================================================
# Query Run History Commands
# ============================================================================

def frontend_collaboration_query_runhistory_list(
        cmd, collaboration_id, document_id):
    """List query run history

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :return: List of query runs
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_document_id_runhistory_get(
        collaboration_id, document_id
    )


def frontend_collaboration_query_runresult_show(
        cmd, collaboration_id, job_id):
    """Show query job result details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param job_id: Query job identifier
    :return: Query job result details
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_queries_jobid_get(
        collaboration_id, job_id)


# ============================================================================
# Audit Commands
# ============================================================================

def frontend_collaboration_audit_list(cmd, collaboration_id):
    """List audit events for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: List of audit events
    """
    client = get_frontend_client(cmd)
    return client.collaboration.analytics_auditevents_get(collaboration_id)


# ============================================================================
# Attestation Commands
# ============================================================================

def frontend_collaboration_attestation_cgs(cmd, collaboration_id):
    """Get CGS attestation report

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: CGS attestation report
    """
    client = get_frontend_client(cmd)
    return client.collaboration.attestationreport_cgs_get(collaboration_id)


def frontend_collaboration_attestation_cleanroom(cmd, collaboration_id):
    """Get cleanroom attestation report

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :return: Cleanroom attestation report
    """
    client = get_frontend_client(cmd)
    return client.collaboration.attestationreport_cleanroom_get(
        collaboration_id)


# ============================================================================
# Authentication Commands
# ============================================================================

def frontend_login(cmd, use_microsoft_identity=False):  # pylint: disable=unused-argument
    """Login using Microsoft device code flow

    Initiates interactive authentication via browser.
    Token is cached for future use.

    :param cmd: CLI command context
    :param use_microsoft_identity: Explicit flag for MSAL (optional, always True)
    :return: Login status with user information
    """
    from azure.cli.core.util import CLIError
    from ._msal_auth import perform_device_code_flow

    # Note: use_microsoft_identity flag is optional/explicit
    # The login command always uses MSAL device code flow

    try:
        result = perform_device_code_flow(cmd)

        # Extract user info from token claims
        claims = result.get("id_token_claims", {})
        name = claims.get("name", "Unknown")
        email = claims.get("preferred_username", "Unknown")
        oid = claims.get("oid", "Unknown")

        return {
            'status': 'success',
            'message': 'Login successful. Token cached for future use.',
            'authentication_method': 'MSAL device code flow',
            'user': {
                'name': name,
                'email': email,
                'oid': oid
            }
        }
    except Exception as ex:
        raise CLIError(f'Login failed: {str(ex)}')


def frontend_logout(cmd):  # pylint: disable=unused-argument
    """Logout and clear cached credentials

    Removes stored MSAL token cache.
    Note: Does not affect Azure CLI authentication (az login).

    :param cmd: CLI command context
    :return: Logout status
    """
    from azure.cli.core.util import CLIError
    from ._msal_auth import clear_msal_cache

    try:
        clear_msal_cache()
        return {
            'status': 'success',
            'message': 'Logged out successfully. MSAL token cache cleared.',
            'note': 'Azure CLI authentication (az login) is not affected.'
        }
    except Exception as ex:
        raise CLIError(f'Logout failed: {str(ex)}')


# ============================================================================
# Configuration Commands
# ============================================================================

def frontend_configure(cmd, endpoint=None, auth_scope=None):
    """Configure Analytics Frontend API settings

    Shows current configuration including authentication method and MSAL config.

    :param cmd: CLI command context
    :param endpoint: API endpoint URL (optional)
    :param auth_scope: OAuth2 resource URL (optional)
    """
    from azure.cli.core._profile import Profile
    from ._msal_auth import get_msal_token, get_msal_config, get_msal_cache_file

    if endpoint:
        set_frontend_config(cmd, endpoint)
        return {'status': 'success', 'endpoint': endpoint}

    if auth_scope:
        cmd.cli_ctx.config.set_value(
            'managedcleanroom-frontend',
            'auth_scope',
            auth_scope
        )
        return {'status': 'success', 'auth_scope': auth_scope}

    config_endpoint = get_frontend_config(cmd)
    # Get effective auth_scope (env var takes priority over config)
    from ._msal_auth import get_auth_scope
    config_auth_scope = get_auth_scope(cmd)

    auth_method = None
    logged_in = False
    user_info = None

    msal_token = get_msal_token(cmd)
    if msal_token:
        auth_method = 'MSAL device code flow'
        logged_in = True

        try:
            import base64
            import json
            token_parts = msal_token[0].split('.')
            if len(token_parts) >= 2:
                payload = token_parts[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload)
                claims = json.loads(decoded)
                user_info = claims.get('preferred_username') or claims.get(
                    'upn') or claims.get('email') or 'MSAL User'
            else:
                user_info = 'MSAL User'
        except Exception:
            user_info = 'MSAL User'

        msal_config = get_msal_config(cmd)

        return {
            'endpoint': config_endpoint,
            'auth_scope': config_auth_scope,
            'authentication_method': auth_method,
            'logged_in': logged_in,
            'user': user_info,
            'msal_config': {
                'client_id': msal_config['client_id'],
                'tenant_id': msal_config['tenant_id'],
                'scopes': msal_config['scopes'],
                'cache_dir': str(get_msal_cache_file().parent)
            }
        }

    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        account = profile.get_subscription()
        auth_method = 'Azure CLI (az login)'
        logged_in = True
        user_info = account['user']['name']
    except Exception:
        auth_method = 'None'
        logged_in = False
        user_info = None

    return {
        'endpoint': config_endpoint,
        'auth_scope': config_auth_scope,
        'authentication_method': auth_method,
        'logged_in': logged_in,
        'user': user_info
    }
