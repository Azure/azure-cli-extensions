from dataclasses import dataclass
from typing import Optional
from typing_extensions import Literal


@dataclass
class AciContainerPropertyEnvVariable:
    name: str
    value: str
    strategy: str
    required: bool = False


@dataclass
class AciContainerPropertyExecProcesses:
    command: list[str]
    signals: Optional[list[str]] = None
    allow_stdio_access: bool = True


@dataclass
class AciContainerPropertyVolumeMounts:
    mountPath: str
    name: Optional[str] = None
    readonly: bool = False
    mountType: Optional[Literal["azureFile", "secret", "configMap", "emptyDir"]] = None


@dataclass
class AciContainerPropertySecurityContextCapabilities:
    add: list[str]
    drop: list[str]


@dataclass
class AciContainerPropertySecurityContext:
    priviledged: bool
    runAsUser: int
    runAsGroup: int
    runAsNonRoot: bool
    readOnlyRootFilesystem: bool
    capabilities: AciContainerPropertySecurityContextCapabilities


@dataclass
class AciContainerProperties():
    image: str
    allowStdioAccess: bool = True
    environmentVariables: Optional[list[AciContainerPropertyEnvVariable]] = None
    execProcesses: Optional[list[AciContainerPropertyExecProcesses]] = None
    volumeMounts: Optional[list[AciContainerPropertyVolumeMounts]] = None
    securityContext: Optional[AciContainerPropertySecurityContext] = None
    command: Optional[list[str]] = None


# ------------------------------------------------------------------------------


@dataclass
class AciFragmentSpec:
    feed: str
    issuer: str
    minimum_svn: str
    includes: list[Literal["containers", "fragments"]]


@dataclass
class AciContainerSpec:
    name: str
    properties: AciContainerProperties


@dataclass
class AciPolicySpec:
    fragments: Optional[list[AciFragmentSpec]]
    containers: Optional[list[AciContainerSpec]]