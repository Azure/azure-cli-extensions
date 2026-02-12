# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from azext_arcdata.vendored_sdks.kubernetes_sdk.models.kube_quantity import KubeQuantity
from azext_arcdata.core.constants import (
    ARC_API_V1BETA1,
    ARC_API_V1BETA6,
)
import os

RESOURCE_KIND = "PostgreSql"
"""
Kubernetes resource kind for PostgreSQL.
"""

RESOURCE_KIND_PLURAL = "postgresqls"
"""
Kubernetes plural resource kind for PostgreSQL.
"""

API_GROUP = "arcdata.microsoft.com"
"""
Defines the API group.
"""

API_VERSION = ARC_API_V1BETA6
"""
Defines the API version.
"""

RESTORE_TASK_KIND = "PostgreSqlRestoreTask"
"""
Kubernetes resource kind for the PostgreSQL Restore Task.
"""

RESTORE_TASK_PLURAL = "postgresqlrestoretasks"
"""
Kubernetes plural resource kind for the PostgreSQL Restore Task.
"""

RESTORE_TASK_API_GROUP = "tasks.postgresql.arcdata.microsoft.com"
"""
Defines the API group for the PostgreSQL Restore Task.
"""

RESTORE_TASK_API_VERSION = ARC_API_V1BETA1
"""
Defines the API version for the PostgreSQL Restore Task.
"""

COMMAND_UNIMPLEMENTED = "This command is currently unimplemented."
"""
Unimplemented response.
"""

DEFAULT_ENGINE_VERSION = 14
"""
Default engine versions.
"""

# ------------------------------------------------------------------------------
# Postgres resource constants
# ------------------------------------------------------------------------------
POSTGRES_MIN_MEMORY_SIZE = KubeQuantity("256Mi")
POSTGRES_MIN_CORES_SIZE = KubeQuantity("1")

BASE = os.path.dirname(os.path.realpath(__file__))
"""
Base directory
"""

TEMPLATE_DIR = os.path.join(BASE, "templates")
"""
Custom resource definition directory
"""

POSTGRES_SPEC = os.path.join(TEMPLATE_DIR, "postgresql-spec.json")
"""
File location for PostgreSQL spec.
"""

POSTGRESQL_RESTORE_TASK_SPEC = os.path.join(
    TEMPLATE_DIR, "postgresql-restore-task-spec.json"
)
"""
File location for postgres restore task spec.
"""
