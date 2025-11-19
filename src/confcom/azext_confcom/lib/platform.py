# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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
