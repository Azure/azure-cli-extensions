# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=redefined-builtin

import logging

from knack.util import CLIError

from .._client_factory import cf_jobs, _get_data_credentials, base_url
from .workspace import WorkspaceInfo
from .target import TargetInfo

logger = logging.getLogger(__name__)


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


def build(cmd, target_id=None, project=None):
    """
    Compile a Q# program to run on Azure Quantum.
    """
    target = TargetInfo(cmd, target_id)

    args = ["dotnet", "build"]

    args.append(f"-property:ExecutionTarget={target.target_id}")

    if project:
        args.append("--project")
        args.append(project)

    logger.debug("Building project with arguments:")
    logger.debug(args)

    import subprocess
    result = subprocess.run(args, stdout=subprocess.PIPE, check=False)

    if result.returncode == 0:
        return {'result': 'ok'}

    raise CLIError("Failed to compile program.")


def _generate_submit_args(program_args, ws, target, token, project, job_name, shots, storage):
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


def submit(cmd, program_args, resource_group_name=None, workspace_name=None, location=None,
           target_id=None, project=None, job_name=None, shots=None, storage=None, no_build=False):
    """
    Submit a Q# project to run on Azure Quantum.
    """

    # We first build and then call run.
    # Can't call run directly because it fails to understand the
    # `ExecutionTarget` property when passed in the command line
    if not no_build:
        build(cmd, target_id=target_id, project=project)

    logger.info("Project built successfully.")

    ws = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    target = TargetInfo(cmd, target_id)
    token = _get_data_credentials(cmd.cli_ctx, ws.subscription).get_token().token

    args = _generate_submit_args(program_args, ws, target, token, project, job_name, shots, storage)
    _set_cli_version()

    import subprocess
    result = subprocess.run(args, stdout=subprocess.PIPE, check=False)

    if result.returncode == 0:
        job_id = result.stdout.decode('ascii').strip()
        return get(cmd, job_id, resource_group_name, workspace_name, location)

    raise CLIError("Failed to submit job.")


def _parse_blob_url(url):
    from urllib.parse import urlparse
    o = urlparse(url)

    try:
        account_name = o.netloc.split('.')[0]
        container = o.path.split('/')[-2]
        blob = o.path.split('/')[-1]
        sas_token = o.query
    except IndexError:
        raise CLIError(f"Failed to parse malformed blob URL: {url}")

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

    if os.path.exists(path):
        logger.debug("Using existing blob from %s", path)
    else:
        logger.debug("Downloading job results blob into %s", path)

        info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
        client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)
        job = client.get(job_id)

        if job.status != "Succeeded":
            return f"Job status: {job.status}. Output only available if Succeeded."

        args = _parse_blob_url(job.output_data_uri)
        blob_service = blob_data_service_factory(cmd.cli_ctx, args)
        blob_service.get_blob_to_path(args['container'], args['blob'], path)

    with open(path) as json_file:
        data = json.load(json_file)
        return data


def wait(cmd, job_id, resource_group_name=None, workspace_name=None, location=None, max_poll_wait_secs=5):
    """
    Place the CLI in a waiting state until the job finishes running.
    """
    import time

    def has_completed(job):
        return job.status in ("Succeeded", "Failed", "Cancelled")

    info = WorkspaceInfo(cmd, resource_group_name, workspace_name, location)
    client = cf_jobs(cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.location)

    # TODO: LROPoller...
    wait_indicators_used = False
    poll_wait = 0.2
    job = client.get(job_id)

    while not has_completed(job):
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
        project=None, job_name=None, shots=None, storage=None, no_build=False):
    """
    Submit a job to run on Azure Quantum, and waits for the result.
    """
    job = submit(cmd, program_args, resource_group_name, workspace_name, location, target_id, project, job_name, shots, storage, no_build)
    logger.warning("Job id: %s", job.id)
    logger.debug(job)

    job = wait(cmd, job.id, resource_group_name, workspace_name, location)
    logger.debug(job)

    if not job.status == "Succeeded":
        return job

    return output(cmd, job.id, resource_group_name, workspace_name)
