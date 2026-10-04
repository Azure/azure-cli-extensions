# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

################################################################################
# Export
################################################################################

UID = "uid"
KIND = "kind"
INSTANCE_NAME = "instanceName"
NAMESPACE = "instanceNamespace"

LAST_USAGE_UPLOAD_FLAG = "end_usage"
"""
Key of flag in usage file indicating last usage upload
"""

DEFAULT_LOG_QUERY_WINDOW_IN_MINUTE = 14 * 24 * 60
"""
Default log query window in minute
"""

DEFAULT_USAGE_QUERY_WINDOW_IN_MINUTE = 62 * 24 * 60
"""
Default usage query window in minute
"""

DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE = 28
"""
Default metric query window in minute
"""

DEFAULT_QUERY_WINDOW = {
    "metrics": DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE,
    "logs": DEFAULT_LOG_QUERY_WINDOW_IN_MINUTE,
    "usage": DEFAULT_USAGE_QUERY_WINDOW_IN_MINUTE,
}
