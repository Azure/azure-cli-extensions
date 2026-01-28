[
  {
    "command": [],
    "env_rules": [
      {
        "required": false,
        "strategy": "string",
        "pattern": "FROM_CONFIG=value-one"
      },
      {
        "required": false,
        "strategy": "string",
        "pattern": "FROM_BINARY_CONFIG=value-binary"
      },
      {
        "required": false,
        "strategy": "string",
        "pattern": "FROM_SECRET=value-secret"
      },
      {
        "required": false,
        "strategy": "string",
        "pattern": "FROM_STRINGDATA=value-plain"
      },
      {
        "required": false,
        "strategy": "string",
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
      },
      {
        "required": false,
        "strategy": "string",
        "pattern": "TERM=xterm"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "(?i)(FABRIC)_.+=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "HOSTNAME=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "T(E)?MP=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "FabricPackageFileName=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "HostedServiceName=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "IDENTITY_API_VERSION=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "IDENTITY_HEADER=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "IDENTITY_SERVER_THUMBPRINT=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "azurecontainerinstance_restarted_by=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_SERVICE_HOST=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_SERVICE_PORT=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_SERVICE_PORT_[A-Z0-9_]+=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_PORT=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PROTO=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PORT=.+"
      },
      {
        "required": false,
        "strategy": "re2",
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_ADDR=.+"
      }
    ],
    "id": "mcr.microsoft.com/azurelinux/distroless/base@sha256:1e77d97e1e39f22ed9c52f49b3508b4c1044cec23743df9098ac44e025f654f2",
    "layers": [
      "243e1b3ce08093f2f0d9cd6a9eafde8737f64fec105ed59c346d309fbe760b58"
    ],
    "mounts": [
      {
        "destination": "/etc/resolv.conf",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/var/run/secrets/kubernetes.io/serviceaccount",
        "options": [
          "rbind",
          "rshared",
          "ro"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/etc/hosts",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/dev/termination-log",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/etc/hostname",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      }
    ],
    "name": "app",
    "working_dir": "/"
  }
]
