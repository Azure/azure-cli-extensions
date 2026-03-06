[
  {
    "id": "mcr.microsoft.com/azurelinux/base/nginx:1@sha256:6b8ca92221f842cd3e1ea3f863a324221cc5cf9e54f47dc76092d9582e0a1807",
    "name": "app",
    "layers": [
      "a189b02d4858578459fda1dfbd7c6a4557c44208b9829e02b931771a6d611c39",
      "66e9ff28ccda836e7eb180b82db793c6b6cbcd9005a06a961744f26abdc5054c",
      "2c2883502fc02e5ffb4cea70ca7aa601e94ee1d530aa47645a0fc08b7062acd6",
      "33dca1b97992e2925a81c7b6cb158e32254de123fcf1b53ec6da811e9260a72e",
      "4863bc193bdbccac11219d75a165ddefa35c3981f9d978ba19b169e04e85fd30"
    ],
    "env_rules": [
      {
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "strategy": "string",
        "required": false
      },
      {
        "strategy": "string",
        "required": false,
        "pattern": "TERM=xterm"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "(?i)(FABRIC)_.+=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "HOSTNAME=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "T(E)?MP=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "FabricPackageFileName=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "HostedServiceName=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "IDENTITY_API_VERSION=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "IDENTITY_HEADER=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "IDENTITY_SERVER_THUMBPRINT=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "azurecontainerinstance_restarted_by=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_SERVICE_HOST=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_SERVICE_PORT=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_SERVICE_PORT_[A-Z0-9_]+=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_PORT=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PROTO=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_PORT=.+"
      },
      {
        "strategy": "re2",
        "required": false,
        "pattern": "[A-Z0-9_]+_PORT_[0-9]+_TCP_ADDR=.+"
      },
      {
        "pattern": "APP_MODE=production",
        "strategy": "string",
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
    "command": [
      "/bin/sh",
      "-c",
      "echo hello"
    ],
    "signals": [
      3
    ],
    "working_dir": "/"
  }
]
