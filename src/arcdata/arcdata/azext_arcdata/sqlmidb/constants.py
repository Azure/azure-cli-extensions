# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.constants import ARC_API_V1

RESTORE_TASK_RESOURCE_KIND = "SqlManagedInstanceRestoreTask"
"""
Defines the Kubernetes custom resource kind for sql mi restore task
"""
RESTORE_TASK_RESOURCE_KIND_PLURAL = "sqlmanagedinstancerestoretasks"
"""
Defines the plural name for sql mi restore task
"""
TASK_API_GROUP = "tasks.sql.arcdata.microsoft.com"
"""
The Kubernetes group for SQL MI task crd.
"""
TASK_API_VERSION = ARC_API_V1
"""
The Kubernetes version for SQL MI task resources.
"""
