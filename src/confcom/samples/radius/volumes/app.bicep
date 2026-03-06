extension radius

// Feature: volume mounts (ephemeral + persistent)
// Template fields: container.volumes[].kind, .mountPath, .source, .permission
// Policy field:    mounts

param application string

resource container 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'volumes'
  properties: {
    application: application
    container: {
      image: 'alpine:3.19'
      volumes: {
        scratch: {
          kind: 'ephemeral'
          mountPath: '/tmp/scratch'
          managedStore: 'memory'
        }
        data: {
          kind: 'persistent'
          mountPath: '/data'
          source: 'volume.id'
          permission: 'write'
        }
        config: {
          kind: 'persistent'
          mountPath: '/config'
          source: 'configvol.id'
        }
      }
    }
  }
}
