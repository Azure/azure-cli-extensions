
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from dataclasses import asdict
import json
from pathlib import Path
from textwrap import dedent
from typing import Union

from azext_confcom.lib.opa import opa_eval
from azext_confcom.lib.policy import Container, FragmentReference, Fragment, Policy
import re


# This is a single entrypoint for serializing both Policy and Fragment objects
def policy_serialize(policy: Union[Policy, Fragment]):

    if isinstance(policy, Fragment):
        return fragment_serialize(policy)

    policy_dict = asdict(policy)
    fragments_json = json.dumps(policy_dict.pop("fragments"), indent=2)
    containers_json = json.dumps(policy_dict.pop("containers"), indent=2)

    return dedent(f"""
package {policy_dict.pop('package')}

api_version := "{policy_dict.pop('api_version')}"
framework_version := "{policy_dict.pop('framework_version')}"

fragments := {fragments_json}

containers := {containers_json}

{chr(10).join(f"{key} := {str(value).lower()}" for key, value in policy_dict.items() if key.startswith("allow"))}

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
""")


def fragment_serialize(fragment: Fragment):

    fragment_dict = asdict(fragment)
    fragments_json = json.dumps(fragment_dict.pop("fragments"), indent=2)
    containers_json = json.dumps(fragment_dict.pop("containers"), indent=2)

    return dedent(f"""
package {fragment_dict.pop('package')}

svn := "{fragment_dict.pop('svn')}"
framework_version := "{fragment_dict.pop('framework_version')}"

fragments := {fragments_json}

containers := {containers_json}
""")


def policy_deserialize(file_path: str):

    with open(file_path, 'r') as f:
        content = f.read()

    package_match = re.search(r'package\s+(\S+)', content)
    package_name = package_match.group(1)

    PolicyType = Policy if package_name == "policy" else Fragment

    raw_json = opa_eval(Path(file_path), f"data.{package_name}")["result"][0]["expressions"][0]["value"]

    raw_fragments = raw_json.pop("fragments", [])
    raw_containers = raw_json.pop("containers", [])

    return PolicyType(
        package=package_name,
        fragments=[FragmentReference(**fragment) for fragment in raw_fragments],
        containers=[Container(**container) for container in raw_containers],
        **raw_json
    )
