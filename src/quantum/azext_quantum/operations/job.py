# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin,bare-except,inconsistent-return-statements,too-many-locals,too-many-branches,too-many-statements

import gzip
import io
import json
import logging
import os
import uuid
import knack.log

from azure.cli.core.azclierror import (FileOperationError, AzureInternalError,
                                       InvalidArgumentValueError, AzureResponseError,
                                       RequiredArgumentMissingError)

from ..vendored_sdks.azure_quantum_python.workspace import Workspace
from ..vendored_sdks.azure_quantum_python.storage import upload_blob
from ..vendored_sdks.azure_storage_blob import BlobClient, ContainerClient
from .._client_factory import cf_jobs
from .._list_helper import repack_response_json
from .workspace import WorkspaceInfo
from .target import TargetInfo, get_provider


MINIMUM_MAX_POLL_WAIT_SECS = 1
DEFAULT_SHOTS = 100

ERROR_MSG_MISSING_INPUT_FORMAT = "The following argument is required: --job-input-format"  # NOTE: The Azure CLI core generates a similar error message, but "the" is lowercase and "arguments" is always plural.
ERROR_MSG_MISSING_OUTPUT_FORMAT = "The following argument is required: --job-output-format"
ERROR_MSG_MISSING_ENTRY_POINT = "The following argument is required on QIR jobs: --entry-point"
JOB_SUBMIT_DOC_LINK_MSG = "See https://learn.microsoft.com/cli/azure/quantum/job?view=azure-cli-latest#az-quantum-job-submit"
ERROR_MSG_INVALID_ORDER_ARGUMENT = "The --order argument is not valid: Specify either asc or desc"
ERROR_MSG_MISSING_ORDERBY_ARGUMENT = "The --order argument is not valid without an --orderby argument"
JOB_LIST_DOC_LINK_MSG = "See https://learn.microsoft.com/cli/azure/quantum/job?view=azure-cli-latest#az-quantum-job-list"

# Job types
QIR_JOB = 1
PASS_THROUGH_JOB = 2

logger = logging.getLogger(__name__)
knack_logger = knack.log.get_logger(__name__)


def list(cmd, resource_group_name, workspace_name, location, job_type=None, item_type=None, provider_id=None,
         target_id=None, job_status=None, created_after=None, created_before=None, job_name=None,
         skip=None, top=None, orderby=None, order=None):
    """
    Get the list of jobs in a Quantum Workspace.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.location)

    query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
    orderby_expression = _construct_orderby_expression(orderby, order)

    response = client.list(info.subscription, resource_group_name, workspace_name, filter=query, skip=skip, top=top, orderby=orderby_expression)
    first_page = next(iter(response.by_page()), [])
    # Note: --top produces multi-page responses, but we only process the first page. All the other params put everything on the first page.
    return repack_response_json(first_page)


def _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name):
    """
    Construct a job-list filter query expression
    """
    query = ""

    query = _parse_pagination_param_values("JobType", query, job_type)
    query = _parse_pagination_param_values("ItemType", query, item_type)
    query = _parse_pagination_param_values("ProviderId", query, provider_id)
    query = _parse_pagination_param_values("Target", query, target_id)
    query = _parse_pagination_param_values("State", query, job_status)

    query = _parse_pagination_param_values("CreationTime", query, created_after, "ge")
    query = _parse_pagination_param_values("CreationTime", query, created_before, "le")
    query = _parse_pagination_param_values("Name", query, job_name, "startswith")

    if query == "":
        query = None
    return query


def _parse_pagination_param_values(param_name, query, raw_values, logic_operator=None):
    """
    Parse the pagination parameter values for a job-list filter query expression
    """
    if raw_values is not None:
        if len(query) > 0:
            query += " and "

        # Special handling of --job-name
        if param_name == "Name":
            query += logic_operator + "(Name, '" + raw_values + "')"
            return query

        # Special handling of --created-before and --created-after (No quotes around the date)
        if param_name == "CreationTime":
            query += "CreationTime " + logic_operator + " " + raw_values
            return query

        if logic_operator is None:
            logic_operator = "eq"
        padded_logic_operator = " " + logic_operator + " '"

        first_value = True
        values_list = raw_values.split(",")

        if len(values_list) <= 1:
            query += param_name + padded_logic_operator + values_list[0] + "'"
        else:
            for value in values_list:
                value = value.strip()

                if first_value:
                    query += "(" + param_name + padded_logic_operator + value + "'"
                    first_value = False
                else:
                    query += " or " + param_name + padded_logic_operator + value + "'"
            query += ")"
    return query


def _construct_orderby_expression(orderby, order):
    """
    Construct a job-list orderby expression
    """
    if (orderby == "" or orderby is None) and not (order == "" or order is None):
        raise RequiredArgumentMissingError(ERROR_MSG_MISSING_ORDERBY_ARGUMENT, JOB_LIST_DOC_LINK_MSG)

    orderby_expression = orderby
    if orderby_expression is not None and order is not None:
        # Validate order, otherwise the error message will be vague
        if not (order == "asc" or order == "desc"):
            raise InvalidArgumentValueError(ERROR_MSG_INVALID_ORDER_ARGUMENT, JOB_LIST_DOC_LINK_MSG)
        orderby_expression += " " + order
    return orderby_expression


def get(cmd, job_id, resource_group_name=None, workspace_name=None, location=None):
    """
    Get the job's status and details.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.get(job_id)


def _has_completed(job):
    return job.status in ("Succeeded", "Failed", "Cancelled")


def _convert_numeric_params(job_params):
    # The CLI framework passes all --job-params values as strings. This function
    # attempts to convert numeric string values to their appropriate numeric types.
    # Non-numeric string values and values that are already integers are unaffected.
    for param in job_params:
        if isinstance(job_params[param], str):
            try:
                job_params[param] = int(job_params[param])
            except:
                try:
                    job_params[param] = float(job_params[param])
                except:
                    pass


def submit(cmd, resource_group_name, workspace_name, location, target_id, job_input_file, job_input_format,
           job_name=None, shots=None, storage=None, job_params=None, target_capability=None,
           job_output_format=None, entry_point=None):
    """
    Submit QIR or a pass-through job to run on Azure Quantum.
    """
    # Get workspace, target, and provider information
    ws_info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    if ws_info is None:
        raise AzureInternalError("Failed to get workspace information.")
    target_info = TargetInfo(cmd, target_id)
    if target_info is None:
        raise AzureInternalError("Failed to get target information.")
    provider_id = get_provider(cmd, target_info.target_id, resource_group_name, workspace_name, location)
    if provider_id is None:
        raise AzureInternalError(f"Failed to find a Provider ID for the specified Target ID, {target_info.target_id}")

    # Identify the type of job being submitted
    lc_job_input_format = job_input_format.lower()
    if "qir.v" in lc_job_input_format:
        job_type = QIR_JOB
    else:
        job_type = PASS_THROUGH_JOB

    # If output format is not specified, supply a default for QIR jobs
    if job_output_format is None:
        if job_type == QIR_JOB:
            job_output_format = "microsoft.quantum-results.v1"
        else:
            raise RequiredArgumentMissingError(ERROR_MSG_MISSING_OUTPUT_FORMAT, JOB_SUBMIT_DOC_LINK_MSG)

    # Extract "metadata" and "tags" from job_params, then remove those parameters from job_params,
    # since they should not be included in the "inputParams" parameter of job_details. They are
    # separate parameters of job_details.
    #
    #   USAGE NOTE: To specify "metadata", the --job-params value needs to be entered as a JSON string or file.
    #
    metadata = None
    tags = []
    if job_params is not None:
        if "metadata" in job_params.keys():
            metadata = job_params["metadata"]
            del job_params["metadata"]
            if not isinstance(metadata, dict) and metadata is not None:
                raise InvalidArgumentValueError('The "metadata" parameter is not valid.',
                                                'To specify "metadata", use a JSON string for the --job-params value.')
        if "tags" in job_params.keys():
            tags = job_params["tags"]
            del job_params["tags"]
            if isinstance(tags, str):
                tags = tags.split(',')
            list_type = type([])    # "list" has been redefined as a function name, so "isinstance(tags, list)" doesn't work here
            if not isinstance(tags, list_type):
                raise InvalidArgumentValueError('The "tags" parameter is not valid.')

    # Extract content type and content encoding from --job-parameters, then remove those parameters from job_params, since
    # they should not be included in the "inputParams" parameter of job_details. Content type and content encoding are
    # parameters of the upload_blob function. These parameters are accepted in three case-formats: kebab-case, snake_case,
    # and camelCase. (See comments below.)
    content_type = None
    content_encoding = None
    if job_params is not None:
        if "content-type" in job_params.keys():         # Parameter names in the CLI are commonly in kebab-case (hyphenated)...
            content_type = job_params["content-type"]
            del job_params["content-type"]
        if "content_type" in job_params.keys():         # ...however names are often in in snake_case in our Jupyter notebooks...
            content_type = job_params["content_type"]
            del job_params["content_type"]
        if "contentType" in job_params.keys():          # ...but the params that go into inputParams are generally in camelCase.
            content_type = job_params["contentType"]
            del job_params["contentType"]
        if "content-encoding" in job_params.keys():
            content_encoding = job_params["content-encoding"]
            del job_params["content-encoding"]
        if "content_encoding" in job_params.keys():
            content_encoding = job_params["content_encoding"]
            del job_params["content_encoding"]
        if "contentEncoding" in job_params.keys():
            content_encoding = job_params["contentEncoding"]
            del job_params["contentEncoding"]

    # Prepare for input file upload according to job type
    if job_type == QIR_JOB:
        if content_type is None:
            if provider_id.lower() == "rigetti":
                content_type = "application/octet-stream"
            else:
                # MAINTENANCE NOTE: The following value is valid for QCI and Quantinuum.
                # Make sure it's correct for new providers when they are added. If not,
                # modify this logic.
                content_type = "application/x-qir.v1"
        content_encoding = None
    try:
        with open(job_input_file, "rb") as input_file:
            blob_data = input_file.read()
    except (IOError, OSError) as e:
        raise FileOperationError(f"An error occurred opening the input file: {job_input_file}") from e

    # Upload the input file to the workspace's storage account
    if storage is None:
        from .workspace import get as ws_get
        ws = ws_get(cmd)
        if ws.properties.storage_account is None:
            raise RequiredArgumentMissingError("No storage account specified or linked with workspace.")
        storage = ws.properties.storage_account.split('/')[-1]
    job_id = str(uuid.uuid4())
    blob_name = "inputData"

    resource_id = "/subscriptions/" + ws_info.subscription + "/resourceGroups/" + ws_info.resource_group + "/providers/Microsoft.Quantum/Workspaces/" + ws_info.name
    workspace = Workspace(resource_id=resource_id, location=location)

    knack_logger.warning("Getting Azure credential token...")
    container_uri = workspace.get_container_uri(job_id=job_id)
    container_client = ContainerClient.from_container_url(container_uri)

    knack_logger.warning("Uploading input data...")
    try:
        blob_uri = upload_blob(container_client, blob_name, content_type, content_encoding, blob_data, return_sas_token=False)
        logger.debug("  - blob uri: %s", blob_uri)
    except Exception as e:
        # Unexplained behavior:
        #    QIR input input data get UnicodeDecodeError on jobs run in tests using
        #    "azdev test --live", but the same commands are successful when run interactively.
        #    See commented-out tests in test_submit in test_quantum_jobs.py
        error_msg = f"Input file upload failed.\nError type: {type(e)}"
        if isinstance(e, UnicodeDecodeError):
            error_msg += f"\nReason: {e.reason}"
        raise AzureResponseError(error_msg) from e

    # Combine separate command-line parameters (like shots, target_capability, and entry_point) with job_params
    if job_params is None:
        job_params = {}
    if shots is not None:
        try:
            job_params["shots"] = int(shots)
        except Exception as exc:
            raise InvalidArgumentValueError("Invalid --shots value.  Shots must be an integer.") from exc
    if target_capability is not None:
        job_params["targetCapability"] = target_capability
    if entry_point is not None:
        job_params["entryPoint"] = entry_point

    # Convert "count" to an integer
    if "count" in job_params.keys():
        try:
            job_params["count"] = int(job_params["count"])
        except Exception as exc:
            raise InvalidArgumentValueError("Invalid count value.  Count must be an integer.") from exc

    # Convert all other numeric parameter values from string to int or float
    _convert_numeric_params(job_params)

    # Make sure QIR jobs have an "arguments" parameter, even if it's empty
    if job_type == QIR_JOB:
        if "arguments" not in job_params:
            job_params["arguments"] = []

    # ...supply a default "shots" if it's not specified (like Q# does)
        if "shots" not in job_params:
            job_params["shots"] = DEFAULT_SHOTS

    # Submit the job
    client = cf_jobs(cmd.cli_ctx, ws_info.subscription, ws_info.location)
    job_details = {'name': job_name,
                   'containerUri': container_uri,
                   'inputDataFormat': job_input_format,
                   'outputDataFormat': job_output_format,
                   'inputParams': job_params,
                   'providerId': provider_id,
                   'target': target_info.target_id,
                   'metadata': metadata,
                   'tags': tags}

    knack_logger.warning("Submitting job...")
    return client.create_or_replace(ws_info.subscription, ws_info.resource_group, ws_info.name, job_id, job_details).as_dict()


def output(cmd, job_id, resource_group_name, workspace_name, location):
    """
    Get the results of running a job.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.location)
    job = client.get(info.subscription, info.resource_group, info.name, job_id)

    if job.status != "Succeeded":
        return job  # If "-o table" is specified, this allows transform_output() in commands.py
        #             to format the output, so the error info is shown. If "-o json" or no "-o"
        #             parameter is specified, then the full JSON job output is displayed, being
        #             consistent with other commands.

    return _get_job_output(cmd, job)


def wait(cmd, job_id, resource_group_name, workspace_name, location, max_poll_wait_secs=5):
    """
    Place the CLI in a waiting state until the job finishes running.
    """
    import time

    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.location)

    # TODO: LROPoller...
    wait_indicators_used = False
    poll_wait = 0.2
    max_poll_wait_secs = _validate_max_poll_wait_secs(max_poll_wait_secs)
    job = client.get(info.subscription, info.resource_group, info.name, job_id)

    while not _has_completed(job):
        print('.', end='', flush=True)
        wait_indicators_used = True
        time.sleep(poll_wait)
        job = client.get(info.subscription, info.resource_group, info.name, job_id)
        poll_wait = max_poll_wait_secs if poll_wait >= max_poll_wait_secs else poll_wait * 1.5

    if wait_indicators_used:
        # Insert a new line if we had to display wait indicators.
        print()

    return job.as_dict()


def job_show(cmd, job_id, resource_group_name, workspace_name, location):
    """
    Get the job's status and details.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.location)
    job = client.get(info.subscription, info.resource_group, info.name, job_id)
    return job.as_dict()


def run(cmd, resource_group_name, workspace_name, location, target_id, job_input_file, job_input_format,
        job_name=None, shots=None, storage=None, job_params=None, target_capability=None,
        job_output_format=None, entry_point=None):
    """
    Submit a job to run on Azure Quantum, and wait for the result.
    """
    job = submit(cmd, resource_group_name, workspace_name, location, target_id, job_input_file, job_input_format,
                 job_name, shots, storage, job_params, target_capability,
                 job_output_format, entry_point)
    logger.warning("Job id: %s", job["id"])
    logger.debug(job)

    job = wait(cmd, job["id"], resource_group_name, workspace_name, location)
    logger.debug(job)

    return output(cmd, job["id"], resource_group_name, workspace_name, location)


def cancel(cmd, job_id, resource_group_name, workspace_name, location):
    """
    Request to cancel a job on Azure Quantum if it hasn't completed.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.location)
    job = client.get(info.subscription, info.resource_group, info.name, job_id)

    if _has_completed(job):
        print(f"Job {job_id} has already completed with status: {job.status}.")
        return

    # If the job hasn't succeeded or failed, attempt to cancel.
    client.delete(info.subscription, info.resource_group, info.name, job_id)  # JobOperations.cancel has been replaced with .delete in the updated DP client

    # Wait for the job status to complete or be reported as cancelled
    return wait(cmd, job_id, info.resource_group, info.name, info.location)


def _get_job_output(cmd, job):

    import tempfile
    path = os.path.join(tempfile.gettempdir(), job.id)

    if os.path.exists(path):
        logger.debug("Using existing blob from %s", path)
    else:
        logger.debug("Downloading job results blob into %s", path)

        blob_client = BlobClient.from_blob_url(job.output_data_uri)
        blobProperties = blob_client.get_blob_properties()

        if blobProperties.size == 0:
            return
        
        with open(file=path, mode="wb") as stream:
            download_stream = blob_client.download_blob()
            stream.write(download_stream.readall())

    with open(path, encoding="utf-8") as json_file:
        lines = [line.strip() for line in json_file.readlines()]

        # Receiving an empty response is valid.
        if len(lines) == 0:
            return

        json_file.seek(0)  # Reset the file pointer before loading
        data = json.load(json_file)

        return data


def _validate_max_poll_wait_secs(max_poll_wait_secs):
    valid_max_poll_wait_secs = 0.0
    error_message = f"--max-poll-wait-secs parameter is not valid: {max_poll_wait_secs}"
    error_recommendation = f"Must be a number greater than or equal to {MINIMUM_MAX_POLL_WAIT_SECS}"

    try:
        valid_max_poll_wait_secs = float(max_poll_wait_secs)
    except ValueError as e:
        raise InvalidArgumentValueError(error_message, error_recommendation) from e

    if valid_max_poll_wait_secs < MINIMUM_MAX_POLL_WAIT_SECS:
        raise InvalidArgumentValueError(error_message, error_recommendation)

    return valid_max_poll_wait_secs
