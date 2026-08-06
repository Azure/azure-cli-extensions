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
    print("Successfully initiated removal of replication for "
          "'{}'.".format(protected_item_name))
    print("Job ID: {}".format(job_name))
    print("\nTo check removal job status, run:")
    print("  az migrate local replication get-job "
          "--job-name {} "
          "--resource-group {} "
          "--project-name <project-name>".format(job_name, resource_group_name))


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
