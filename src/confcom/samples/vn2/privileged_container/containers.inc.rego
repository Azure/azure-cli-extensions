[
  {
    "id": "mcr.microsoft.com/azurelinux/distroless/base@sha256:1e77d97e1e39f22ed9c52f49b3508b4c1044cec23743df9098ac44e025f654f2",
    "name": "app",
    "layers": [
      "243e1b3ce08093f2f0d9cd6a9eafde8737f64fec105ed59c346d309fbe760b58"
    ],
    "env_rules": [
      {
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "strategy": "string",
        "required": false
      },
      {
        "name": "TERM",
        "value": "xterm",
        "strategy": "string",
        "required": false
      },
      {
        "name": "(?i)(FABRIC)_.+",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "HOSTNAME",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "T(E)?MP",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "FabricPackageFileName",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "HostedServiceName",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "IDENTITY_API_VERSION",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "IDENTITY_HEADER",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "IDENTITY_SERVER_THUMBPRINT",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "azurecontainerinstance_restarted_by",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_HOST",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_PORT",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_SERVICE_PORT_[A-Z0-9_]+",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_PORT",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PROTO",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PORT",
        "value": ".+",
        "strategy": "re2",
        "required": false
      },
      {
        "name": "[A-Z0-9_]+_PORT_[0-9]+_TCP_ADDR",
        "value": ".+",
        "strategy": "re2",
        "required": false
      }
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
    "command": [],
    "working_dir": "/"
  }
]
