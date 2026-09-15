
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re

from dataclasses import asdict
from textwrap import dedent
from typing import Union

from azext_confcom.lib.policy import Container, FragmentReference, Fragment, Policy


COMMON_ENFORCEMENT_POINTS = (
    "mount_device",
    "unmount_device",
    "mount_overlay",
    "unmount_overlay",
    "create_container",
    "exec_in_container",
    "exec_external",
    "shutdown_container",
    "signal_container_process",
    "plan9_mount",
    "plan9_unmount",
    "get_properties",
    "dump_stacks",
    "runtime_logging",
    "load_fragment",
    "scratch_mount",
    "scratch_unmount",
    "rw_mount_device",
)

PRERELEASE_COMMON_ENFORCEMENT_POINTS = (
    "host_network",
    "load_transparency_trust_list",
)

WINDOWS_ENFORCEMENT_POINTS = (
    "log_provider",
    "registry_changes",
    "mount_cims",
)

PRERELEASE_WINDOWS_ENFORCEMENT_POINTS = (
    "unmount_cims",
    "mapped_directory_mount",
    "mapped_directory_unmount",
)

WINDOWS_POLICY_VALUES = (
    "allow_log_provider_dropping",
    "allow_registry_changes_dropping",
    "allowed_log_providers",
)


def _api_version_at_least(version: str, minimum: str) -> bool:
    return tuple(int(part) for part in version.split(".")) >= tuple(
        int(part) for part in minimum.split(".")
    )


# This is a single entrypoint for serializing both Policy and Fragment objects
def policy_serialize(policy: Union[Policy, Fragment]):

    if isinstance(policy, Fragment):
        return fragment_serialize(policy)

    policy_dict = asdict(policy)
    fragments_json = json.dumps(policy_dict.pop("fragments"), indent=2)
    containers_json = json.dumps(policy_dict.pop("containers"), indent=2)
    is_windows = policy_dict.pop("is_windows")
    policy_values = "\n".join(
        f"{key} := {json.dumps(value, indent=2)}"
        for key, value in policy_dict.items()
        if key.startswith("allow")
        and (is_windows or key not in WINDOWS_POLICY_VALUES)
    )
    enforcement_points = COMMON_ENFORCEMENT_POINTS
    if _api_version_at_least(policy_dict["api_version"], "0.12.0"):
        enforcement_points += PRERELEASE_COMMON_ENFORCEMENT_POINTS
    if is_windows:
        enforcement_points += WINDOWS_ENFORCEMENT_POINTS
        if _api_version_at_least(policy_dict["api_version"], "0.12.0"):
            enforcement_points += PRERELEASE_WINDOWS_ENFORCEMENT_POINTS
    enforcement_bindings = "\n".join(
        f"{name} := data.framework.{name}" for name in enforcement_points
    )

    return dedent(f"""
package {policy_dict.pop('package')}

api_version := "{policy_dict.pop('api_version')}"
framework_version := "{policy_dict.pop('framework_version')}"

fragments := {fragments_json}

containers := {containers_json}

{policy_values}

{enforcement_bindings}

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
        content = f.readlines()

    def _brace_delta(line: str) -> int:
        delta = 0
        for char in line:
            if char in ['{', '[', '(']:
                delta += 1
            elif char in ['}', ']', ')']:
                delta -= 1
        return delta

    policy_json = {}
    is_windows = False
    line_idx = 0

    while line_idx < len(content):
        line = content[line_idx]

        packages_search = re.search(r'package\s+(\S+)', line)
        if packages_search:
            policy_json["package"] = packages_search.group(1)
            line_idx += 1
            continue

        assignment = re.match(r"\s*(?P<name>[A-Za-z0-9_]+)\s*:=\s*(?P<expr>.*)", line)
        if assignment:
            name = assignment.group('name')
            if name == "mount_cims":
                is_windows = True
            expr = assignment.group('expr').strip()
            expr_parts = [expr]
            depth = _brace_delta(expr)

            while depth > 0 and line_idx + 1 < len(content):
                line_idx += 1
                continuation = content[line_idx].strip()
                expr_parts.append(continuation)
                depth += _brace_delta(continuation)

            full_expr = "\n".join(expr_parts).strip().rstrip(",")
            try:
                policy_json[name] = json.loads(full_expr)
            except json.JSONDecodeError:
                # Skip non-literal expressions (e.g. data.framework bindings)
                ...

        line_idx += 1

    PolicyType = Policy if policy_json.get("package") == "policy" else Fragment

    raw_fragments = policy_json.pop("fragments", [])
    raw_containers = policy_json.pop("containers", [])

    if PolicyType is Policy:
        policy_json["is_windows"] = is_windows

    return PolicyType(
        **policy_json,
        fragments=[FragmentReference(**fragment) for fragment in raw_fragments],
        containers=[Container(**container) for container in raw_containers],
    )
