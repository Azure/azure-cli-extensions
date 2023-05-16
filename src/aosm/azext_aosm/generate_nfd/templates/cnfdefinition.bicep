// Copyright (c) Microsoft Corporation.

// This file creates an NF definition for a VNF
param location string = resourceGroup().location
@description('Name of an existing publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an existing ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of an existing Storage Account-backed Artifact Store, deployed under the publisher.')
param saArtifactStoreName string
@description('Name of an existing Network Function Definition Group')
param nfDefinitionGroup string
@description('The version of the NFDV you want to deploy, in format A-B-C')
param nfDefinitionVersion string
@description('The configuration of the network function applications')
param nfApplicationConfigurations array

// Created by the az aosm definition publish command before the template is deployed
resource publisher 'Microsoft.HybridNetwork/publishers@2022-09-01-preview' existing = {
  name: publisherName
  scope: resourceGroup()
}

// Created by the az aosm definition publish command before the template is deployed
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2022-09-01-preview' existing = {
  parent: publisher
  name: acrArtifactStoreName
}

// Created by the az aosm definition publish command before the template is deployed
resource saArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-04-01-preview' existing = {
  parent: publisher
  name: saArtifactStoreName
}

// Created by the az aosm definition publish command before the template is deployed
resource nfdg 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups@2023-04-01-preview' existing = {
  parent: publisher
  name: nfDefinitionGroup
}

resource nfdv 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups/networkfunctiondefinitionversions@2023-04-01-preview' = {
  parent: nfdg
  name: nfDefinitionVersion
  location: location
  properties: {
    // versionState should be changed to 'Active' once it is finalized.
    versionState: 'Preview'
    deployParameters: string(loadJsonContent('schemas/deploymentParameters.json'))
    networkFunctionType: 'ContainerizedNetworkFunction'
    networkFunctionTemplate: {
      nfviType: 'AzureArcKubernetes'
      networkFunctionApplications: [ for (application, index) in nfApplicationConfigurations: {
          artifactType: 'HelmPackage'
          name: application.name
          dependsOnProfile: application.dependsOnProfile
          artifactProfile: {
            artifactStore: {
              id: acrArtifactStore.id
            }
            helmArtifactProfile: {
              helmPackageName: application.name
              helmPackageVersionRange: application.name
              registryValuesPaths: application.registryValuesPaths
              imagePullSecretsValuesPaths: application.imagePullSecretsValuesPaths
            }
          }
          deployParametersMappingRuleProfile: {
            applicationEnablement: 'Enabled'
            helmMappingRuleProfile: {
              releaseNamespace: application.name
              releaseName: application.name
              helmPackageVersion: application.helmPackageVersion
              values: string(loadFileAsBase64(nfApplicationConfigurations[index].valuesFilePath))
            }
          }
        }
      ]
    }
  }
}
