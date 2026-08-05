[
  {
    "id": "mcr.microsoft.com/azurelinux/distroless/base@sha256:1e77d97e1e39f22ed9c52f49b3508b4c1044cec23743df9098ac44e025f654f2",
    "name": "app",
    "layers": [
      "243e1b3ce08093f2f0d9cd6a9eafde8737f64fec105ed59c346d309fbe760b58"
    ],
    "platform": "linux/amd64",
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
    "env_rules": [
      {
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "strategy": "string",
        "required": false
      },
      {
        "pattern": "TERM=xterm",
        "strategy": "string",
        "required": false
      },
      {
        "pattern": "(?i)(FABRIC)_.+=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "HOSTNAME=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "T(E)?MP=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "FabricPackageFileName=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "HostedServiceName=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "IDENTITY_API_VERSION=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "IDENTITY_HEADER=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "IDENTITY_SERVER_THUMBPRINT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "azurecontainerinstance_restarted_by=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_SERVICE_HOST=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_SERVICE_PORT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_SERVICE_PORT_[A-Z0-9_]+=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PROTO=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PORT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_ADDR=.+",
        "strategy": "re2",
        "required": false
      }
    ],
    "working_dir": "/",
    "command": [
      "/bin/sh",
      "-c",
      "sleep 3600"
    ],
    "exec_processes": [
      {
        "command": [
          "cat",
          "/tmp/healthy"
        ],
        "signals": []
      },
      {
        "command": [
          "cat",
          "/tmp/ready"
        ],
        "signals": []
      },
      {
        "command": [
          "cat",
          "/tmp/started"
        ],
        "signals": []
      },
      {
        "command": [
          "echo",
          "started"
        ],
        "signals": []
      },
      {
        "command": [
          "echo",
          "stopping"
        ],
        "signals": []
      }
    ]
  },
  {
    "id": "mcr.microsoft.com/azurelinux/distroless/base@sha256:1e77d97e1e39f22ed9c52f49b3508b4c1044cec23743df9098ac44e025f654f2",
    "name": "init-setup",
    "layers": [
      "243e1b3ce08093f2f0d9cd6a9eafde8737f64fec105ed59c346d309fbe760b58"
    ],
    "platform": "linux/amd64",
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
    "env_rules": [
      {
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "strategy": "string",
        "required": false
      },
      {
        "pattern": "TERM=xterm",
        "strategy": "string",
        "required": false
      },
      {
        "pattern": "(?i)(FABRIC)_.+=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "HOSTNAME=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "T(E)?MP=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "FabricPackageFileName=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "HostedServiceName=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "IDENTITY_API_VERSION=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "IDENTITY_HEADER=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "IDENTITY_SERVER_THUMBPRINT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "azurecontainerinstance_restarted_by=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_SERVICE_HOST=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_SERVICE_PORT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_SERVICE_PORT_[A-Z0-9_]+=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PROTO=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PORT=.+",
        "strategy": "re2",
        "required": false
      },
      {
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_ADDR=.+",
        "strategy": "re2",
        "required": false
      }
    ],
    "working_dir": "/",
    "command": [
      "/bin/sh",
      "-c",
      "echo init"
    ]
  }
]
