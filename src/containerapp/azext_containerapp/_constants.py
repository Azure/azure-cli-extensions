# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# SSH control byte values for container app proxy
SSH_PROXY_FORWARD = 0
SSH_PROXY_INFO = 1
SSH_PROXY_ERROR = 2

# SSH control byte values for container app cluster
SSH_CLUSTER_STDIN = 0
SSH_CLUSTER_STDOUT = 1
SSH_CLUSTER_STDERR = 2

# forward byte + stdin byte
SSH_INPUT_PREFIX = b"\x00\x00"

SSH_DEFAULT_ENCODING = "utf-8"
SSH_BACKUP_ENCODING = "latin_1"
