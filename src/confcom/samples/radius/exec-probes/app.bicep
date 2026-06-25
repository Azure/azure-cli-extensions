extension radius

// Feature: exec health probes
// Template fields: container.livenessProbe (kind=exec), container.readinessProbe (kind=exec)
// Policy field:    exec_processes

param application string

resource container 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'exec-probes'
  properties: {
    application: application
    container: {
      image: 'alpine:3.19'
      livenessProbe: {
        kind: 'exec'
        command: 'cat /tmp/healthy'
      }
      readinessProbe: {
        kind: 'exec'
        command: 'cat /tmp/ready'
      }
    }
  }
}
