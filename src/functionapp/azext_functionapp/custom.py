# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

from knack.log import get_logger

logger = get_logger(__name__)
FILE_SHARE_CREATE_RETRY_DELAYS = (5, 10, 20, 40)


def create_devops_pipeline(
        cmd,
        functionapp_name=None,
        organization_name=None,
        project_name=None,
        repository_name=None,
        overwrite_yaml=None,
        allow_force_push=None,
        github_pat=None,
        github_repository=None
):
    from .azure_devops_build_interactive import AzureDevopsBuildInteractive
    azure_devops_build_interactive = AzureDevopsBuildInteractive(cmd, logger, functionapp_name,
                                                                 organization_name, project_name, repository_name,
                                                                 overwrite_yaml, allow_force_push,
                                                                 github_pat, github_repository)
    return azure_devops_build_interactive.interactive_azure_devops_build()


def create_functionapp(cmd, resource_group_name, name, storage_account, **kwargs):
    from azure.cli.command_modules.appservice import custom as core_custom

    original_create_file_share = core_custom.create_file_share

    def create_file_share_with_retry(cli_ctx, file_share_resource_group, file_share_storage_account, share_name):
        for attempt, delay in enumerate(FILE_SHARE_CREATE_RETRY_DELAYS, start=1):
            try:
                return original_create_file_share(cli_ctx, file_share_resource_group, file_share_storage_account,
                                                  share_name)
            except Exception as ex:  # pylint: disable=broad-except
                if _get_status_code(ex) != 403:
                    raise

                logger.warning(
                    "Storage file share creation failed with HTTP 403 for storage account '%s'. "
                    "This can happen while storage network rules are still propagating. "
                    "Retrying in %s seconds (%s/%s).",
                    file_share_storage_account,
                    delay,
                    attempt,
                    len(FILE_SHARE_CREATE_RETRY_DELAYS))
                time.sleep(delay)

        try:
            return original_create_file_share(cli_ctx, file_share_resource_group, file_share_storage_account,
                                              share_name)
        except Exception as ex:  # pylint: disable=broad-except
            if _get_status_code(ex) != 403:
                raise

            from knack.util import CLIError
            raise CLIError(
                "Creation of storage file share failed with HTTP 403 (Forbidden) after retrying. "
                "This usually means the storage account's virtual network or firewall rules have not finished "
                "propagating yet. Please wait a few minutes and try again. "
                "Original error: '{}'.".format(ex)
            ) from ex

    core_custom.create_file_share = create_file_share_with_retry
    try:
        return core_custom.create_functionapp(
            cmd,
            resource_group_name,
            name,
            storage_account,
            **kwargs)
    finally:
        core_custom.create_file_share = original_create_file_share


def _get_status_code(ex):
    status_code = getattr(ex, 'status_code', None)
    if status_code is None:
        response = getattr(ex, 'response', None)
        status_code = getattr(response, 'status_code', None) or getattr(response, 'status', None)

    try:
        return int(status_code)
    except (TypeError, ValueError):
        return None
