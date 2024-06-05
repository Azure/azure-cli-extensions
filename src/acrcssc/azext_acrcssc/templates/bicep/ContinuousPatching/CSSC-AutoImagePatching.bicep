param AcrName string
param AcrLocation string = resourceGroup().location

var taskContextPath='https://github.com/pwalecha/ACR-CSSC.git#csscworkflow'
var imagePatching='ACR-CSSC\\ContinuousPatching\\CSSCPatchImage.yaml'
var imageScanning='ACR-CSSC\\ContinuousPatching\\CSSCScanImageAndScedulePatch.yaml'
var repoPatching='ACR-CSSC\\ContinuousPatching\\CSSCScanRepoAndScedulePatch.yaml'
var registryPatching='ACR-CSSC\\ContinuousPatching\\CSSCScanRegistryAndScedulePatch.yaml'

resource contributorRoleDefinition 'Microsoft.Authorization/roleDefinitions@2018-01-01-preview' existing = {
  scope: subscription()
  name: 'b24988ac-6180-42a0-ab88-20f7382dd24c'
}

resource acr 'Microsoft.ContainerRegistry/registries@2019-05-01' existing = {
  name: AcrName
}

resource CSSCPatchImage 'Microsoft.ContainerRegistry/registries/tasks@2019-06-01-preview' = {
  name: 'CSSC-PatchImage'
  location: AcrLocation
  parent: acr
  tags:{
    cssc: 'true'
    clienttracking: 'true'
  }
  properties: {
    platform: {
      os: 'linux'
      architecture: 'amd64'
    }
    agentConfiguration: {
      cpu: 2
    }
    timeout: 3600
    step: {
      type: 'FileTask'
      contextPath: taskContextPath
      taskFilePath: imagePatching
    }
    isSystemTask: false
  }
}

resource CSSCImageScaning 'Microsoft.ContainerRegistry/registries/tasks@2019-06-01-preview' = {
  name: 'CSSC-ScanImageAndSchedulePatch'
  location: AcrLocation
  parent: acr
  identity: {
    type: 'SystemAssigned'
  }
  tags:{
    cssc: 'true'
  }
  properties: {
    platform: {
      os: 'linux'
      architecture: 'amd64'
    }
    agentConfiguration: {
      cpu: 2
    }
    timeout: 3600
    step: {
      type: 'FileTask'
      contextPath: taskContextPath
      taskFilePath: imageScanning
    }
    isSystemTask: false
  }
}


resource roleAssignmentCSSCImageScaning 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: acr
  name: guid(CSSCImageScaning.id, contributorRoleDefinition.id)
  properties: {
    roleDefinitionId: contributorRoleDefinition.id
    principalId: CSSCImageScaning.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource CSSCRepoScaning 'Microsoft.ContainerRegistry/registries/tasks@2019-06-01-preview' = {
  name: 'CSSC-ScanRepoAndSchedulePatch'
  location: AcrLocation
  parent: acr
  identity: {
    type: 'SystemAssigned'
  }
  tags:{
    cssc: 'true'
  }
  properties: {
    platform: {
      os: 'linux'
      architecture: 'amd64'
    }
    agentConfiguration: {
      cpu: 2
    }
    timeout: 3600
    step: {
      type: 'FileTask'
      contextPath: taskContextPath
      taskFilePath: repoPatching
    }
    isSystemTask: false
  }
}

resource roleAssignmentCSSCRepoScaning 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: acr
  name: guid(CSSCRepoScaning.id, contributorRoleDefinition.id)
  properties: {
    roleDefinitionId: contributorRoleDefinition.id
    principalId: CSSCRepoScaning.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource CSSCRegistryScaning 'Microsoft.ContainerRegistry/registries/tasks@2019-06-01-preview' = {
  name: 'CSSC-ScanRegistryAndSchedulePatch'
  location: AcrLocation
  parent: acr
  identity: {
    type: 'SystemAssigned'
  }
  tags:{
    cssc: 'true'
    clienttracking: 'true'
  }
  properties: {
    platform: {
      os: 'linux'
      architecture: 'amd64'
    }
    agentConfiguration: {
      cpu: 2
    }
    timeout: 3600
    status: 'Enabled'
    step: {
      type: 'FileTask'
      contextPath: taskContextPath
      taskFilePath: registryPatching
    }
    isSystemTask: false
    trigger:{
      timerTriggers:[
        {
          name:'daily'
          schedule:'0 12 * * *'
        }
      ]
    }
  }
}

resource roleAssignmentCSSCRegistryScaning 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: acr
  name: guid(CSSCRegistryScaning.id, contributorRoleDefinition.id)
  properties: {
    roleDefinitionId: contributorRoleDefinition.id
    principalId: CSSCRegistryScaning.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
