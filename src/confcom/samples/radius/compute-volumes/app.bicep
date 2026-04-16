// Radius.Compute/containers: volumes + probes in the Radius.Compute schema
//   properties.volumes.<name>.emptyDir           → mount (ephemeral)
//   containers.<name>.volumeMounts               → references to properties.volumes
//   containers.<name>.livenessProbe.exec         → exec_processes
extension radius
extension radiusResources

param application string
param environment string

resource app 'Applications.Core/applications@2023-10-01-preview' = {
  name: 'volumes-app'
  properties: {
    environment: environment
  }
}

resource container 'Radius.Compute/containers@2025-08-01-preview' = {
  name: 'worker'
  properties: {
    environment: environment
    application: app.id
    containers: {
      worker: {
        image: 'ghcr.io/radius-project/samples/demo:latest'
        env: {
          LOG_LEVEL: {
            value: 'debug'
          }
        }
        volumeMounts: [
          {
            volumeName: 'scratch'
            mountPath: '/tmp/scratch'
          }
        ]
        livenessProbe: {
          exec: {
            command: [
              'cat'
              '/tmp/scratch/healthy'
            ]
          }
          periodSeconds: 10
        }
      }
    }
    volumes: {
      scratch: {
        emptyDir: {
          medium: 'memory'
        }
      }
    }
  }
}
