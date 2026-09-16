# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook command implementations (generate/show/list/update/
regenerate/delete/wait)."""

import time

from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from azext_migrate.shared import arm_ids
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.runbook import models

logger = get_logger(__name__)


def _project_id(cmd, resource_group_name, project_name):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return arm_ids.migrate_project_id(
        subscription_id, resource_group_name, project_name)


def _matches(runbook, wave_name, status):
    props = runbook.get('properties', {}) or {}
    if status and props.get('status') != status:
        return False
    if wave_name:
        scope = props.get('scope', {}) or {}
        wid = (scope.get('waveId', '') or '').rstrip('/')
        if not wid.endswith('/waves/' + wave_name):
            return False
    return True


def generate(cmd, resource_group_name, project_name, runbook_name,
             wave_name, no_wait=False):
    """Generate (create) a runbook scoped to a wave."""
    project = _project_id(cmd, resource_group_name, project_name)
    resource_id = arm_ids.runbook_id(project, runbook_name)
    body = models.build_generate_body(models.wave_id(project, wave_name))
    return ArmClient(cmd).put(resource_id, body, no_wait=no_wait)


def show(cmd, resource_group_name, project_name, runbook_name):
    """Get a single runbook."""
    project = _project_id(cmd, resource_group_name, project_name)
    resource_id = arm_ids.runbook_id(project, runbook_name)
    return ArmClient(cmd).get(resource_id)


def list_(cmd, resource_group_name, project_name, wave_name=None,
          status=None):
    """List runbooks, optionally filtered by wave and/or status."""
    project = _project_id(cmd, resource_group_name, project_name)
    collection_id = project + '/runbooks'
    items = ArmClient(cmd).list(collection_id)
    return [rb for rb in items if _matches(rb, wave_name, status)]


def delete(cmd, resource_group_name, project_name, runbook_name,
           no_wait=False):
    """Delete a runbook."""
    project = _project_id(cmd, resource_group_name, project_name)
    resource_id = arm_ids.runbook_id(project, runbook_name)
    return ArmClient(cmd).delete(resource_id, no_wait=no_wait)


def update(cmd, resource_group_name, project_name, runbook_name,
           description=None):
    """Update editable runbook metadata (e.g. description)."""
    project = _project_id(cmd, resource_group_name, project_name)
    resource_id = arm_ids.runbook_id(project, runbook_name)
    body = models.build_update_body(description)
    return ArmClient(cmd).patch(resource_id, body)


def regenerate(cmd, resource_group_name, project_name, runbook_name,
               no_wait=False):
    """Regenerate a runbook: delete it, then re-create it from its scope.

    The service has no Regenerate action, so the CLI reads the runbook's
    current scope (wave), deletes the runbook, and re-generates it with the
    same scope.
    """
    project = _project_id(cmd, resource_group_name, project_name)
    resource_id = arm_ids.runbook_id(project, runbook_name)
    client = ArmClient(cmd)
    existing = client.get(resource_id)
    scope = ((existing or {}).get('properties') or {}).get('scope') or {}
    wave_id = scope.get('waveId')
    if not wave_id:
        raise CLIError(
            'Cannot regenerate: the runbook has no wave scope to '
            'regenerate from.')
    logger.warning(
        "Regenerating runbook '%s': deleting and re-creating from its "
        "wave scope.", runbook_name)
    client.delete(resource_id)
    body = models.build_generate_body(wave_id)
    return client.put(resource_id, body, no_wait=no_wait)


def _provisioning_state(runbook):
    props = (runbook or {}).get('properties', {}) or {}
    return runbook.get('provisioningState') or \
        props.get('provisioningState')


def wait(cmd, resource_group_name, project_name, runbook_name,
         created=False, updated=False, deleted=False, exists=False,
         custom=None, interval=30, timeout=3600):
    """Poll a runbook until a wait condition is met, logging progress."""
    from azure.cli.core.commands.arm import verify_property
    from azure.cli.core.azclierror import (
        InvalidArgumentValueError, AzureResponseError)

    if not any([created, updated, deleted, exists, custom]):
        raise InvalidArgumentValueError(
            'incorrect usage: --created | --updated | --deleted | '
            '--exists | --custom JMESPATH')

    project = _project_id(cmd, resource_group_name, project_name)
    resource_id = arm_ids.runbook_id(project, runbook_name)
    client = ArmClient(cmd)

    active = ', '.join(name for name, on in (
        ('created', created), ('updated', updated), ('deleted', deleted),
        ('exists', exists), ('custom', custom)) if on)
    logger.warning(
        "Waiting for runbook '%s' [condition: %s, interval: %ss, "
        "timeout: %ss].", runbook_name, active, interval, timeout)

    start = time.monotonic()
    attempt = 0
    for _ in range(0, timeout, interval):
        attempt += 1
        elapsed = int(time.monotonic() - start)
        instance = client.get_or_none(resource_id)

        if instance is None:
            if deleted:
                logger.warning(
                    "Runbook '%s' is deleted (elapsed %ss, %s poll(s)).",
                    runbook_name, elapsed, attempt)
                return None
            logger.warning(
                "Runbook '%s' not found yet (elapsed %ss, poll #%s, "
                "next check in %ss).",
                runbook_name, elapsed, attempt, interval)
            time.sleep(interval)
            continue

        if exists:
            logger.warning(
                "Runbook '%s' exists (elapsed %ss, %s poll(s)).",
                runbook_name, elapsed, attempt)
            return None

        state = _provisioning_state(instance)
        norm = state.lower() if state else None
        if norm == 'failed':
            raise AzureResponseError(
                "Runbook '%s' provisioning failed "
                "(provisioningState=Failed)." % runbook_name)
        if custom and bool(verify_property(instance, custom)):
            logger.warning(
                "Custom condition '%s' met (elapsed %ss, %s poll(s)).",
                custom, elapsed, attempt)
            return None
        if (created or updated) and norm == 'succeeded':
            logger.warning(
                "Runbook '%s' provisioningState=Succeeded "
                "(elapsed %ss, %s poll(s)).",
                runbook_name, elapsed, attempt)
            return None

        logger.warning(
            "Still waiting for runbook '%s': provisioningState=%s "
            "(elapsed %ss, poll #%s, next check in %ss).",
            runbook_name, state or '(none)', elapsed, attempt, interval)
        time.sleep(interval)

    raise CLIError(
        'Wait operation timed out after %ss.' % timeout)
