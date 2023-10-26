// Copyright (c) Microsoft Corporation. All rights reserved.
// Highly Confidential Material
//
// Bicep template to create an Artifact Manifest, Config Group Schema and NSDV.
//
// Requires an existing NFDV from which the values will be populated.

param location string
@description('Name of an existing publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an existing ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of an existing Network Service Design Group')
param nsDesignGroup string
@description('The version of the NSDV you want to create, in format A.B.C')
param nsDesignVersion string
@description('Name of the nfvi site')
param nfviSiteName string = 'ubuntu_NFVI'

// The publisher resource is the top level AOSM resource under which all other designer resources
// are created.
resource publisher 'Microsoft.HybridNetwork/publishers@2023-09-01' existing = {
  name: publisherName
  scope: resourceGroup()
}

// The artifact store is the resource in which all the artifacts required to deploy the NF are stored.
// The artifact store is created by the az aosm CLI before this template is deployed.
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-09-01' existing = {
  parent: publisher
  name: acrArtifactStoreName
}

// Created up-front, the NSD Group is the parent resource under which all NSD versions will be created.
resource nsdGroup 'Microsoft.Hybridnetwork/publishers/networkservicedesigngroups@2023-09-01' existing = {
  parent: publisher
  name: nsDesignGroup
}

// The configuration group schema defines the configuration required to deploy the NSD. The NSD references this object in the
// `configurationgroupsSchemaReferences` and references the values in the schema in the `parameterValues`.
// The operator will create a config group values object that will satisfy this schema.
resource cgSchema 'Microsoft.Hybridnetwork/publishers/configurationGroupSchemas@2023-09-01' = {
  parent: publisher
  name: 'ubuntu_ConfigGroupSchema'
  location: location
  properties: {
    schemaDefinition: string(loadJsonContent('schemas/ubuntu_ConfigGroupSchema.json'))
  }
}

// The NSD version
resource nsdVersion 'Microsoft.Hybridnetwork/publishers/networkservicedesigngroups/networkservicedesignversions@2023-09-01' = {
  parent: nsdGroup
  name: nsDesignVersion
  location: location
  properties: {
    description: 'Plain ubuntu VM'
    // The version state can be Preview, Active or Deprecated.
    // Once in an Active state, the NSDV becomes immutable.
    versionState: 'Preview'
    // The `configurationgroupsSchemaReferences` field contains references to the schemas required to
    // be filled out to configure this NSD.
    configurationGroupSchemaReferences: {
      ubuntu_ConfigGroupSchema: {
        id: cgSchema.id
      }
    }
    // This details the NFVIs that should be available in the Site object created by the operator.
    nfvisFromSite: {
      nfvi1: {
        name: nfviSiteName
        type: 'AzureCore'
      }
    }
    // This field lists the templates that will be deployed by AOSM and the config mappings
    // to the values in the CG schemas.
    resourceElementTemplates: [
      {
        name: 'ubuntu-vm-nfdg_nf_artifact_resource_element'
        // The type of resource element can be ArmResourceDefinition, ConfigurationDefinition or NetworkFunctionDefinition.
        type: 'NetworkFunctionDefinition'
        // The configuration object may be different for different types of resource element.
        configuration: {
          // This field points AOSM at the artifact in the artifact store.
          artifactProfile: {
            artifactStoreReference: {
              id: acrArtifactStore.id
            }
            artifactName: 'ubuntu-vm-nfdg_nf_artifact'
            artifactVersion: '1.0.0'
          }
          templateType: 'ArmTemplate'
          // The parameter values map values from the CG schema, to values required by the template
          // deployed by this resource element.
          parameterValues: string(loadJsonContent('configMappings/ubuntu-vm-nfdg_config_mapping.json'))
        }
        dependsOnProfile: {
          installDependsOn: []
          uninstallDependsOn: []
          updateDependsOn: []
        }
      }
    ]
  }
}