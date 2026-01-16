# v1 `--input`, `-i` json file format

This document provides a comprehensive reference for the JSON configuration format used by the `confcom` extension's `--input`, `-i` flag.
This schema allows you to define container properties and fragment specifications to be used with `acipolicygen` and `acifragmentgen` including usage with `VN2`.

## Schema Overview

The configuration file uses a structured JSON format with the following main sections:

| Field        | Type    | Required                                      | Description                                                                                   |
|--------------|---------|-----------------------------------------------|-----------------------------------------------------------------------------------------------|
| `version`    | string  | Yes                                           | Policy framework version identifier (currently "1.0")                                                   |
| `scenario`   | string  | No                                            | Adds appropriate mounts and environment variables for different deployment scenarios. If deploying to `vn2`, this field is required |
| `fragments`  | array   | Yes (either `containers` or `fragments` must be defined) | Specifies policy fragments to include                                                          |
| `containers` | array   | Yes (either `containers` or `fragments` must be defined) | Container configurations to deploy                                                             |

## Detailed Field Reference

### Top-Level Fields

#### `version`

- **Type**: String
- **Required**: Yes
- **Description**: Version identifier for the output policy format
- **Allowed Values**: "1.0"
- **Example**: `"version": "1.0"`

#### `scenario`

- **Type**: String
- **Required**: No
- **Description**: Adds appropriate mounts and environment variables for different deployment scenarios.
If deploying to `vn2`, this field is required.
The default value is `aci`
- **Allowed Values**: "vn2", "aci"
- **Example**: `"scenario": "vn2"`

#### `fragments`

- **Type**: Array of objects
- **Required**: Yes (either `containers` or `fragments` must be defined)
- **Description**: Policy fragments that should be included and imported when enforcing the security policy

These objects define all the information necessary for importing and using a fragment.

Each fragment object must include the following fields:

| Field         | Type   | Required | Description                                                          |
|---------------|--------|----------|----------------------------------------------------------------------|
| `issuer`      | string | Yes      | DID identifier of the fragment signer                                |
| `feed`        | string | Yes      | Name for the fragment. Can be its address in a container registry (for standalone fragments) or an arbitrary name (for image-attached fragments)                                             |
| `minimum_svn` | string | Yes      | Minimum Security Version Number required                             |
| `includes`    | array  | Yes      | Variables included in the fragment (e.g., "containers", "fragments") |

**Example**:

```json
{
  "issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
  "feed": "contoso.azurecr.io/infra",
  "minimum_svn": "1",
  "includes": ["containers"]
}
```

#### `containers`

- **Type**: Array of objects
- **Required**: Yes (either `containers` or `fragments` must be defined)
- **Description**: Container specifications for deployment

Container Object Fields

| Field      | Type   | Required | Description                         |
|------------|--------|----------|-------------------------------------|
| name       | string | Yes      | Unique identifier for the container |
| properties | object | Yes      | Container-specific configuration    |

Container `properties` Fields

| Field                | Type   | Required | Description                                                  |
|----------------------|--------|----------|--------------------------------------------------------------|
| image                | string | Yes      | Container image URI                                          |
| execProcesses        | array  | No       | Commands executed within the container (usually from probes) |
| command              | array  | No       | Container startup command                                    |
| volumeMounts         | array  | No       | Volumes mounted into the container                           |
| environmentVariables | array  | No       | Environment variables set within the container               |
| securityContext      | object | No       | Defines privileges associated with the container             |

**Example**:

```json
{
  "containers": [
    {
      "name": "my-container",
      "properties": {
        "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
        "execProcesses": [
          {
            "command": ["echo", "Hello World"]
          }
        ],
        "command": ["python3"],
        "volumeMounts": [
          {
            "name": "azurefile",
            "mountPath": "/aci/logs",
            "mountType": "azureFile",
            "readOnly": true
          }
        ],
        "environmentVariables": [
          {
            "name": "PATH",
            "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
          },
          {
            "name": "NEW_VAR",
            "value": "value.*",
            "regex": true
          }
        ],
        "securityContext": {
          "privileged": false,
          "runAsUser": 1001,
          "runAsGroup": 3001,
          "runAsNonRoot": true,
          "readOnlyRootFilesystem": true,
          "capabilities": {
            "add": ["NET_ADMIN"],
            "drop": ["ALL"]
          }
        }
      }
    }
  ]
}
```

`execProcesses` Object Fields

| Field   | Type  | Required | Description                    |
|---------|-------|----------|--------------------------------|
| command | array | Yes      | Command and arguments to execute|

**Example**:

```json
{
  "command": ["echo", "Hello World"]
}
```

`command` Field

- **Type**: array of strings
- **Required**: No
- **Description**: Command executed at container startup.

**Example**:

```json
"command": ["python3"]
```

`volumeMounts` Object Fields

| Field      | Type    | Required | Description                                             |
|------------|---------|----------|---------------------------------------------------------|
| name       | string  | Yes      | Name of the volume                                      |
| mountPath  | string  | Yes      | Path inside the container where volume is mounted       |
| mountType  | string  | Yes      | Type of volume (`azureFile`, `secret`, `configMap`, `emptyDir`) |
| readOnly   | boolean | No       | Mount volume as read-only (default: false)              |

**Example**:

```json
{
  "name": "azurefile",
  "mountPath": "/aci/logs",
  "mountType": "azureFile",
  "readOnly": true
}
```

`environmentVariables` Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name  | string | Yes | Environment variable name |
| value | string | Yes | Environment variable value |
| regex | boolean | No | Indicates if the value is a regex pattern (default: false) |

**Example**:

```json
[
  {
    "name": "PATH",
    "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  },
  {
    "name": "NEW_VAR",
    "value": "value.*",
    "regex": true
  }
]
```

`securityContext` Object Fields

The `securityContext` field defines security-related settings for a container. These settings control privileges and access controls for the container process. These options are not used in most situations

| Field             | Type    | Required | Description                                                                                 |
|-------------------|---------|----------|---------------------------------------------------------------------------------------------|
| `privileged`      | boolean | No       | If true, the container runs in privileged mode (not recommended for production workloads).  |
| `runAsUser`       | int     | No       | The UID to run the container process as.                                                    |
| `runAsGroup`      | int     | No       | The GID to run the container process as.                                                    |
| `runAsNonRoot`    | boolean | No       | Requires the container to run as a non-root user.                                           |
| `readOnlyRootFilesystem` | boolean | No | If true, mounts the container's root filesystem as read-only.                               |
| `capabilities`    | object  | No       | [Linux capabilities](https://www.man7.org/linux/man-pages/man7/capabilities.7.html) to add or drop (e.g., `add`, `drop` arrays).                             |

**Example**:

```json
"securityContext": {
  "privileged": false,
  "runAsUser": 1001,
  "runAsGroup": 3001,
  "runAsNonRoot": true,
  "readOnlyRootFilesystem": true,
  "capabilities": {
    "add": ["NET_ADMIN"],
    "drop": ["ALL"]
  }
}
```

#### Usage Notes and Best Practices

- Use either command or execProcesses, but not both simultaneously.
- Clearly name containers to reflect their role or function.
- Limit environment variables to essential values; use regex sparingly.
- Mount volumes as read-only whenever possible for enhanced security.
- Keep fragments modular and scoped to specific capabilities.

#### Azure Best Practices

- Store container images securely in Azure Container Registry (ACR).
- Regularly update container images and fragments to patch vulnerabilities.
- Follow the principle of least privilege when defining container capabilities and permissions.
- Use Azure Managed Identities for secure access to Azure resources from containers.

#### Full Example

The most up to date example [can be found here](../../samples/config.json)
