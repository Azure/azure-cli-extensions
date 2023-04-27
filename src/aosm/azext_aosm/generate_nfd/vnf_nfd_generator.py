# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains a class for generating VNF NFDs and associated resources."""
from knack.log import get_logger

from azext_aosm.generate_nfd.nfd_generator_base import NFDGenerator
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.vendored_sdks.models import (
    NetworkFunctionDefinitionVersion, 
    NetworkFunctionDefinitionGroup, 
    ArtifactManifest, 
    ManifestArtifactFormat, 
    VersionState, 
    NetworkFunctionType,
    NFVIType,
    ArtifactType,
    VirtualNetworkFunctionDefinitionVersion, # this is actually properties, badly named
    AzureCoreNetworkFunctionTemplate,
    AzureCoreNetworkFunctionVhdApplication,
    AzureCoreNetworkFunctionArmTemplateApplication
)

from azext_aosm._configuration import VNFConfiguration
from azext_aosm.publisher_resources.publisher_resources import PublisherResourceGenerator


logger = get_logger(__name__)

class VnfNfdGenerator(NFDGenerator):
    """_summary_

    :param NFDGenerator: _description_
    :type NFDGenerator: _type_
    """
    def __init__(
        self,
        config: VNFConfiguration
    ):
        super(NFDGenerator, self).__init__(
            config=config,
        )    
        
    def generate_nfd(self) -> None:
        """Generate a VNF NFD which comprises an group, an Artifact Manifest and a NFDV.
        """
        assert isinstance(self.config, VNFConfiguration)
        arty_manny_sa = ArtifactManifest(location=self.config.location,
                                      #tags={"blah": "blah"},
                                      artifacts=[ManifestArtifactFormat(artifact_name=self.config.vhd.artifact_name,
                                                                        artifact_type=ArtifactType.VHD_IMAGE_FILE,
                                                                        artifact_version=self.config.vhd.version)])
        
        arty_manny_acr = ArtifactManifest(location=self.config.location,
                                      #tags={"blah": "blah"},
                                      artifacts=[ManifestArtifactFormat(artifact_name=self.config.arm_template.artifact_name,
                                                                        artifact_type=ArtifactType.ARM_TEMPLATE,
                                                                        artifact_version=self.config.arm_template.version)])
        common_generator = PublisherResourceGenerator(config=self.config)
        nfdg: NetworkFunctionDefinitionGroup = common_generator.generate_nfd_group()
        
        
    def _generate_nfdv(self) -> NetworkFunctionDefinitionVersion:
        """Generate an NFDV for a VNF

        :return: _description_
        :rtype: NetworkFunctionDefinitionVersion
        """
        
        vnf_props = VirtualNetworkFunctionDefinitionVersion(
            version_state=VersionState.PREVIEW,
            deploy_parameters= "TODO",
            network_function_femplate=AzureCoreNetworkFunctionTemplate(
                network_function_applications= [
                    AzureCoreNetworkFunctionVhdApplication(),
                    AzureCoreNetworkFunctionArmTemplateApplication()
                ]
        ))
        
        nfdv = NetworkFunctionDefinitionVersion(location=self.config.location,
                                                # Think kwargs map magically to properties in bicep, somehow                                                
                                                kwargs=vnf_props)
        
        return nfdv
        

        
        
