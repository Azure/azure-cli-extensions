# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import os

from azext_arcdata.core.constants import ARC_API_V2

RESOURCE_KIND = "SqlManagedInstance"
"""
Defines the Kubernetes custom resource kind.
"""

RESOURCE_KIND_PLURAL = "sqlmanagedinstances"
"""
Defines the plural name.
"""

API_GROUP = "sql.arcdata.microsoft.com"
"""
Defines the API group.
"""

TASK_API_GROUP = "tasks.sql.arcdata.microsoft.com"
"""
The Kubernetes group for SQL MI task crd.
"""

FOG_RESOURCE_KIND = "FailoverGroup"

FOG_RESOURCE_KIND_PLURAL = "failovergroups"

FOG_API_GROUP = "sql.arcdata.microsoft.com"

FOG_API_VERSION = ARC_API_V2

BASE = os.path.dirname(os.path.realpath(__file__))
"""
Base directory
"""

TEMPLATE_DIR = os.path.join(BASE, "templates")
"""
Custom resource definition directory
"""

SQLMI_SPEC = os.path.join(TEMPLATE_DIR, "sqlmi_spec.json")
"""
File location for sqlmi SPEC.
"""

FOG_SPEC = os.path.join(TEMPLATE_DIR, "fog_spec.json")
"""
File location for fog SPEC.
"""

SQLMI_DIRECT_MODE_SPEC_MERGE = os.path.join(
    TEMPLATE_DIR, "sqlmi_default_properties_merge.json"
)
"""
File location for sqlmi direct mode SPEC output.
"""

SQLMI_DIRECT_MODE_OUTPUT_SPEC = os.path.join(
    TEMPLATE_DIR, "sqlmi_default_properties_output.json"
)
"""
File location for sqlmi direct mode SPEC output.
"""


DAG_ROLE_PRIMARY = "primary"
DAG_ROLE_SECONDARY = "secondary"
DAG_ROLE_FORCE_PRIMARY = "force-primary-allow-data-loss"
DAG_ROLE_FORCE_SECONDARY = "force-secondary"

DAG_ROLES_ALL = set(
    [
        DAG_ROLE_PRIMARY,
        DAG_ROLE_SECONDARY,
        DAG_ROLE_FORCE_PRIMARY,
        DAG_ROLE_FORCE_SECONDARY,
    ]
)

DAG_ROLES_CREATE = set(
    [
        DAG_ROLE_PRIMARY,
        DAG_ROLE_SECONDARY,
    ]
)

DAG_ROLES_UPDATE = set(
    [
        DAG_ROLE_SECONDARY,
        DAG_ROLE_FORCE_PRIMARY,
        DAG_ROLE_FORCE_SECONDARY,
    ]
)

DAG_ROLES_ALLOWED_VALUES_MSG_CREATE = (
    "Allowed values are: {0}, {1}. "
    "Role can be changed.".format(
        DAG_ROLE_PRIMARY,
        DAG_ROLE_SECONDARY,
    )
)

DAG_ROLES_ALLOWED_VALUES_MSG_UPDATE = (
    "Role can only be changed to: {0}, {1}, {2}. ".format(
        DAG_ROLE_SECONDARY,
        DAG_ROLE_FORCE_PRIMARY,
        DAG_ROLE_FORCE_SECONDARY,
    )
)

DAG_PARTNER_SYNC_MODE_ASYNC = "async"
DAG_PARTNER_SYNC_MODE_SYNC = "sync"

DAG_PARTNER_SYNC_MODE = set(
    [
        DAG_PARTNER_SYNC_MODE_ASYNC,
        DAG_PARTNER_SYNC_MODE_SYNC,
    ]
)

DAG_RPARTNER_SYNC_MODE_ALLOWED_MSG = (
    "Allowed values are: {0}, {1}. "
    "Partner sync mode can be changed.".format(
        DAG_PARTNER_SYNC_MODE_ASYNC,
        DAG_PARTNER_SYNC_MODE_SYNC,
    )
)
