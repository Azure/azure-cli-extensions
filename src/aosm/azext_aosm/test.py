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

vnf_props = VirtualNetworkFunctionDefinitionVersion(
    version_state=VersionState.PREVIEW,
    deploy_parameters= "TODO",
    network_function_template=AzureCoreNetworkFunctionTemplate(
        network_function_applications= [
            AzureCoreNetworkFunctionVhdApplication(),
            AzureCoreNetworkFunctionArmTemplateApplication()
        ]
))

#test_dict = dict(**vnf_props)
print(vnf_props.__dict__)

nfdv = NetworkFunctionDefinitionVersion(location="uksouth",
                                        #network_function_type="VirtualNetworkFunction",
                                        # Think kwargs map magically to properties in bicep, somehow
                                        **vnf_props.__dict__)

print(nfdv)
