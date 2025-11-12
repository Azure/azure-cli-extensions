# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import Literal, Optional


def get_default_capabilities():
    return [
        "CAP_AUDIT_WRITE",
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_MKNOD",
        "CAP_NET_BIND_SERVICE",
        "CAP_NET_RAW",
        "CAP_SETFCAP",
        "CAP_SETGID",
        "CAP_SETPCAP",
        "CAP_SETUID",
        "CAP_SYS_CHROOT"
    ]


@dataclass
class ContainerCapabilities:
    ambient: list[str] = field(default_factory=list)
    bounding: list[str] = field(default_factory=get_default_capabilities)
    effective: list[str] = field(default_factory=get_default_capabilities)
    inheritable: list[str] = field(default_factory=list)
    permitted: list[str] = field(default_factory=get_default_capabilities)


@dataclass
class ContainerRule:
    pattern: str
    strategy: str
    required: Optional[bool] = False


@dataclass
class ContainerExecProcesses:
    command: list[str]
    signals: Optional[list[str]] = None
    allow_stdio_access: bool = True


@dataclass
class ContainerMount:
    destination: str
    source: str
    type: str
    options: list[str] = field(default_factory=list)


@dataclass
class ContainerUser:
    group_idnames: list[ContainerRule] = field(default_factory=lambda: [ContainerRule(pattern="", strategy="any")])
    umask: str = "0022"
    user_idname: ContainerRule = field(default_factory=lambda: ContainerRule(pattern="", strategy="any"))


@dataclass
class FragmentReference:
    feed: str
    issuer: str
    minimum_svn: str
    includes: list[Literal["containers", "fragments", "namespace", "external_processes"]]
    path: Optional[str] = None


# pylint: disable=too-many-instance-attributes
@dataclass
class Container:
    allow_elevated: bool = False
    allow_stdio_access: bool = True
    capabilities: ContainerCapabilities = field(default_factory=ContainerCapabilities)
    command: Optional[list[str]] = None
    env_rules: list[ContainerRule] = field(default_factory=list)
    exec_processes: list[ContainerExecProcesses] = field(default_factory=list)
    id: Optional[str] = None
    layers: list[str] = field(default_factory=list)
    mounts: list[ContainerMount] = field(default_factory=list)
    name: Optional[str] = None
    no_new_privileges: bool = False
    seccomp_profile_sha256: str = ""
    signals: list[str] = field(default_factory=list)
    user: ContainerUser = field(default_factory=ContainerUser)
    working_dir: str = "/"


# pylint: disable=too-many-instance-attributes
@dataclass
class Policy:
    package: str = "policy"
    api_version: str = "0.10.0"
    framework_version: str = "0.2.3"
    fragments: list[FragmentReference] = field(default_factory=list)
    containers: list[Container] = field(default_factory=list)
    allow_properties_access: bool = True
    allow_dump_stacks: bool = False
    allow_runtime_logging: bool = False
    allow_environment_variable_dropping: bool = True
    allow_unencrypted_scratch: bool = False
    allow_capability_dropping: bool = True


@dataclass
class Fragment:
    package: str = "fragment"
    svn: str = "0"
    framework_version: str = "0.2.3"
    fragments: list[FragmentReference] = field(default_factory=list)
    containers: list[Container] = field(default_factory=list)
