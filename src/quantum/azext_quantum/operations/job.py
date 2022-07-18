# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=redefined-builtin,bare-except,inconsistent-return-statements

import logging
import knack.log

from azure.cli.core.azclierror import (FileOperationError, AzureInternalError,
                                       InvalidArgumentValueError, AzureResponseError)

from .._client_factory import cf_jobs, _get_data_credentials
from .workspace import WorkspaceInfo
from .target import TargetInfo

MINIMUM_MAX_POLL_WAIT_SECS = 1

logger = logging.getLogger(__name__)
knack_logger = knack.log.get_logger(__name__)


def list(cmd, resource_group_name=None, workspace_name=None, location=None):
    """
    Get the list of jobs in a Quantum Workspace.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.list()


def get(cmd, job_id, resource_group_name=None, workspace_name=None, location=None):
    """
    Get the job's status and details.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    return client.get(job_id)


def _check_dotnet_available():
    """
    Will fail if dotnet cannot be executed on the system.
    """
    args = ["dotnet", "--version"]

    try:
        import subprocess
        result = subprocess.run(args, stdout=subprocess.PIPE, check=False)
    except FileNotFoundError as e:
        raise FileOperationError("Could not find 'dotnet' on the system.") from e

    if result.returncode != 0:
        raise FileOperationError(f"Failed to run 'dotnet'. (Error {result.returncode})")


def build(cmd, target_id=None, project=None, target_capability=None):
    """
    Compile a Q# program to run on Azure Quantum.
    """
    target = TargetInfo(cmd, target_id)

    # Validate that dotnet is available
    _check_dotnet_available()

    args = ["dotnet", "build"]

    if project:
        args.append(project)

    args.append(f"-property:ExecutionTarget={target.target_id}")

    if target_capability:
        args.append(f"-property:TargetCapability={target_capability}")

    logger.debug("Building project with arguments:")
    logger.debug(args)

    knack_logger.warning('Building project...')

    import subprocess
    result = subprocess.run(args, stdout=subprocess.PIPE, check=False)

    if result.returncode == 0:
        return {'result': 'ok'}

    # If we got here, we might have encountered an error during compilation, so propagate standard output to the user.
    logger.error("Compilation stage failed with error code %s", result.returncode)
    print(result.stdout.decode('ascii'))
    raise AzureInternalError("Failed to compile program.")


def _generate_submit_args(program_args, ws, target, token, project, job_name, shots, storage, job_params):
    """ Generates the list of arguments for calling submit on a Q# project """

    args = ["dotnet", "run", "--no-build"]

    if project:
        args.append("--project")
        args.append(project)

    args.append("--")
    args.append("submit")

    args.append("--subscription")
    args.append(ws.subscription)

    args.append("--resource-group")
    args.append(ws.resource_group)

    args.append("--workspace")
    args.append(ws.name)

    args.append("--target")
    args.append(target.target_id)

    args.append("--output")
    args.append("Id")

    if job_name:
        args.append("--job-name")
        args.append(job_name)

    if shots:
        args.append("--shots")
        args.append(shots)

    if storage:
        args.append("--storage")
        args.append(storage)

    args.append("--aad-token")
    args.append(token)

    args.append("--location")
    args.append(ws.location)

    args.append("--user-agent")
    args.append("CLI")

    if job_params:
        args.append("--job-params")
        for k, v in job_params.items():
            args.append(f"{k}={v}")

    args.extend(program_args)

    logger.debug("Running project with arguments:")
    logger.debug(args)

    return args


def _set_cli_version():
    # This is a temporary approach for runtime compatibility between a runtime version
    # before support for the --user-agent parameter is added. We'll rely on the environment
    # variable before the stand alone executable submits to the service.
    try:
        import os
        from .._client_factory import get_appid
        os.environ["USER_AGENT"] = get_appid()
    except:
        logger.warning("User Agent environment variable could not be set.")


def _has_completed(job):
    return job.status in ("Succeeded", "Failed", "Cancelled")


def submit(cmd, program_args, resource_group_name=None, workspace_name=None, location=None, target_id=None,
           project=None, job_name=None, shots=None, storage=None, no_build=False, job_params=None,
           target_capability=None):
    """
    Submit a Q# project to run on Azure Quantum.
    """

    # We first build and then call run.
    # Can't call run directly because it fails to understand the
    # `ExecutionTarget` property when passed in the command line
    if not no_build:
        build(cmd, target_id=target_id, project=project, target_capability=target_capability)
        logger.info("Project built successfully.")
    else:
        _check_dotnet_available()

    ws = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    target = TargetInfo(cmd, target_id)
    token = _get_data_credentials(cmd.cli_ctx, ws.subscription).get_token().token

    args = _generate_submit_args(program_args, ws, target, token, project, job_name, shots, storage, job_params)
    _set_cli_version()

    knack_logger.warning('Submitting job...')

    import subprocess
    result = subprocess.run(args, stdout=subprocess.PIPE, check=False)

    if result.returncode == 0:
        std_output = result.stdout.decode('ascii').strip()
        # Retrieve the job-id as the last line from standard output.
        job_id = std_output.split()[-1]
        # Query for the job and return status to caller.
        return get(cmd, job_id, resource_group_name, workspace_name, location)

    # The program compiled succesfully, but executing the stand-alone .exe failed to run.
    logger.error("Submission of job failed with error code %s", result.returncode)
    print(result.stdout.decode('ascii'))
    raise AzureInternalError("Failed to submit job.")


def _parse_blob_url(url):
    from urllib.parse import urlparse
    o = urlparse(url)

    try:
        account_name = o.netloc.split('.')[0]
        container = o.path.split('/')[-2]
        blob = o.path.split('/')[-1]
        sas_token = o.query
    except IndexError as e:
        raise InvalidArgumentValueError(f"Failed to parse malformed blob URL: {url}") from e

    return {
        "account_name": account_name,
        "container": container,
        "blob": blob,
        "sas_token": sas_token
    }


def output(cmd, job_id, resource_group_name=None, workspace_name=None, location=None):
    """
    Get the results of running a Q# job.
    """
    import tempfile
    import json
    import os
    from azure.cli.command_modules.storage._client_factory import blob_data_service_factory

    path = os.path.join(tempfile.gettempdir(), job_id)
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    job = client.get(job_id)

    if os.path.exists(path):
        logger.debug("Using existing blob from %s", path)
    else:
        logger.debug("Downloading job results blob into %s", path)

        if job.status != "Succeeded":
            return job  # If "-o table" is specified, this allows transform_output() in commands.py
            #             to format the output, so the error info is shown. If "-o json" or no "-o"
            #             parameter is specified, then the full JSON job output is displayed, being
            #             consistent with other commands.

        args = _parse_blob_url(job.output_data_uri)
        blob_service = blob_data_service_factory(cmd.cli_ctx, args)
        blob_service.get_blob_to_path(args['container'], args['blob'], path)

    with open(path) as json_file:
        lines = [line.strip() for line in json_file.readlines()]

        # Receiving an empty response is valid.
        if len(lines) == 0:
            return

        if job.target.startswith("microsoft.simulator"):
            result_start_line = len(lines) - 1
            is_result_string = lines[-1].endswith('"')
            if is_result_string:
                while result_start_line >= 0 and not lines[result_start_line].startswith('"'):
                    result_start_line -= 1
            if result_start_line < 0:
                raise AzureResponseError("Job output is malformed, mismatched quote characters.")

            # Print the job output and then the result of the operation as a histogram.
            # If the result is a string, trim the quotation marks.
            print('\n'.join(lines[:result_start_line]))
            raw_result = ' '.join(lines[result_start_line:])
            result = raw_result[1:-1] if is_result_string else raw_result
            print('_' * len(result) + '\n')

            json_string = '{ "histogram" : { "' + result + '" : 1 } }'
            data = json.loads(json_string)
        else:
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


def wait(cmd, job_id, resource_group_name=None, workspace_name=None, location=None, max_poll_wait_secs=5):
    """
    Place the CLI in a waiting state until the job finishes running.
    """
    import time

    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)

    # TODO: LROPoller...
    wait_indicators_used = False
    poll_wait = 0.2
    max_poll_wait_secs = _validate_max_poll_wait_secs(max_poll_wait_secs)
    job = client.get(job_id)

    while not _has_completed(job):
        print('.', end='', flush=True)
        wait_indicators_used = True
        time.sleep(poll_wait)
        job = client.get(job_id)
        poll_wait = max_poll_wait_secs if poll_wait >= max_poll_wait_secs else poll_wait * 1.5

    if wait_indicators_used:
        # Insert a new line if we had to display wait indicators.
        print()

    return job


def run(cmd, program_args, resource_group_name=None, workspace_name=None, location=None, target_id=None,
        project=None, job_name=None, shots=None, storage=None, no_build=False, job_params=None, target_capability=None):
    """
    Submit a job to run on Azure Quantum, and waits for the result.
    """
    job = submit(cmd, program_args, resource_group_name, workspace_name, location, target_id,
                 project, job_name, shots, storage, no_build, job_params, target_capability)
    logger.warning("Job id: %s", job.id)
    logger.debug(job)

    job = wait(cmd, job.id, resource_group_name, workspace_name, location)
    logger.debug(job)

    if not job.status == "Succeeded":
        return job

    return output(cmd, job.id, resource_group_name, workspace_name, location)


def cancel(cmd, job_id, resource_group_name=None, workspace_name=None, location=None):
    """
    Request to cancel a job on Azure Quantum if it hasn't completed.
    """
    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
    job = client.get(job_id)

    if _has_completed(job):
        print(f"Job {job_id} has already completed with status: {job.status}.")
        return

    # If the job hasn't succeeded or failed, attempt to cancel.
    client.cancel(job_id)

    # Wait for the job status to complete or be reported as cancelled
    return wait(cmd, job_id, info.resource_group, info.name, info.location)
