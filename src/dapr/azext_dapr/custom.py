# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess

from knack.util import CLIError
from azext_dapr._client_factory import get_dapr_cli_path 

def update_dapr(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

def status_dapr(cmd):
    try:
        dapr_cli_path = get_dapr_cli_path()
        subprocess.call([dapr_cli_path, "status", "-k"],
                            stderr=subprocess.STDOUT)
    except Exception as e:
        raise CLIError(e.output)