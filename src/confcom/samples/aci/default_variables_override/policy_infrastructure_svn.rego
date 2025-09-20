package policy

import future.keywords.every
import future.keywords.in

api_version := "0.10.0"
framework_version := "0.2.3"

fragments := [
  {
    "feed": "mcr.microsoft.com/aci/aci-cc-infra-fragment",
    "includes": [
      "containers",
      "fragments"
    ],
    "issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
    "minimum_svn": "99"
  }
]

containers := [{"allow_elevated":false,"allow_stdio_access":true,"capabilities":{"ambient":[],"bounding":["CAP_AUDIT_WRITE","CAP_CHOWN","CAP_DAC_OVERRIDE","CAP_FOWNER","CAP_FSETID","CAP_KILL","CAP_MKNOD","CAP_NET_BIND_SERVICE","CAP_NET_RAW","CAP_SETFCAP","CAP_SETGID","CAP_SETPCAP","CAP_SETUID","CAP_SYS_CHROOT"],"effective":["CAP_AUDIT_WRITE","CAP_CHOWN","CAP_DAC_OVERRIDE","CAP_FOWNER","CAP_FSETID","CAP_KILL","CAP_MKNOD","CAP_NET_BIND_SERVICE","CAP_NET_RAW","CAP_SETFCAP","CAP_SETGID","CAP_SETPCAP","CAP_SETUID","CAP_SYS_CHROOT"],"inheritable":[],"permitted":["CAP_AUDIT_WRITE","CAP_CHOWN","CAP_DAC_OVERRIDE","CAP_FOWNER","CAP_FSETID","CAP_KILL","CAP_MKNOD","CAP_NET_BIND_SERVICE","CAP_NET_RAW","CAP_SETFCAP","CAP_SETGID","CAP_SETPCAP","CAP_SETUID","CAP_SYS_CHROOT"]},"command":["python3","main.py"],"env_rules":[{"pattern":"(?i)(FABRIC)_.+=.+","required":false,"strategy":"re2"},{"pattern":"FabricPackageFileName=.+","required":false,"strategy":"re2"},{"pattern":"HOSTNAME=.+","required":false,"strategy":"re2"},{"pattern":"HostedServiceName=.+","required":false,"strategy":"re2"},{"pattern":"IDENTITY_API_VERSION=.+","required":false,"strategy":"re2"},{"pattern":"IDENTITY_HEADER=.+","required":false,"strategy":"re2"},{"pattern":"IDENTITY_SERVER_THUMBPRINT=.+","required":false,"strategy":"re2"},{"pattern":"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","required":false,"strategy":"string"},{"pattern":"PYTHONUNBUFFERED=1","required":false,"strategy":"string"},{"pattern":"T(E)?MP=.+","required":false,"strategy":"re2"},{"pattern":"TERM=xterm","required":false,"strategy":"string"},{"pattern":"azurecontainerinstance_restarted_by=.+","required":false,"strategy":"re2"}],"exec_processes":[],"id":"mcr.microsoft.com/acc/samples/aci/helloworld@sha256:86da7a2c5e55b72bf6bc7cf465b860e49c075395d854877124de63a9342ac777","layers":["4e74440c7b0e6e6c1cc9e6eb9b779e1ffde807122ed8a16bb0422a1d64fd5aa8","4cf856bcde8e1fa71f57d2218e21dd7c1a6a12c6d930d2bdb4bdb13a46fed9e4","41a52f45506177737caec5d57fe6160b6c8942dcac1bc7834fc0e94e62ff6b4d","b8ea8eae7795453b5e3dcfafe3f11fb2d68efb1062308e4d2411d44dd19fa97c","a0df1939f552483286c45204e7f583c9a6146963a79556fe22578d7b7e63e7a1","3ccbd6b119e951f3f2586339e9d10168b064a5852fd87cfae94af47a89f4d6c6","8348c9d4357db6a600aa4c5116ed9755a230d274096706a7d214c02105d0b256"],"mounts":[{"destination":"/etc/resolv.conf","options":["rbind","rshared","rw"],"source":"sandbox:///tmp/atlas/resolvconf/.+","type":"bind"}],"name":"container1","no_new_privileges":false,"seccomp_profile_sha256":"","signals":[],"user":{"group_idnames":[{"pattern":"","strategy":"any"}],"umask":"0022","user_idname":{"pattern":"","strategy":"any"}},"working_dir":"/app"},{"allow_elevated":false,"allow_stdio_access":true,"capabilities":{"ambient":[],"bounding":["CAP_CHOWN","CAP_DAC_OVERRIDE","CAP_FSETID","CAP_FOWNER","CAP_MKNOD","CAP_NET_RAW","CAP_SETGID","CAP_SETUID","CAP_SETFCAP","CAP_SETPCAP","CAP_NET_BIND_SERVICE","CAP_SYS_CHROOT","CAP_KILL","CAP_AUDIT_WRITE"],"effective":["CAP_CHOWN","CAP_DAC_OVERRIDE","CAP_FSETID","CAP_FOWNER","CAP_MKNOD","CAP_NET_RAW","CAP_SETGID","CAP_SETUID","CAP_SETFCAP","CAP_SETPCAP","CAP_NET_BIND_SERVICE","CAP_SYS_CHROOT","CAP_KILL","CAP_AUDIT_WRITE"],"inheritable":[],"permitted":["CAP_CHOWN","CAP_DAC_OVERRIDE","CAP_FSETID","CAP_FOWNER","CAP_MKNOD","CAP_NET_RAW","CAP_SETGID","CAP_SETUID","CAP_SETFCAP","CAP_SETPCAP","CAP_NET_BIND_SERVICE","CAP_SYS_CHROOT","CAP_KILL","CAP_AUDIT_WRITE"]},"command":["/pause"],"env_rules":[{"pattern":"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","required":true,"strategy":"string"},{"pattern":"TERM=xterm","required":false,"strategy":"string"}],"exec_processes":[],"layers":["16b514057a06ad665f92c02863aca074fd5976c755d26bff16365299169e8415"],"mounts":[],"name":"pause-container","no_new_privileges":false,"seccomp_profile_sha256":"","signals":[],"user":{"group_idnames":[{"pattern":"","strategy":"any"}],"umask":"0022","user_idname":{"pattern":"","strategy":"any"}},"working_dir":"/"}]

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


