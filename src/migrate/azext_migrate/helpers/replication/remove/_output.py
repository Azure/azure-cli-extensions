# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Output formatting utilities for Azure Migrate replication removal.
"""

from knack.log import get_logger

logger = get_logger(__name__)


def display_removal_success(protected_item_name, job_name,
                           resource_group_name):
    """
    Display success message with job tracking information.

    Args:
        protected_item_name (str): Name of the protected item
        job_name (str): Name of the removal job
        resource_group_name (str): Resource group name
    """
    print(f"Successfully initiated removal of replication for "
          f"'{protected_item_name}'.")
    print(f"Job ID: {job_name}")
    print(f"\nTo check removal job status, run:")
    print(f"  az migrate local replication get-job "
          f"--job-name {job_name} "
          f"--resource-group {resource_group_name} "
          f"--project-name <project-name>")


def display_removal_initiated(protected_item_name):
    """
    Display simple success message when job details are unavailable.

    Args:
        protected_item_name (str): Name of the protected item
    """
    print(f"Successfully initiated removal of replication for "
          f"'{protected_item_name}'.")


def log_removal_success(protected_item_name, job_name=None):
    """
    Log successful removal initiation.

    Args:
        protected_item_name (str): Name of the protected item
        job_name (str, optional): Name of the removal job
    """
    if job_name:
        logger.info(
            "Successfully initiated removal of replication "
            "for '%s'. Job: %s",
            protected_item_name, job_name)
    else:
        logger.info(
            "Successfully initiated removal of replication for '%s'",
            protected_item_name)
