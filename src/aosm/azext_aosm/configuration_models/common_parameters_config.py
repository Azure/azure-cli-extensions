# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


# Config is sometimes used as an argument to cached functions. These
# arguments must be hashable, so we need to use frozen dataclasses.
# This is fine because we shouldn't be changing this initial input anyway.
@dataclass(frozen=True)
class BaseCommonParametersConfig(ABC):
    """Base common parameters configuration."""

    location: str
    publisherName: str
    publisherResourceGroupName: str
    acrArtifactStoreName: str
    acrManifestName: str


@dataclass(frozen=True)
class NFDCommonParametersConfig(BaseCommonParametersConfig):
    """Common parameters configuration for NFs."""

    nfDefinitionGroup: str
    nfDefinitionVersion: str


@dataclass(frozen=True)
class CoreVNFCommonParametersConfig(NFDCommonParametersConfig):
    """Common parameters configuration for VNFs."""

    saArtifactStoreName: str
    saManifestName: str


@dataclass(frozen=True)
class NexusVNFCommonParametersConfig(NFDCommonParametersConfig):
    """Common parameters configuration for VNFs."""


@dataclass(frozen=True)
class CNFCommonParametersConfig(NFDCommonParametersConfig):
    """Common parameters configuration for VNFs."""


@dataclass(frozen=True)
class NSDCommonParametersConfig(BaseCommonParametersConfig):
    """Common parameters configuration for NSDs."""

    nsDesignGroup: str
    nsDesignVersion: str
    nfviSiteName: str
