# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Literal, Optional, List
from azext_confcom.lib.orderless_dataclasses import dataclass, OrderlessField, Field


def get_default_capabilities():
    return (
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
    )


@dataclass
class ContainerCapabilities:
    ambient: List[str] = OrderlessField(default_factory=list)
    bounding: List[str] = OrderlessField(default_factory=get_default_capabilities)
    effective: List[str] = OrderlessField(default_factory=get_default_capabilities)
    inheritable: List[str] = OrderlessField(default_factory=list)
    permitted: List[str] = OrderlessField(default_factory=get_default_capabilities)


@dataclass
class ContainerRule:
    pattern: str
    strategy: str
    required: Optional[bool] = False


@dataclass
class ContainerExecProcesses:
    command: List[str]
    signals: Optional[List[str]] = OrderlessField(default=None)
    allow_stdio_access: bool = True


@dataclass()
class ContainerMount:
    destination: str
    source: str
    type: str
    options: List[str] = OrderlessField(default_factory=list)


@dataclass
class ContainerUser:
    group_idnames: List[ContainerRule] = \
        OrderlessField(default_factory=lambda: [ContainerRule(pattern="", strategy="any")])
    umask: str = "0022"
    user_idname: ContainerRule = \
        Field(default_factory=lambda: ContainerRule(pattern="", strategy="any"))


@dataclass
class FragmentReference:
    feed: str
    issuer: str
    minimum_svn: str
    includes: List[Literal["containers", "fragments", "namespace", "external_processes"]] = \
        OrderlessField(default_factory=list)
    path: Optional[str] = None


# pylint: disable=too-many-instance-attributes
@dataclass
class Container:
    allow_elevated: bool = False
    allow_stdio_access: bool = True
    capabilities: ContainerCapabilities = Field(default_factory=ContainerCapabilities)
    command: Optional[List[str]] = None
    env_rules: List[ContainerRule] = OrderlessField(default_factory=list)
    exec_processes: List[ContainerExecProcesses] = OrderlessField(default_factory=list)
    id: Optional[str] = None
    layers: List[str] = Field(default_factory=list)
    mounts: List[ContainerMount] = OrderlessField(default_factory=list)
    name: Optional[str] = None
    no_new_privileges: bool = False
    seccomp_profile_sha256: str = ""
    signals: List[str] = OrderlessField(default_factory=list)
    user: ContainerUser = Field(default_factory=ContainerUser)
    working_dir: str = "/"


# pylint: disable=too-many-instance-attributes
@dataclass
class Policy:
    package: str = "policy"
    api_version: str = "0.10.0"
    framework_version: str = "0.2.3"
    fragments: List[FragmentReference] = OrderlessField(default_factory=list)
    containers: List[Container] = OrderlessField(default_factory=list)
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
    fragments: List[FragmentReference] = OrderlessField(default_factory=list)
    containers: List[Container] = OrderlessField(default_factory=list)
