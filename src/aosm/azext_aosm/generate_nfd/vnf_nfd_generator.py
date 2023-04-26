# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""
from typing import Dict, Any
from .nfd_generator_base import NFDGenerator
from knack.log import get_logger
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.vendored_sdks.models import Publisher, NetworkFunctionDefinitionVersion, NetworkFunctionDefinitionGroup, ArtifactManifest, ManifestArtifactFormat
from azext_aosm._constants import VHD_ARTIFACT, ARM_TEMPLATE_ARTIFACT


logger = get_logger(__name__)

class VnfNfdGenerator(NFDGenerator):
    """_summary_

    :param NFDGenerator: _description_
    :type NFDGenerator: _type_
    """
    def __init__(
        self,
        config: Dict[Any, Any]
    ):
        super(NFDGenerator, self).__init__(
            config=config,
        )
        
    def generate_nfd(self) -> None:
        """Generate a VNF NFD which comprises an group, an Artifact Manifest and a NFDV.
        """
        arty_manny_sa = ArtifactManifest(location="blah",
                                      tags={"blah": "blah"},
                                      artifacts=[ManifestArtifactFormat(artifact_name="blah",
                                                                        artifact_type=VHD_ARTIFACT,
                                                                        artifact_version="blah")])
        
        arty_manny_acr = ArtifactManifest(location="blah",
                                      tags={"blah": "blah"},
                                      artifacts=[ManifestArtifactFormat(artifact_name="blah",
                                                                        artifact_type=ARM_TEMPLATE_ARTIFACT,
                                                                        artifact_version="blah")])
                        
                
        
        
