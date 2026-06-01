# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Helpers that delegate AKS backup enablement to the dataprotection CLI extension.

The actual orchestration (vault, policy, storage account, extension install,
trusted access, role assignments, backup instance) lives in the
``dataprotection`` extension. This module is a thin shim that:

* loads that extension's path lazily (so ``az aks`` works without it),
* offers to install the extension on-demand if it is missing (and installs
  silently when ``--yes`` is passed),
* derives the AKS datasource ARM id from the resource group + cluster name.
"""

from knack.log import get_logger
from knack.prompting import prompt_y_n, NoTTYException

from azure.cli.core.azclierror import RequiredArgumentMissingError

DATAPROTECTION_EXTENSION_NAME = "dataprotection"

logger = get_logger(__name__)


def _ensure_dataprotection_extension(cmd, yes):
    """Make ``azext_dataprotection.manual.aks.aks_helper`` importable.

    If the ``dataprotection`` extension is not installed, prompt the user to
    install it (or install silently when ``yes`` is True). Raises
    ``RequiredArgumentMissingError`` if the user declines or the install fails.
    """
    from azure.cli.core.extension.operations import add_extension_to_path

    try:
        add_extension_to_path(DATAPROTECTION_EXTENSION_NAME)
        from azext_dataprotection.manual.aks.aks_helper import (  # pylint: disable=unused-import
            dataprotection_enable_backup_helper,
        )
        return
    except ImportError:
        pass

    install_msg = (
        f"The '{DATAPROTECTION_EXTENSION_NAME}' extension is required for "
        "--enable-backup but is not installed. Install it now?"
    )
    proceed = yes
    if not proceed:
        try:
            proceed = prompt_y_n(install_msg, default="y")
        except NoTTYException:
            proceed = False
    if not proceed:
        raise RequiredArgumentMissingError(
            f"The '{DATAPROTECTION_EXTENSION_NAME}' extension is required for "
            "--enable-backup with 'az aks create' / 'az aks update'.\n"
            f"Run `az extension add --name {DATAPROTECTION_EXTENSION_NAME}` "
            "and retry, or rerun with --yes to auto-install."
        )

    logger.warning("Installing extension '%s'...", DATAPROTECTION_EXTENSION_NAME)
    from azure.cli.core.extension.operations import add_extension
    add_extension(cmd=cmd, extension_name=DATAPROTECTION_EXTENSION_NAME)
    add_extension_to_path(DATAPROTECTION_EXTENSION_NAME)


def enable_aks_backup(cmd, resource_group_name, cluster_name,  # pylint: disable=too-many-positional-arguments
                      backup_strategy, backup_configuration_file, yes):
    """Enable Azure Backup for an AKS cluster by delegating to the
    ``dataprotection`` extension.
    """
    from azure.cli.core.commands.client_factory import get_subscription_id

    _ensure_dataprotection_extension(cmd, yes)

    from azext_dataprotection.manual.aks.aks_helper import (  # pylint: disable=import-error
        dataprotection_enable_backup_helper,
    )

    subscription_id = get_subscription_id(cmd.cli_ctx)
    datasource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.ContainerService/managedClusters/{cluster_name}"
    )
    dataprotection_enable_backup_helper(
        cmd,
        datasource_id,
        backup_strategy or "Week",
        backup_configuration_file or {},
        yes=yes,
    )
