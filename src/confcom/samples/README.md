# Microsoft Azure CLI 'confcom' Extension Samples

## Example Input Configuration

```json
{
    "version": "1.0",
    "containers": [
    {
        "containerImage": "rust:1.52.1",
        "environmentVariables": [
            {
                "name": "PATH",
                "value": "/customized/path/value",
                "strategy": "string"
            },
            {
                "name": "TEST_REGEXP_ENV",
                "value": "test_regexp_env_[[:alpha:]]*",
                "strategy": "re2"
            }
        ],
        "command": ["rustc", "--help"],
        "workingDir": ["/"],
        "mounts": [
            {
                "mountType": "azureFile",
                "mountPath": "path/to/something/in/container",
                "readonly": false
            },
            {
                "mountType": "secret",
                "mountPath": "path/to/something/in/container",
                "readonly": false
            },
            {
                "mountType": "emptyDir",
                "mountPath": "path/to/something/in/container",
                "readonly": false
            }
        ],
        "wait_mount_points": [
            "path/to/something/in/container/blob0",
            "path/to/something/in/container/blob1"
        ],
        "allow_elevated": true
    }
    ]
}
```

## version

This specified the version of the input configuration file format.

## containers

This is a list of containers that will be deployed as part of a confidential container group.

For each container the following items can be configured:

### _containerImage_

The uri of the container image and container tag.

### _environmentVariables_

The allowed environment variables for the container.  There are 2 ways to specify the environment variables:

1. Exact 'string' matching.  With the _string_ strategy the value in the environment variable must exactly match the configured value.

```json
{
    "name": "<environment variable name>",
    "value": "<environment variable value>",
    "strategy": "string"
},
```

2. Regular expression "re2" matching.  For more information see the [re2 guide.](https://github.com/google/re2/wiki/Syntax)<br>

```json
{
    "name": "<environment variable name>",
    "value": "<re2 regular expression>",
    "strategy": "re2"
}
```

With re2 matching any value that matches the re2 expression will be allowed.

```json
    "<environment variable name>=<environment regular expression>"
```

### _command_

The command item configures the allowed start-up command to launch inside the container.  It is a list of strings that make up the final command to run.

### **[Optional]** _workingDir_

The working directory item configures where the working directory where the command is executed.  This is an optional field.  If one is not specified the value is defaulted to the first value found in the following list:

- The _working_dir_ field in the container image.
- Defaults to "/"

### **[Optional]** _mounts_

Specifies the mounts that are allowed inside the container.

```json
    “mounts”: [
        {
            "mountType": "azureFile | secret | emptyDir",
            "mountPath": "path/to/something/in/container",
            "readonly": "true | false" # Optional
        }
    ]
```

- _mountType_ - Specifies the type of the Azure mount.  There are 3 types of Azure mounts that are supported.  These mount should match with the mounts that are configured when deploying the container group.
    1. **azureFile** - This mount type corresponds to an [Azure file volume](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-volume-azure-files) mount.
    2. **secret** - This mount type corresponds to an [Azure secret volume](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-volume-secret).
    3. **emptyDir** - This mount type corresponds to an [Azure emptyDir volume](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-volume-emptydir)

- _mountPath_ - Specifies the container path for the corresponding mount.
- _readonly_ - Specifies whether the volume is read-only or writable.  Defaults to false.

### _wait_mount_points_

This configuration item list of container paths for different mounts that should exists before the command execution starts.  If a mount does not exist, the container will not start to run.

```json
        "wait_mount_points": [
            "path/to/something/in/container/blob0",
            "path/to/something/in/container/blob1"
        ]
```

### **[Optional]** _allow_elevated_

By default, “/sys” and “/sys/fs/cgroup” mounts are added as “ro”, by setting "allow_elevated" to true, those mounts are added as “rw”. This is an optional field.  If one is not specified the value is defaulted to false.

---

## sample-template-output.json

This file shows the changes that are made to an input ARM Template when the `--inject-policy` argument is supplied.
