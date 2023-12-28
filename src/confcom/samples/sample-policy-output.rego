package policy

import future.keywords.every
import future.keywords.in

api_version := "0.10.0"

framework_version := "0.2.3"

fragments := [{
	"feed": "mcr.microsoft.com/aci/aci-cc-infra-fragment",
	"includes": [
		"containers",
		"fragments",
	],
	"issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
	"minimum_svn": "1",
}]

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
				"CAP_SYS_CHROOT",
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
				"CAP_SYS_CHROOT",
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
				"CAP_SYS_CHROOT",
			],
		},
		"command": ["bash"],
		"env_rules": [
			{
				"pattern": "PATH=/customized/path/value",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "TEST_REGEXP_ENV=test_regexp_env",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "RUSTUP_HOME=/usr/local/rustup",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "CARGO_HOME=/usr/local/cargo",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "RUST_VERSION=1.52.1",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "TERM=xterm",
				"required": false,
				"strategy": "string",
			},
			{
				"pattern": "(?i)(FABRIC)_.+=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "HOSTNAME=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "T(E)?MP=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "FabricPackageFileName=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "HostedServiceName=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "IDENTITY_API_VERSION=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "IDENTITY_HEADER=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "IDENTITY_SERVER_THUMBPRINT=.+",
				"required": false,
				"strategy": "re2",
			},
			{
				"pattern": "azurecontainerinstance_restarted_by=.+",
				"required": false,
				"strategy": "re2",
			},
		],
		"exec_processes": [],
		"id": "rust:1.52.1",
		"layers": [
			"fe84c9d5bfddd07a2624d00333cf13c1a9c941f3a261f13ead44fc6a93bc0e7a",
			"4dedae42847c704da891a28c25d32201a1ae440bce2aecccfa8e6f03b97a6a6c",
			"41d64cdeb347bf236b4c13b7403b633ff11f1cf94dbc7cf881a44d6da88c5156",
			"eb36921e1f82af46dfe248ef8f1b3afb6a5230a64181d960d10237a08cd73c79",
			"e769d7487cc314d3ee748a4440805317c19262c7acd2fdbdb0d47d2e4613a15c",
			"1b80f120dbd88e4355d6241b519c3e25290215c469516b49dece9cf07175a766",
		],
		"mounts": [
			{
				"destination": "/mount/azurefile",
				"options": [
					"rbind",
					"rshared",
					"rw",
				],
				"source": "sandbox:///tmp/atlas/azureFileVolume/.+",
				"type": "bind",
			},
			{
				"destination": "/etc/resolv.conf",
				"options": [
					"rbind",
					"rshared",
					"rw",
				],
				"source": "sandbox:///tmp/atlas/resolvconf/.+",
				"type": "bind",
			},
		],
		"no_new_privileges": false,
		"seccomp_profile_sha256": "",
		"signals": [],
		"user": {
			"group_idnames": [{
				"pattern": "",
				"strategy": "any",
			}],
			"umask": "0022",
			"user_idname": {
				"pattern": "",
				"strategy": "any",
			},
		},
		"working_dir": "/",
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
				"CAP_AUDIT_WRITE",
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
				"CAP_AUDIT_WRITE",
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
				"CAP_AUDIT_WRITE",
			],
		},
		"command": ["/pause"],
		"env_rules": [
			{
				"pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
				"required": true,
				"strategy": "string",
			},
			{
				"pattern": "TERM=xterm",
				"required": false,
				"strategy": "string",
			},
		],
		"exec_processes": [],
		"layers": ["16b514057a06ad665f92c02863aca074fd5976c755d26bff16365299169e8415"],
		"mounts": [],
		"no_new_privileges": false,
		"seccomp_profile_sha256": "",
		"signals": [],
		"user": {
			"group_idnames": [{
				"pattern": "",
				"strategy": "any",
			}],
			"umask": "0022",
			"user_idname": {
				"pattern": "",
				"strategy": "any",
			},
		},
		"working_dir": "/",
	},
]

allow_properties_access := true

allow_dump_stacks := false

allow_runtime_logging := false

allow_environment_variable_dropping := true

allow_unencrypted_scratch := false

allow_capability_dropping := true

mount_device := data.framework.mount_device

unmount_device := data.framework.unmount_device

mount_overlay := data.framework.mount_overlay

unmount_overlay := data.framework.unmount_overlay

create_container := data.framework.create_container

exec_in_container := data.framework.exec_in_container

exec_external := data.framework.exec_external

shutdown_container := data.framework.shutdown_container

signal_container_process := data.framework.signal_container_process

plan9_mount := data.framework.plan9_mount

plan9_unmount := data.framework.plan9_unmount

get_properties := data.framework.get_properties

dump_stacks := data.framework.dump_stacks

runtime_logging := data.framework.runtime_logging

load_fragment := data.framework.load_fragment

scratch_mount := data.framework.scratch_mount

scratch_unmount := data.framework.scratch_unmount

reason := {"errors": data.framework.errors}
