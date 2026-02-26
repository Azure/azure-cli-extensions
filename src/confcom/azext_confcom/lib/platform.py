# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_confcom.lib.policy import ContainerMount

ACI_MOUNTS = [
    ContainerMount(
        destination="/etc/resolv.conf",
        options=[
            "rbind",
            "rshared",
            "rw"
        ],
        source="sandbox:///tmp/atlas/resolvconf/.+",
        type="bind"
    )
]

VN2_MOUNTS = [
    {
        "destination": "/etc/resolv.conf",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    },
    {
        "destination": "/var/run/secrets/kubernetes.io/serviceaccount",
        "options": [
            "rbind",
            "rshared",
            "ro"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    },
    {
        "destination": "/etc/hosts",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    },
    {
        "destination": "/dev/termination-log",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    },
    {
        "destination": "/etc/hostname",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    }
]

VN2_PRIVILEGED_MOUNTS = [
    {
        "destination": "/sys/fs/cgroup",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    },
    {
        "destination": "/sys",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    },
]

VN2_WORKLOAD_IDENTITY_ENV_RULES = [
    {
        "name": "AZURE_CLIENT_ID",
        "value": ".+",
        "strategy": "re2",
        "required": False
    },
    {
        "name": "AZURE_TENANT_ID",
        "value": ".+",
        "strategy": "re2",
        "required": False
    },
    {
        "name": "AZURE_FEDERATED_TOKEN_FILE",
        "value": ".+",
        "strategy": "re2",
        "required": False
    },
    {
        "name": "AZURE_AUTHORITY_HOST",
        "value": ".+",
        "strategy": "re2",
        "required": False
    }
]


VN2_WORKLOAD_IDENTITY_MOUNTS = [
    {
        "destination": "/var/run/secrets/azure/tokens",
        "options": [
            "rbind",
            "rshared",
            "ro"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
    },
]

_PRIVILEDGED_CAPABILITIES = [
    "CAP_AUDIT_CONTROL",
    "CAP_AUDIT_READ",
    "CAP_AUDIT_WRITE",
    "CAP_BLOCK_SUSPEND",
    "CAP_BPF",
    "CAP_CHECKPOINT_RESTORE",
    "CAP_CHOWN",
    "CAP_DAC_OVERRIDE",
    "CAP_DAC_READ_SEARCH",
    "CAP_FOWNER",
    "CAP_FSETID",
    "CAP_IPC_LOCK",
    "CAP_IPC_OWNER",
    "CAP_KILL",
    "CAP_LEASE",
    "CAP_LINUX_IMMUTABLE",
    "CAP_MAC_ADMIN",
    "CAP_MAC_OVERRIDE",
    "CAP_MKNOD",
    "CAP_NET_ADMIN",
    "CAP_NET_BIND_SERVICE",
    "CAP_NET_BROADCAST",
    "CAP_NET_RAW",
    "CAP_PERFMON",
    "CAP_SETFCAP",
    "CAP_SETGID",
    "CAP_SETPCAP",
    "CAP_SETUID",
    "CAP_SYSLOG",
    "CAP_SYS_ADMIN",
    "CAP_SYS_BOOT",
    "CAP_SYS_CHROOT",
    "CAP_SYS_MODULE",
    "CAP_SYS_NICE",
    "CAP_SYS_PACCT",
    "CAP_SYS_PTRACE",
    "CAP_SYS_RAWIO",
    "CAP_SYS_RESOURCE",
    "CAP_SYS_TIME",
    "CAP_SYS_TTY_CONFIG",
    "CAP_WAKE_ALARM"
]
PRIVILEDGED_CAPABILITIES = {
    "ambient": [],
    "bounding": _PRIVILEDGED_CAPABILITIES,
    "effective": _PRIVILEDGED_CAPABILITIES,
    "inheritable": _PRIVILEDGED_CAPABILITIES,
    "permitted": _PRIVILEDGED_CAPABILITIES
}
