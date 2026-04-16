extension radius

// Feature: working directory override
// Template field: container.workingDir
// Policy field:   working_dir

param application string

resource container 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'working-dir'
  properties: {
    application: application
    container: {
      image: 'alpine:3.19'
      workingDir: '/app/src'
    }
  }
}
