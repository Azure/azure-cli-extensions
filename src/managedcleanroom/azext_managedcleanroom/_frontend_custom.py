# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=broad-exception-raised, broad-exception-caught

"""Custom command implementations for Analytics Frontend API"""

from knack.log import get_logger
from ._frontend_auth import (
    get_frontend_client,
    set_frontend_config,
    get_frontend_config,
)

logger = get_logger(__name__)


# ============================================================================
# Base Collaboration Commands
# ============================================================================


def frontend_collaboration_list(cmd, active_only=False, api_version=None):
    """List all collaborations

    :param cmd: CLI command context
    :param active_only: When true, returns only active collaborations (default: False)
    :param api_version: API version to use for this request
    :return: List of collaboration objects with collaborationId, collaborationName, userStatus
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.list_get(active_only=active_only)


def frontend_collaboration_show(
    cmd, collaboration_id, active_only=False, api_version=None
):
    """Show collaboration details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param active_only: When true, queries only active collaborations (default: False)
    :param api_version: API version to use for this request
    :return: Collaboration details
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.id_get(collaboration_id, active_only=active_only)


def frontend_collaboration_report_show(cmd, collaboration_id, api_version=None):
    """Get collaboration report (comprehensive attestation report)

    Replaces the deprecated attestation cgs and cleanroom commands.
    Returns attestation reports from CGS and consortium manager.

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param api_version: API version to use for this request
    :return: Collaboration report with cgs and consortiumManager attestation details
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.report_get(collaboration_id)


# ============================================================================
# Analytics Commands
# ============================================================================


def frontend_collaboration_analytics_show(cmd, collaboration_id, api_version=None):
    """Show analytics information for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param api_version: API version to use for this request
    :return: Analytics information
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_get(collaboration_id)


def frontend_collaboration_analytics_skr_policy(
    cmd, collaboration_id, dataset_id, api_version=None
):
    """Get SKR policy for a dataset in analytics workload

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param dataset_id: Dataset identifier
    :param api_version: API version to use for this request
    :return: SKR policy for the dataset
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_skr_policy_get(collaboration_id, dataset_id)


# ============================================================================
# OIDC Commands
# ============================================================================


def frontend_collaboration_oidc_issuerinfo_show(
    cmd, collaboration_id, api_version=None
):
    """Show OIDC issuer information

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param api_version: API version to use for this request
    :return: OIDC issuer information
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.oidc_issuer_info_get(collaboration_id)


def frontend_collaboration_oidc_set_issuer_url(
    cmd, collaboration_id, url, api_version=None
):
    """Set collaboration OIDC issuer URL

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param url: OIDC issuer URL
    :param api_version: API version to use for this request
    :return: Operation result
    """
    body = {"url": url}
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.oidc_set_issuer_url_post(collaboration_id, body=body)


def frontend_collaboration_oidc_keys_show(cmd, collaboration_id, api_version=None):
    """Get collaboration OIDC signing keys (JWKS format)

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param api_version: API version to use for this request
    :return: OIDC keys in JWKS format
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.oidc_keys_get(collaboration_id)


# ============================================================================
# Invitation Commands
# ============================================================================


def frontend_collaboration_invitation_list(
    cmd, collaboration_id, pending_only=False, api_version=None
):
    """List invitations for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param pending_only: When true, returns only pending invitations (default: False)
    :param api_version: API version to use for this request
    :return: Invitations object with array of invitation details
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.invitations_get(
        collaboration_id, pending_only=pending_only
    )


def frontend_collaboration_invitation_show(
    cmd, collaboration_id, invitation_id, api_version=None
):
    """Show invitation details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param invitation_id: Invitation identifier
    :param api_version: API version to use for this request
    :return: Invitation details
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.invitation_id_get(collaboration_id, invitation_id)


def frontend_collaboration_invitation_accept(
    cmd, collaboration_id, invitation_id, api_version=None
):
    """Accept an invitation

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param invitation_id: Invitation identifier
    :param api_version: API version to use for this request
    :return: Acceptance result
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.invitation_id_accept_post(
        collaboration_id, invitation_id
    )


# ============================================================================
# Dataset Commands
# ============================================================================


def frontend_collaboration_dataset_list(cmd, collaboration_id, api_version=None):
    """List datasets for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param api_version: API version to use for this request
    :return: List of datasets
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_datasets_list_get(collaboration_id)


def frontend_collaboration_dataset_show(
    cmd, collaboration_id, document_id, api_version=None
):
    """Show dataset details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Dataset document identifier
    :param api_version: API version to use for this request
    :return: Dataset details
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_datasets_document_id_get(
        collaboration_id, document_id
    )


# pylint: disable=too-many-locals
def frontend_collaboration_dataset_publish(
    cmd,
    collaboration_id,
    document_id,
    body=None,
    storage_account_url=None,
    container_name=None,
    storage_account_type=None,
    encryption_mode=None,
    schema_file=None,
    schema_format=None,
    access_mode=None,
    allowed_fields=None,
    identity_name=None,
    identity_client_id=None,
    identity_tenant_id=None,
    identity_issuer_url=None,
    dek_keyvault_url=None,
    dek_secret_id=None,
    kek_keyvault_url=None,
    kek_secret_id=None,
    kek_maa_url=None,
    api_version=None,
):
    """Publish a dataset

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Dataset document identifier
    :param body: Publish configuration JSON (string, dict, or @file) - legacy mode
    :param storage_account_url: Azure Storage account URL
    :param container_name: Blob container name
    :param storage_account_type: Storage account type
    :param encryption_mode: Encryption mode (SSE or CPK)
    :param schema_file: Path to schema file (@path/to/schema.json)
    :param schema_format: Schema format (default: Delta)
    :param access_mode: Access mode
    :param allowed_fields: Comma-separated allowed field names
    :param identity_name: Managed identity name
    :param identity_client_id: Client ID
    :param identity_tenant_id: Tenant ID
    :param identity_issuer_url: OIDC issuer URL
    :param dek_keyvault_url: DEK Key Vault URL (CPK mode)
    :param dek_secret_id: DEK secret ID (CPK mode)
    :param kek_keyvault_url: KEK Key Vault URL (CPK mode)
    :param kek_secret_id: KEK secret ID (CPK mode)
    :param kek_maa_url: KEK MAA URL (CPK mode)
    :param api_version: API version to use for this request
    :return: Publish result
    """
    import json
    from azure.cli.core.util import CLIError

    # Check for mutual exclusion: body vs parameters
    has_params = any(
        [
            storage_account_url,
            container_name,
            storage_account_type,
            encryption_mode,
            schema_file,
            access_mode,
            identity_name,
            identity_client_id,
            identity_tenant_id,
            identity_issuer_url,
        ]
    )

    if body and has_params:
        raise CLIError(
            "Cannot use --body together with individual parameters. "
            "Use either --body or the parameter flags."
        )

    # Legacy mode: use body directly
    if body:
        if isinstance(body, str):
            body = json.loads(body)
        client = get_frontend_client(cmd, api_version=api_version)
        return client.collaboration.analytics_datasets_document_id_publish_post(
            collaboration_id, document_id, body
        )

    # Parameter mode: construct body from parameters
    if not has_params:
        raise CLIError(
            "Either --body or individual parameters (--storage-account-url, "
            "--container-name, etc.) must be provided."
        )

    # Validate required parameters
    required_params = {
        "storage_account_url": storage_account_url,
        "container_name": container_name,
        "storage_account_type": storage_account_type,
        "encryption_mode": encryption_mode,
        "schema_file": schema_file,
        "access_mode": access_mode,
        "identity_name": identity_name,
        "identity_client_id": identity_client_id,
        "identity_tenant_id": identity_tenant_id,
        "identity_issuer_url": identity_issuer_url,
    }

    missing = [k for k, v in required_params.items() if v is None]
    if missing:
        missing_params = ", ".join(f"--{k.replace('_', '-')}" for k in missing)
        raise CLIError(f"Missing required parameters: {missing_params}")

    # Validate CPK parameters if encryption_mode is CPK
    if encryption_mode and encryption_mode.upper() == "CPK":
        cpk_params = {
            "dek_keyvault_url": dek_keyvault_url,
            "dek_secret_id": dek_secret_id,
            "kek_keyvault_url": kek_keyvault_url,
            "kek_secret_id": kek_secret_id,
            "kek_maa_url": kek_maa_url,
        }
        missing_cpk = [k for k, v in cpk_params.items() if v is None]
        if missing_cpk:
            missing_cpk_params = ", ".join(
                f"--{k.replace('_', '-')}" for k in missing_cpk
            )
            raise CLIError(f"CPK encryption mode requires: {missing_cpk_params}")

    # Load schema from file (handle Azure CLI auto-loading)
    schema_content = None

    if isinstance(schema_file, dict):
        # CLI already parsed the @file.json and loaded it as dict
        schema_content = schema_file
    elif isinstance(schema_file, str) and schema_file.startswith("@"):
        # Manual file reference (not auto-loaded)
        schema_path = schema_file[1:]
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_content = json.load(f)
        except FileNotFoundError as exc:
            raise CLIError(f"Schema file not found: {schema_path}") from exc
        except json.JSONDecodeError as e:
            raise CLIError(f"Invalid JSON in schema file: {str(e)}") from e
    elif isinstance(schema_file, str):
        # CLI auto-loaded file content as string
        try:
            schema_content = json.loads(schema_file)
        except json.JSONDecodeError as e:
            raise CLIError(f"Invalid JSON in schema content: {str(e)}") from e
    else:
        raise CLIError(
            "--schema-file must be a file path prefixed with @ (e.g., @schema.json) or valid JSON"
        )

    # Override format if provided
    if schema_format:
        schema_content["format"] = schema_format

    # Build datasetAccessPolicy
    dataset_access_policy = {"accessMode": access_mode}
    if allowed_fields:
        dataset_access_policy["allowedFields"] = [
            f.strip() for f in allowed_fields.split(",")
        ]

    # Build store configuration
    store = {
        "storageAccountUrl": storage_account_url,
        "containerName": container_name,
        "storageAccountType": storage_account_type,
        "encryptionMode": encryption_mode,
    }

    # Build identity
    identity = {
        "name": identity_name,
        "clientId": identity_client_id,
        "tenantId": identity_tenant_id,
        "issuerUrl": identity_issuer_url,
    }

    # Construct final body
    body = {
        "name": document_id,
        "datasetSchema": schema_content,
        "datasetAccessPolicy": dataset_access_policy,
        "store": store,
        "identity": identity,
    }

    # Add DEK/KEK for CPK mode
    if encryption_mode and encryption_mode.upper() == "CPK":
        body["dek"] = {"keyVaultUrl": dek_keyvault_url, "secretId": dek_secret_id}
        body["kek"] = {
            "keyVaultUrl": kek_keyvault_url,
            "secretId": kek_secret_id,
            "maaUrl": kek_maa_url,
        }

    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_datasets_document_id_publish_post(
        collaboration_id, document_id, body
    )


def frontend_collaboration_dataset_queries_list(
    cmd, collaboration_id, document_id, api_version=None
):
    """List queries that use a specific dataset

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Dataset document identifier
    :param api_version: API version to use for this request
    :return: List of query IDs using this dataset
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_datasets_document_id_queries_get(
        collaboration_id, document_id
    )


# ============================================================================
# Consent Commands
# ============================================================================


def frontend_collaboration_consent_check(
    cmd, collaboration_id, document_id, api_version=None
):
    """Check consent document status

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Consent document identifier
    :param api_version: API version to use for this request
    :return: Consent status
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.consent_document_id_get(collaboration_id, document_id)


def frontend_collaboration_consent_set(
    cmd, collaboration_id, document_id, consent_action, api_version=None
):
    """Set consent document action

    NOTE: API changed - consent action is now 'enable' or 'disable' (not accept/reject)

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Consent document identifier
    :param consent_action: Consent action ('enable' or 'disable')
    :param api_version: API version to use for this request
    :return: Action result
    """
    body = {"consentAction": consent_action}
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.consent_document_id_put(
        collaboration_id, document_id, body=body
    )


# ============================================================================
# Query Commands
# ============================================================================


def frontend_collaboration_query_list(cmd, collaboration_id, api_version=None):
    """List queries for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param api_version: API version to use for this request
    :return: List of queries
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_queries_list_get(collaboration_id)


def frontend_collaboration_query_show(
    cmd, collaboration_id, document_id, api_version=None
):
    """Show query details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param api_version: API version to use for this request
    :return: Query details
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_queries_document_id_get(
        collaboration_id, document_id
    )


# pylint: disable=too-many-locals,too-many-branches
def frontend_collaboration_query_publish(
    cmd,
    collaboration_id,
    document_id,
    body=None,
    query_segment=None,
    execution_sequence=None,
    input_datasets=None,
    output_dataset=None,
    api_version=None,
):
    """Publish a query

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param body: Publish configuration JSON (string, dict, or @file) - legacy mode
    :param query_segment: List of query segments (repeatable, @file.sql or inline SQL)
    :param execution_sequence: Comma-separated execution sequence numbers
    :param input_datasets: Comma-separated input datasets (datasetId:viewName pairs)
    :param output_dataset: Output dataset (datasetId:viewName)
    :param api_version: API version to use for this request
    :return: Publish result
    """
    import json
    from azure.cli.core.util import CLIError

    # Check for mutual exclusion: body vs parameters
    has_params = any(
        [query_segment, execution_sequence, input_datasets, output_dataset]
    )

    if body and has_params:
        raise CLIError(
            "Cannot use --body together with individual parameters. "
            "Use either --body or the parameter flags."
        )

    # Legacy mode: use body directly
    if body:
        if isinstance(body, str):
            body = json.loads(body)
        client = get_frontend_client(cmd, api_version=api_version)
        return client.collaboration.analytics_queries_document_id_publish_post(
            collaboration_id, document_id, body
        )

    # Parameter mode: construct body from parameters
    if not has_params:
        raise CLIError(
            "Either --body or individual parameters (--query-segment, "
            "--execution-sequence, etc.) must be provided."
        )

    # Validate required parameters
    if not query_segment:
        raise CLIError("--query-segment is required (can be specified multiple times)")
    if not input_datasets:
        raise CLIError("--input-datasets is required")
    if not output_dataset:
        raise CLIError("--output-dataset is required")

    # Parse query segments - detect mode (FILE/DICT vs INLINE)
    # Azure CLI auto-loads @file.json content but for action='append' params,
    # the file content arrives as a raw string (not parsed dict). We need to
    # detect JSON strings vs inline SQL.
    query_data = []
    parsed_segments = []

    for seg in query_segment:
        if isinstance(seg, dict):
            # Already parsed dict (unlikely with append but handle it)
            parsed_segments.append(seg)
        elif isinstance(seg, str) and seg.startswith("@"):
            # Manual @file reference (not auto-loaded)
            file_path = seg[1:]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    segment_obj = json.load(f)
            except FileNotFoundError as exc:
                raise CLIError(f"Query segment file not found: {file_path}") from exc
            except json.JSONDecodeError as e:
                raise CLIError(
                    f"Invalid JSON in segment file {file_path}: {str(e)}"
                ) from e
            parsed_segments.append(segment_obj)
        elif isinstance(seg, str):
            # Could be auto-loaded JSON string or inline SQL.
            # Try JSON parse first.
            seg_stripped = seg.strip()
            if seg_stripped.startswith("{"):
                try:
                    segment_obj = json.loads(seg_stripped)
                    if isinstance(segment_obj, dict) and "data" in segment_obj:
                        parsed_segments.append(segment_obj)
                        continue
                except json.JSONDecodeError:
                    pass
            # Treat as inline SQL
            parsed_segments.append(seg)
        else:
            raise CLIError(f"Unexpected segment type: {type(seg)}")

    # Now classify: structured (dict) vs inline (str)
    structured = [s for s in parsed_segments if isinstance(s, dict)]
    inline_segments = [s for s in parsed_segments if isinstance(s, str)]

    # Cannot mix structured and inline segments
    if structured and inline_segments:
        raise CLIError(
            "Cannot mix @file.json / JSON-dict and inline SQL segments. "
            "Either use all structured segments or all inline SQL strings."
        )

    if structured:
        # STRUCTURED mode: segments are dicts with full object structure
        if execution_sequence:
            raise CLIError(
                "--execution-sequence must not be provided when using "
                "@file.json segments. Include executionSequence inside "
                "each JSON file."
            )

        for segment_obj in structured:
            # Validate required fields
            if "data" not in segment_obj:
                raise CLIError('Segment must contain "data" field')
            if "executionSequence" not in segment_obj:
                raise CLIError('Segment must contain "executionSequence" field')

            query_data.append(
                {
                    "data": segment_obj["data"],
                    "executionSequence": segment_obj["executionSequence"],
                    "preConditions": segment_obj.get("preConditions", ""),
                    "postFilters": segment_obj.get("postFilters", ""),
                }
            )

    else:
        # INLINE mode: segments are raw SQL strings
        if not execution_sequence:
            raise CLIError(
                "--execution-sequence is required when using inline SQL segments."
            )

        # Parse execution sequence
        try:
            exec_seq = [int(x.strip()) for x in execution_sequence.split(",")]
        except ValueError as exc:
            raise CLIError(
                '--execution-sequence must be comma-separated integers (e.g., "1,1,2")'
            ) from exc

        # Validate segment count matches execution sequence count
        if len(inline_segments) != len(exec_seq):
            raise CLIError(
                f"Number of query segments ({len(inline_segments)}) must "
                f"match execution sequence count ({len(exec_seq)})"
            )

        # Build queryData array from inline SQL
        for sql, seq in zip(inline_segments, exec_seq):
            query_data.append(
                {
                    "data": sql,
                    "executionSequence": seq,
                    "preConditions": "",
                    "postFilters": "",
                }
            )

    # Parse input datasets (comma-separated datasetId:viewName pairs)
    input_ds_list = []
    for ds in input_datasets.split(","):
        ds = ds.strip()
        if ":" not in ds:
            raise CLIError(
                f"Invalid input dataset format: {ds}. "
                f"Expected format: datasetId:viewName"
            )
        dataset_id, view_name = ds.split(":", 1)
        input_ds_list.append(f"{dataset_id.strip()}:{view_name.strip()}")
    input_ds_str = ",".join(input_ds_list)

    # Parse output dataset
    if ":" not in output_dataset:
        raise CLIError(
            f"Invalid output dataset format: {output_dataset}. "
            f"Expected format: datasetId:viewName"
        )

    # Construct body
    body = {
        "inputDatasets": input_ds_str,
        "outputDataset": output_dataset,
        "queryData": query_data,
    }

    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_queries_document_id_publish_post(
        collaboration_id, document_id, body
    )


def frontend_collaboration_query_run(
    cmd,
    collaboration_id,
    document_id,
    body=None,
    dry_run=False,
    start_date=None,
    end_date=None,
    use_optimizer=False,
    api_version=None,
):
    """Run a query

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param body: Run configuration JSON (string, dict, or @file). Optional fields:
                 runId (auto-generated if not provided), dryRun, startDate, endDate, useOptimizer
    :param dry_run: Perform a dry run without executing the query
    :param start_date: Start date for query execution
    :param end_date: End date for query execution
    :param use_optimizer: Use query optimizer
    :param api_version: API version to use for this request
    :return: Run result
    """
    import json
    import uuid
    from azure.cli.core.util import CLIError

    # Check for mutual exclusion: body vs parameters
    has_params = any([dry_run, start_date, end_date, use_optimizer])

    if body and has_params:
        raise CLIError(
            "Cannot use --body together with individual parameters. "
            "Use either --body or the parameter flags."
        )

    # Handle body parameter - convert string to dict if needed
    if body and isinstance(body, str):
        body = json.loads(body)

    # Initialize body if not provided
    if not body:
        body = {}

    # Add parameter values to body if in parameter mode
    if has_params:
        if dry_run:
            body["dryRun"] = True
        if start_date:
            body["startDate"] = start_date
        if end_date:
            body["endDate"] = end_date
        if use_optimizer:
            body["useOptimizer"] = True

    # Auto-generate runId if not provided
    if "runId" not in body:
        body["runId"] = str(uuid.uuid4())

    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_queries_document_id_run_post(
        collaboration_id, document_id, body=body
    )


def frontend_collaboration_query_vote(
    cmd, collaboration_id, document_id, vote_action, proposal_id=None, api_version=None
):
    """Vote on a query (unified accept/reject endpoint)

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param vote_action: Vote action ('accept' or 'reject')
    :param proposal_id: Optional proposal ID
    :param api_version: API version to use for this request
    :return: Vote result (None on success - 204 No Content)
    """
    body = {"voteAction": vote_action}

    if proposal_id:
        body["proposalId"] = proposal_id

    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_queries_document_id_vote_post(
        collaboration_id, document_id, body=body
    )


# ============================================================================
# Query Run History Commands
# ============================================================================


def frontend_collaboration_query_runhistory_list(
    cmd, collaboration_id, document_id, api_version=None
):
    """List query run history

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param document_id: Query document identifier
    :param api_version: API version to use for this request
    :return: List of query runs
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_queries_document_id_runs_get(
        collaboration_id, document_id
    )


def frontend_collaboration_query_runresult_show(
    cmd, collaboration_id, job_id, api_version=None
):
    """Show query job result details

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param job_id: Query job identifier
    :param api_version: API version to use for this request
    :return: Query job result details
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_runs_job_id_get(collaboration_id, job_id)


# ============================================================================
# Audit Commands
# ============================================================================


def frontend_collaboration_audit_list(
    cmd, collaboration_id, scope=None, from_seqno=None, to_seqno=None, api_version=None
):
    """List audit events for a collaboration

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param scope: Optional scope filter
    :param from_seqno: Optional starting sequence number
    :param to_seqno: Optional ending sequence number
    :param api_version: API version to use for this request
    :return: Paginated audit events with nextLink and value array
    """
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_auditevents_get(
        collaboration_id, scope=scope, from_seqno=from_seqno, to_seqno=to_seqno
    )


def frontend_collaboration_analytics_secret_set(
    cmd, collaboration_id, secret_name, secret_value, api_version=None
):
    """Set secret for analytics workload

    :param cmd: CLI command context
    :param collaboration_id: Collaboration identifier
    :param secret_name: Secret name
    :param secret_value: Secret value
    :param api_version: API version to use for this request
    :return: Operation result
    """
    body = {"secretValue": secret_value}
    client = get_frontend_client(cmd, api_version=api_version)
    return client.collaboration.analytics_secrets_secret_name_put(
        collaboration_id, secret_name, body=body
    )


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
            "status": "success",
            "message": "Login successful. Token cached for future use.",
            "authentication_method": "MSAL device code flow",
            "user": {"name": name, "email": email, "oid": oid},
        }
    except Exception as ex:
        raise CLIError(f"Login failed: {str(ex)}") from ex


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
            "status": "success",
            "message": "Logged out successfully. MSAL token cache cleared.",
            "note": "Azure CLI authentication (az login) is not affected.",
        }
    except Exception as ex:
        raise CLIError(f"Logout failed: {str(ex)}") from ex


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
        return {"status": "success", "endpoint": endpoint}

    if auth_scope:
        cmd.cli_ctx.config.set_value(
            "managedcleanroom-frontend", "auth_scope", auth_scope
        )
        return {"status": "success", "auth_scope": auth_scope}

    config_endpoint = get_frontend_config(cmd)
    # Get effective auth_scope (env var takes priority over config)
    from ._msal_auth import get_auth_scope

    config_auth_scope = get_auth_scope(cmd)

    auth_method = None
    logged_in = False
    user_info = None

    msal_token = get_msal_token(cmd)
    if msal_token:
        auth_method = "MSAL device code flow"
        logged_in = True

        try:
            import base64
            import json

            token_parts = msal_token[0].split(".")
            if len(token_parts) >= 2:
                payload = token_parts[1]
                payload += "=" * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload)
                claims = json.loads(decoded)
                user_info = (
                    claims.get("preferred_username")
                    or claims.get("upn")
                    or claims.get("email")
                    or "MSAL User"
                )
            else:
                user_info = "MSAL User"
        except Exception:
            user_info = "MSAL User"

        msal_config = get_msal_config(cmd)

        return {
            "endpoint": config_endpoint,
            "auth_scope": config_auth_scope,
            "authentication_method": auth_method,
            "logged_in": logged_in,
            "user": user_info,
            "msal_config": {
                "client_id": msal_config["client_id"],
                "tenant_id": msal_config["tenant_id"],
                "scopes": msal_config["scopes"],
                "cache_dir": str(get_msal_cache_file().parent),
            },
        }

    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        account = profile.get_subscription()
        auth_method = "Azure CLI (az login)"
        logged_in = True
        user_info = account["user"]["name"]
    except Exception:
        auth_method = "None"
        logged_in = False
        user_info = None

    return {
        "endpoint": config_endpoint,
        "auth_scope": config_auth_scope,
        "authentication_method": auth_method,
        "logged_in": logged_in,
        "user": user_info,
    }
