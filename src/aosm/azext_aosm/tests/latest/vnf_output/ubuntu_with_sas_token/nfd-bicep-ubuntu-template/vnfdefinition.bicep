// Copyright (c) Microsoft Corporation.

// This file creates an NF definition for a VNF
param location string
@description('Name of an existing publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an existing ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of an existing Storage Account-backed Artifact Store, deployed under the publisher.')
param saArtifactStoreName string
@description('Name of Network Function. Used predominantly as a prefix for other variable names')
param nfName string
@description('Name of an existing Network Function Definition Group')
param nfDefinitionGroup string
@description('The version of the NFDV you want to deploy, in format A.B.C')
param nfDefinitionVersion string
@description('The version that you want to name the NFM VHD artifact, in format A-B-C. e.g. 6-13-0')
param vhdVersion string
@description('The version that you want to name the NFM template artifact, in format A.B.C. e.g. 6.13.0. If testing for development, you can use any numbers you like.')
param armTemplateVersion string

// Created by the az aosm definition publish command before the template is deployed
resource publisher 'Microsoft.HybridNetwork/publishers@2023-09-01' existing = {
  name: publisherName
  scope: resourceGroup()
}

// Created by the az aosm definition publish command before the template is deployed
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-09-01' existing = {
  parent: publisher
  name: acrArtifactStoreName
}

// Created by the az aosm definition publish command before the template is deployed
resource saArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-09-01' existing = {
  parent: publisher
  name: saArtifactStoreName
}

// Created by the az aosm definition publish command before the template is deployed
resource nfdg 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups@2023-09-01' existing = {
  parent: publisher
  name: nfDefinitionGroup
}

resource nfdv 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups/networkfunctiondefinitionversions@2023-09-01' = {
  parent: nfdg
  name: nfDefinitionVersion
  location: location
  properties: {
    // versionState should be changed to 'Active' once it is finalized.
    versionState: 'Preview'
    deployParameters: string(loadJsonContent('schemas/deploymentParameters.json'))
    networkFunctionType: 'VirtualNetworkFunction'
    networkFunctionTemplate: {
      nfviType: 'AzureCore'
      networkFunctionApplications: [
        {
          artifactType: 'VhdImageFile'
          name: '${nfName}Image'
          dependsOnProfile: null
          artifactProfile: {
            vhdArtifactProfile: {
              vhdName: '${nfName}-vhd'
              vhdVersion: vhdVersion
            }
            artifactStore: {
              id: saArtifactStore.id
            }
          }
          // mapping deploy param vals to vals required by this network function application object
          deployParametersMappingRuleProfile: {
            vhdImageMappingRuleProfile: {
              userConfiguration: string(loadJsonContent('configMappings/vhdParameters.json'))
            }
            // ??
            applicationEnablement: 'Unknown'
          }
        }
        {
          artifactType: 'ArmTemplate'
          name: nfName
          dependsOnProfile: null
          artifactProfile: {
            templateArtifactProfile: {
              templateName: '${nfName}-arm-template'
              templateVersion: armTemplateVersion
            }
            artifactStore: {
              id: acrArtifactStore.id
            }
          }
          deployParametersMappingRuleProfile: {
            templateMappingRuleProfile: {
              templateParameters: string(loadJsonContent('configMappings/templateParameters.json'))
            }
            applicationEnablement: 'Unknown'
          }
        }
      ]
    }
  }
}
