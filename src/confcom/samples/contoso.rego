package contoso

svn := "1"
framework_version := "0.2.3"

fragments := []

containers := [
  {
    "allow_elevated": false,
    "allow_stdio_access": true,
    "capabilities": {
      "ambient": [],
      "bounding": [
        "CAP_AUDIT_WRITE",
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_MKNOD",
        "CAP_NET_BIND_SERVICE",
        "CAP_NET_RAW",
        "CAP_SETFCAP",
        "CAP_SETGID",
        "CAP_SETPCAP",
        "CAP_SETUID",
        "CAP_SYS_CHROOT"
      ],
      "effective": [
        "CAP_AUDIT_WRITE",
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_MKNOD",
        "CAP_NET_BIND_SERVICE",
        "CAP_NET_RAW",
        "CAP_SETFCAP",
        "CAP_SETGID",
        "CAP_SETPCAP",
        "CAP_SETUID",
        "CAP_SYS_CHROOT"
      ],
      "inheritable": [],
      "permitted": [
        "CAP_AUDIT_WRITE",
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FOWNER",
        "CAP_FSETID",
        "CAP_KILL",
        "CAP_MKNOD",
        "CAP_NET_BIND_SERVICE",
        "CAP_NET_RAW",
        "CAP_SETFCAP",
        "CAP_SETGID",
        "CAP_SETPCAP",
        "CAP_SETUID",
        "CAP_SYS_CHROOT"
      ]
    },
    "command": [
      "python3",
      "main.py"
    ],
    "env_rules": [
      {
        "pattern": "TEST_REGEXP_ENV=test_regexp_env(.*)",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "required": false,
        "strategy": "string"
      },
      {
        "pattern": "PYTHONUNBUFFERED=1",
        "required": false,
        "strategy": "string"
      },
      {
        "pattern": "TERM=xterm",
        "required": false,
        "strategy": "string"
      },
      {
        "pattern": "(?i)(FABRIC)_.+=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "HOSTNAME=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "T(E)?MP=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "FabricPackageFileName=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "HostedServiceName=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "IDENTITY_API_VERSION=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "IDENTITY_HEADER=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "IDENTITY_SERVER_THUMBPRINT=.+",
        "required": false,
        "strategy": "re2"
      },
      {
        "pattern": "azurecontainerinstance_restarted_by=.+",
        "required": false,
        "strategy": "re2"
      }
    ],
    "exec_processes": [],
    "id": "mcr.microsoft.com/acc/samples/aci/helloworld:2.8",
    "layers": [
      "0de62d1aaa53f09c1ba26871cc97bda0ed29ea2eba4eb95c42b800159f0c087c",
      "1db0e60df71bbeda66196a3b518967cbc1b650cda08ada110744e0e07c965a5a",
      "e5c725f6ef8eae5de23753c9af8ca5489153eecd12982a0db0fc13d93fc7e124",
      "fdafe8a7071ca0af2ec45276bd7c4abe8aa3068b1fef08856251cf19638c52f2",
      "398208096568e4d3b1f7e420038c23d2bd3ba0a6c6b21b0f0d8f61c04d796bd7"
    ],
    "mounts": [
      {
        "destination": "/mount/azurefile",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/azureFileVolume/.+",
        "type": "bind"
      },
      {
        "destination": "/etc/resolv.conf",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/resolvconf/.+",
        "type": "bind"
      }
    ],
    "no_new_privileges": false,
    "seccomp_profile_sha256": "",
    "signals": [],
    "user": {
      "group_idnames": [
        {
          "pattern": "",
          "strategy": "any"
        }
      ],
      "umask": "0022",
      "user_idname": {
        "pattern": "",
        "strategy": "any"
      }
    },
    "working_dir": "/app"
  },
  {
    "allow_elevated": false,
    "allow_stdio_access": true,
    "capabilities": {
      "ambient": [],
      "bounding": [
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FSETID",
        "CAP_FOWNER",
        "CAP_MKNOD",
        "CAP_NET_RAW",
        "CAP_SETGID",
        "CAP_SETUID",
        "CAP_SETFCAP",
        "CAP_SETPCAP",
        "CAP_NET_BIND_SERVICE",
        "CAP_SYS_CHROOT",
        "CAP_KILL",
        "CAP_AUDIT_WRITE"
      ],
      "effective": [
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FSETID",
        "CAP_FOWNER",
        "CAP_MKNOD",
        "CAP_NET_RAW",
        "CAP_SETGID",
        "CAP_SETUID",
        "CAP_SETFCAP",
        "CAP_SETPCAP",
        "CAP_NET_BIND_SERVICE",
        "CAP_SYS_CHROOT",
        "CAP_KILL",
        "CAP_AUDIT_WRITE"
      ],
      "inheritable": [],
      "permitted": [
        "CAP_CHOWN",
        "CAP_DAC_OVERRIDE",
        "CAP_FSETID",
        "CAP_FOWNER",
        "CAP_MKNOD",
        "CAP_NET_RAW",
        "CAP_SETGID",
        "CAP_SETUID",
        "CAP_SETFCAP",
        "CAP_SETPCAP",
        "CAP_NET_BIND_SERVICE",
        "CAP_SYS_CHROOT",
        "CAP_KILL",
        "CAP_AUDIT_WRITE"
      ]
    },
    "command": [
      "/pause"
    ],
    "env_rules": [
      {
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "required": true,
        "strategy": "string"
      },
      {
        "pattern": "TERM=xterm",
        "required": false,
        "strategy": "string"
      }
    ],
    "exec_processes": [],
    "layers": [
      "16b514057a06ad665f92c02863aca074fd5976c755d26bff16365299169e8415"
    ],
    "mounts": [],
    "no_new_privileges": false,
    "seccomp_profile_sha256": "",
    "signals": [],
    "user": {
      "group_idnames": [
        {
          "pattern": "",
          "strategy": "any"
        }
      ],
      "umask": "0022",
      "user_idname": {
        "pattern": "",
        "strategy": "any"
      }
    },
    "working_dir": "/"
  }
]
