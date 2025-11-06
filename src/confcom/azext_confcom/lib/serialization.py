# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from dataclasses import asdict
import json
from pathlib import Path
from textwrap import dedent

from azext_confcom.lib.opa import opa_eval
from azext_confcom.lib.policy import Container, Fragment, Policy


def rego_dict_factory(fields: list) -> dict:
    rego_dict = {}
    for key, value in fields:
        if isinstance(value, str):
            rego_dict[key] = f'"{value}"'
        elif isinstance(value, bool):
            rego_dict[key] = str(value).lower()
        elif key == "fragments" or key == "containers":
            rego_dict[key] = json.dumps(value, indent=2)
        else:
            rego_dict[key] = value

    return rego_dict


def policy_serialize(policy: Policy):

        policy_dict = asdict(policy)
        fragments_json = json.dumps(policy_dict.pop("fragments"), indent=2)
        containers_json = json.dumps(policy_dict.pop("containers"), indent=2)

        return dedent(
f"""
package {policy_dict.pop('package')}

import future.keywords.every
import future.keywords.in

api_version := "{policy_dict.pop('api_version')}"
framework_version := "{policy_dict.pop('framework_version')}"

fragments := {fragments_json}

containers := {containers_json}

{chr(10).join(f"{key} := {str(value).lower()}" for key, value in policy_dict.items())}

mount_device := data.framework.mount_device
unmount_device := data.framework.unmount_device
mount_overlay := data.framework.mount_overlay
unmount_overlay := data.framework.unmount_overlay
create_container := data.framework.create_container
exec_in_container := data.framework.exec_in_container
exec_external := data.framework.exec_external
shutdown_container := data.framework.shutdown_container
signal_container_process := data.framework.signal_container_process
plan9_mount := data.framework.plan9_mount
plan9_unmount := data.framework.plan9_unmount
get_properties := data.framework.get_properties
dump_stacks := data.framework.dump_stacks
runtime_logging := data.framework.runtime_logging
load_fragment := data.framework.load_fragment
scratch_mount := data.framework.scratch_mount
scratch_unmount := data.framework.scratch_unmount

reason := {{"errors": data.framework.errors}}
"""
        )


def policy_deserialize(file_path: str):
    raw_json = opa_eval(Path(file_path), "data.policy")["result"][0]["expressions"][0]["value"]

    raw_fragments = raw_json.pop("fragments", [])
    raw_containers = raw_json.pop("containers", [])

    return Policy(
        fragments=[Fragment(**fragment) for fragment in raw_fragments],
        containers=[Container(**container) for container in raw_containers],
        **raw_json
    )