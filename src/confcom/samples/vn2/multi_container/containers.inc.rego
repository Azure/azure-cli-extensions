[
  {
    "command": [],
    "env_rules": [
      {
        "name": "APP_MODE",
        "required": false,
        "strategy": "string",
        "value": "production"
      },
      {
        "name": "PATH",
        "required": false,
        "strategy": "string",
        "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
      },
      {
        "name": "TERM",
        "required": false,
        "strategy": "string",
        "value": "xterm"
      },
      {
        "name": "(?i)(FABRIC)_.+",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "HOSTNAME",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "T(E)?MP",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "FabricPackageFileName",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "HostedServiceName",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "IDENTITY_API_VERSION",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "IDENTITY_HEADER",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "IDENTITY_SERVER_THUMBPRINT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "azurecontainerinstance_restarted_by",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_HOST",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_PORT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_PORT_[A-Z0-9_]+",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PROTO",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PORT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_ADDR",
        "required": false,
        "strategy": "re2",
        "value": ".+"
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
  },
  {
    "command": [
      "/bin/sh",
      "-c",
      "echo worker"
    ],
    "env_rules": [
      {
        "name": "PATH",
        "required": false,
        "strategy": "string",
        "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
      },
      {
        "name": "TERM",
        "required": false,
        "strategy": "string",
        "value": "xterm"
      },
      {
        "name": "(?i)(FABRIC)_.+",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "HOSTNAME",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "T(E)?MP",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "FabricPackageFileName",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "HostedServiceName",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "IDENTITY_API_VERSION",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "IDENTITY_HEADER",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "IDENTITY_SERVER_THUMBPRINT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "azurecontainerinstance_restarted_by",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_HOST",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_PORT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_PORT_[A-Z0-9_]+",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PROTO",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PORT",
        "required": false,
        "strategy": "re2",
        "value": ".+"
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_ADDR",
        "required": false,
        "strategy": "re2",
        "value": ".+"
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
    "name": "worker",
    "working_dir": "/"
  }
]
