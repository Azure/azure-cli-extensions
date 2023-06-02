// Copyright (c) Microsoft Corporation. All rights reserved.
// Highly Confidential Material
//
// The template that the NSD invokes to create the Network Function from a published NFDV. 

@description('Publisher where the NFD is published')
param publisherName string = '{{publisher_name}}'

@description('NFD Group name for the Network Function')
param networkFunctionDefinitionGroupName string = '{{network_function_definition_group_name}}'

@description('NFD version')
param networkFunctionDefinitionVersion string = '{{network_function_definition_version_name}}'

@description('Offering location for the Network Function')
param networkFunctionDefinitionOfferingLocation string = '{{network_function_definition_offering_location}}'

param location string = '{{location}}'

param resourceGroupId string = resourceGroup().id

{{bicep_params}}

var deploymentValues = {
  {{deploymentValues}}
}

resource nf_resource 'Microsoft.HybridNetwork/networkFunctions@2023-04-01-preview' = {
  name: '{{network_function_name}}'
  location: location
  properties: {
    publisherName: publisherName
    publisherScope: 'Private'
    networkFunctionDefinitionGroupName: networkFunctionDefinitionGroupName
    networkFunctionDefinitionVersion: networkFunctionDefinitionVersion
    networkFunctionDefinitionOfferingLocation: networkFunctionDefinitionOfferingLocation
    nfviType: 'AzureCore'
    nfviId: resourceGroupId
    allowSoftwareUpdate: true
    deploymentValues: string(deploymentValues)
  }
}
