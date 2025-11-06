# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

ACI_MOUNTS = [
    {
        "destination": "/etc/resolv.conf",
        "options": [
            "rbind",
            "rshared",
            "rw"
        ],
        "source": "sandbox:///tmp/atlas/resolvconf/.+",
        "type": "bind"
    }
]