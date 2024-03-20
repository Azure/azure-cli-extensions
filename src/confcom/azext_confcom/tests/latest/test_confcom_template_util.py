# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from azext_confcom.custom import acipolicygen_confcom
import azext_confcom.config as config
from azext_confcom.template_util import (
    case_insensitive_dict_get,
    extract_confidential_properties,
)
from azext_confcom.os_util import load_json_from_str

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class TemplateUtil(unittest.TestCase):
    def test_case_insensitive_dict_get(self):
        test_dict = {"key1": "value1", "key2": "value2", "KEY3": "value3"}
        self.assertEqual(case_insensitive_dict_get(test_dict, "key1"), "value1")
        self.assertEqual(case_insensitive_dict_get(test_dict, "key3"), "value3")
        self.assertEqual(case_insensitive_dict_get(test_dict, "KEY1"), "value1")
        self.assertEqual(case_insensitive_dict_get(test_dict, "KEY3"), "value3")
        self.assertEqual(case_insensitive_dict_get(test_dict, "key4"), None)
        self.assertEqual(case_insensitive_dict_get(test_dict, "KEY4"), None)

    def test_extract_confidential_properties(self):
        """decoded policy:
        package policy

        import future.keywords.every
        import future.keywords.in

        fragments := [{
        "feed": "mcr.microsoft.com/aci/aci-cc-infra-fragment",
        "includes": [],
        "issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
        "minimum_svn": "1.0.0",
        }]

        containers := [
        {
                "allow_elevated": true,
                "allow_stdio_access": true,
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
                                "destination": "/sys",
                                "options": [
                                        "nosuid",
                                        "noexec",
                                        "nodev",
                                        "rw",
                                ],
                                "source": "sysfs",
                                "type": "sysfs",
                        },
                        {
                                "destination": "/sys/fs/cgroup",
                                "options": [
                                        "nosuid",
                                        "noexec",
                                        "nodev",
                                        "relatime",
                                        "rw",
                                ],
                                "source": "cgroup",
                                "type": "cgroup",
                        },
                        {
                                "destination": "/mount/azurefile",
                                "options": [
                                        "rbind",
                                        "rshared",
                                        "rw",
                                ],
                                "source": "sandbox:///tmp/atlas/azureFileVolume/.+",
                                "type": "azureFile",
                        },
                        {
                                "destination": "/etc/resolv.conf",
                                "options": [
                                        "rbind",
                                        "rshared",
                                        "rw",
                                ],
                                "source": "sandbox:///tmp/atlas/resolvconf/.+",
                                "type": "resolvconf",
                        },
                ],
                "signals": [],
                "working_dir": "/",
        },
        {
                "allow_elevated": false,
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
                "execProcesses": [],
                "layers": ["16b514057a06ad665f92c02863aca074fd5976c755d26bff16365299169e8415"],
                "mounts": [],
                "signals": [],
                "working_dir": "/",
        }
        ]

        allow_properties_access := false

        allow_dump_stacks := false

        allow_runtime_logging := false

        allow_environment_variable_dropping := true

        allow_unencrypted_scratch := false

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

        reason := {"errors": data.framework.errors}"""
        policy = {
            config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES: {
                config.ACI_FIELD_TEMPLATE_CCE_POLICY: """cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVy
ZS5rZXl3b3Jkcy5pbgoKZnJhZ21lbnRzIDo9IFt7CgkiZmVlZCI6ICJtY3IubWljcm9zb2Z0LmNv
bS9hY2kvYWNpLWNjLWluZnJhLWZyYWdtZW50IiwKCSJpbmNsdWRlcyI6IFtdLAoJImlzc3VlciI6
ICJkaWQ6eDUwOTowOnNoYTI1NjpJX19pdUwyNW9YRVZGZFRQX2FCTHhfZVQxUlBIYkNRX0VDQlFm
WVpwdDlzOjpla3U6MS4zLjYuMS40LjEuMzExLjc2LjU5LjEuMyIsCgkibWluaW11bV9zdm4iOiAi
MS4wLjAiLAp9XQoKY29udGFpbmVycyA6PSBbCgl7CgkJImFsbG93X2VsZXZhdGVkIjogdHJ1ZSwK
CQkiYWxsb3dfc3RkaW9fYWNjZXNzIjogdHJ1ZSwKCQkiY29tbWFuZCI6IFsiYmFzaCJdLAoJCSJl
bnZfcnVsZXMiOiBbCgkJCXsKCQkJCSJwYXR0ZXJuIjogIlBBVEg9L2N1c3RvbWl6ZWQvcGF0aC92
YWx1ZSIsCgkJCQkicmVxdWlyZWQiOiBmYWxzZSwKCQkJCSJzdHJhdGVneSI6ICJzdHJpbmciLAoJ
CQl9LAoJCQl7CgkJCQkicGF0dGVybiI6ICJURVNUX1JFR0VYUF9FTlY9dGVzdF9yZWdleHBfZW52
IiwKCQkJCSJyZXF1aXJlZCI6IGZhbHNlLAoJCQkJInN0cmF0ZWd5IjogInN0cmluZyIsCgkJCX0s
CgkJCXsKCQkJCSJwYXR0ZXJuIjogIlJVU1RVUF9IT01FPS91c3IvbG9jYWwvcnVzdHVwIiwKCQkJ
CSJyZXF1aXJlZCI6IGZhbHNlLAoJCQkJInN0cmF0ZWd5IjogInN0cmluZyIsCgkJCX0sCgkJCXsK
CQkJCSJwYXR0ZXJuIjogIkNBUkdPX0hPTUU9L3Vzci9sb2NhbC9jYXJnbyIsCgkJCQkicmVxdWly
ZWQiOiBmYWxzZSwKCQkJCSJzdHJhdGVneSI6ICJzdHJpbmciLAoJCQl9LAoJCQl7CgkJCQkicGF0
dGVybiI6ICJSVVNUX1ZFUlNJT049MS41Mi4xIiwKCQkJCSJyZXF1aXJlZCI6IGZhbHNlLAoJCQkJ
InN0cmF0ZWd5IjogInN0cmluZyIsCgkJCX0sCgkJCXsKCQkJCSJwYXR0ZXJuIjogIlRFUk09eHRl
cm0iLAoJCQkJInJlcXVpcmVkIjogZmFsc2UsCgkJCQkic3RyYXRlZ3kiOiAic3RyaW5nIiwKCQkJ
fSwKCQkJewoJCQkJInBhdHRlcm4iOiAiKCg/aSlGQUJSSUMpXy4rPS4rIiwKCQkJCSJyZXF1aXJl
ZCI6IGZhbHNlLAoJCQkJInN0cmF0ZWd5IjogInJlMiIsCgkJCX0sCgkJCXsKCQkJCSJwYXR0ZXJu
IjogIkhPU1ROQU1FPS4rIiwKCQkJCSJyZXF1aXJlZCI6IGZhbHNlLAoJCQkJInN0cmF0ZWd5Ijog
InJlMiIsCgkJCX0sCgkJCXsKCQkJCSJwYXR0ZXJuIjogIlQoRSk/TVA9LisiLAoJCQkJInJlcXVp
cmVkIjogZmFsc2UsCgkJCQkic3RyYXRlZ3kiOiAicmUyIiwKCQkJfSwKCQkJewoJCQkJInBhdHRl
cm4iOiAiRmFicmljUGFja2FnZUZpbGVOYW1lPS4rIiwKCQkJCSJyZXF1aXJlZCI6IGZhbHNlLAoJ
CQkJInN0cmF0ZWd5IjogInJlMiIsCgkJCX0sCgkJCXsKCQkJCSJwYXR0ZXJuIjogIkhvc3RlZFNl
cnZpY2VOYW1lPS4rIiwKCQkJCSJyZXF1aXJlZCI6IGZhbHNlLAoJCQkJInN0cmF0ZWd5IjogInJl
MiIsCgkJCX0sCgkJCXsKCQkJCSJwYXR0ZXJuIjogIklERU5USVRZX0FQSV9WRVJTSU9OPS4rIiwK
CQkJCSJyZXF1aXJlZCI6IGZhbHNlLAoJCQkJInN0cmF0ZWd5IjogInJlMiIsCgkJCX0sCgkJCXsK
CQkJCSJwYXR0ZXJuIjogIklERU5USVRZX0hFQURFUj0uKyIsCgkJCQkicmVxdWlyZWQiOiBmYWxz
ZSwKCQkJCSJzdHJhdGVneSI6ICJyZTIiLAoJCQl9LAoJCQl7CgkJCQkicGF0dGVybiI6ICJJREVO
VElUWV9TRVJWRVJfVEhVTUJQUklOVD0uKyIsCgkJCQkicmVxdWlyZWQiOiBmYWxzZSwKCQkJCSJz
dHJhdGVneSI6ICJyZTIiLAoJCQl9LAoJCQl7CgkJCQkicGF0dGVybiI6ICJhenVyZWNvbnRhaW5l
cmluc3RhbmNlX3Jlc3RhcnRlZF9ieT0uKyIsCgkJCQkicmVxdWlyZWQiOiBmYWxzZSwKCQkJCSJz
dHJhdGVneSI6ICJyZTIiLAoJCQl9LAoJCV0sCgkJImV4ZWNfcHJvY2Vzc2VzIjogW10sCgkJImlk
IjogInJ1c3Q6MS41Mi4xIiwKCQkibGF5ZXJzIjogWwoJCQkiZmU4NGM5ZDViZmRkZDA3YTI2MjRk
MDAzMzNjZjEzYzFhOWM5NDFmM2EyNjFmMTNlYWQ0NGZjNmE5M2JjMGU3YSIsCgkJCSI0ZGVkYWU0
Mjg0N2M3MDRkYTg5MWEyOGMyNWQzMjIwMWExYWU0NDBiY2UyYWVjY2NmYThlNmYwM2I5N2E2YTZj
IiwKCQkJIjQxZDY0Y2RlYjM0N2JmMjM2YjRjMTNiNzQwM2I2MzNmZjExZjFjZjk0ZGJjN2NmODgx
YTQ0ZDZkYTg4YzUxNTYiLAoJCQkiZWIzNjkyMWUxZjgyYWY0NmRmZTI0OGVmOGYxYjNhZmI2YTUy
MzBhNjQxODFkOTYwZDEwMjM3YTA4Y2Q3M2M3OSIsCgkJCSJlNzY5ZDc0ODdjYzMxNGQzZWU3NDhh
NDQ0MDgwNTMxN2MxOTI2MmM3YWNkMmZkYmRiMGQ0N2QyZTQ2MTNhMTVjIiwKCQkJIjFiODBmMTIw
ZGJkODhlNDM1NWQ2MjQxYjUxOWMzZTI1MjkwMjE1YzQ2OTUxNmI0OWRlY2U5Y2YwNzE3NWE3NjYi
LAoJCV0sCgkJIm1vdW50cyI6IFsKCQkJewoJCQkJImRlc3RpbmF0aW9uIjogIi9zeXMiLAoJCQkJ
Im9wdGlvbnMiOiBbCgkJCQkJIm5vc3VpZCIsCgkJCQkJIm5vZXhlYyIsCgkJCQkJIm5vZGV2IiwK
CQkJCQkicnciLAoJCQkJXSwKCQkJCSJzb3VyY2UiOiAic3lzZnMiLAoJCQkJInR5cGUiOiAic3lz
ZnMiLAoJCQl9LAoJCQl7CgkJCQkiZGVzdGluYXRpb24iOiAiL3N5cy9mcy9jZ3JvdXAiLAoJCQkJ
Im9wdGlvbnMiOiBbCgkJCQkJIm5vc3VpZCIsCgkJCQkJIm5vZXhlYyIsCgkJCQkJIm5vZGV2IiwK
CQkJCQkicmVsYXRpbWUiLAoJCQkJCSJydyIsCgkJCQldLAoJCQkJInNvdXJjZSI6ICJjZ3JvdXAi
LAoJCQkJInR5cGUiOiAiY2dyb3VwIiwKCQkJfSwKCQkJewoJCQkJImRlc3RpbmF0aW9uIjogIi9t
b3VudC9henVyZWZpbGUiLAoJCQkJIm9wdGlvbnMiOiBbCgkJCQkJInJiaW5kIiwKCQkJCQkicnNo
YXJlZCIsCgkJCQkJInJ3IiwKCQkJCV0sCgkJCQkic291cmNlIjogInNhbmRib3g6Ly8vdG1wL2F0
bGFzL2F6dXJlRmlsZVZvbHVtZS8uKyIsCgkJCQkidHlwZSI6ICJhenVyZUZpbGUiLAoJCQl9LAoJ
CQl7CgkJCQkiZGVzdGluYXRpb24iOiAiL2V0Yy9yZXNvbHYuY29uZiIsCgkJCQkib3B0aW9ucyI6
IFsKCQkJCQkicmJpbmQiLAoJCQkJCSJyc2hhcmVkIiwKCQkJCQkicnciLAoJCQkJXSwKCQkJCSJz
b3VyY2UiOiAic2FuZGJveDovLy90bXAvYXRsYXMvcmVzb2x2Y29uZi8uKyIsCgkJCQkidHlwZSI6
ICJyZXNvbHZjb25mIiwKCQkJfSwKCQldLAoJCSJzaWduYWxzIjogW10sCgkJIndvcmtpbmdfZGly
IjogIi8iLAoJfSwKCXsKCQkiYWxsb3dfZWxldmF0ZWQiOiBmYWxzZSwKCQkiY29tbWFuZCI6IFsi
L3BhdXNlIl0sCgkJImVudl9ydWxlcyI6IFsKCQkJewoJCQkJInBhdHRlcm4iOiAiUEFUSD0vdXNy
L2xvY2FsL3NiaW46L3Vzci9sb2NhbC9iaW46L3Vzci9zYmluOi91c3IvYmluOi9zYmluOi9iaW4i
LAoJCQkJInJlcXVpcmVkIjogdHJ1ZSwKCQkJCSJzdHJhdGVneSI6ICJzdHJpbmciLAoJCQl9LAoJ
CQl7CgkJCQkicGF0dGVybiI6ICJURVJNPXh0ZXJtIiwKCQkJCSJyZXF1aXJlZCI6IGZhbHNlLAoJ
CQkJInN0cmF0ZWd5IjogInN0cmluZyIsCgkJCX0sCgkJXSwKCQkiZXhlY1Byb2Nlc3NlcyI6IFtd
LAoJCSJsYXllcnMiOiBbIjE2YjUxNDA1N2EwNmFkNjY1ZjkyYzAyODYzYWNhMDc0ZmQ1OTc2Yzc1
NWQyNmJmZjE2MzY1Mjk5MTY5ZTg0MTUiXSwKCQkibW91bnRzIjogW10sCgkJInNpZ25hbHMiOiBb
XSwKCQkid29ya2luZ19kaXIiOiAiLyIsCgl9LApdCgphbGxvd19wcm9wZXJ0aWVzX2FjY2VzcyA6
PSBmYWxzZQoKYWxsb3dfZHVtcF9zdGFja3MgOj0gZmFsc2UKCmFsbG93X3J1bnRpbWVfbG9nZ2lu
ZyA6PSBmYWxzZQoKYWxsb3dfZW52aXJvbm1lbnRfdmFyaWFibGVfZHJvcHBpbmcgOj0gdHJ1ZQoK
YWxsb3dfdW5lbmNyeXB0ZWRfc2NyYXRjaCA6PSBmYWxzZQoKbW91bnRfZGV2aWNlIDo9IGRhdGEu
ZnJhbWV3b3JrLm1vdW50X2RldmljZQoKdW5tb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsu
dW5tb3VudF9kZXZpY2UKCm1vdW50X292ZXJsYXkgOj0gZGF0YS5mcmFtZXdvcmsubW91bnRfb3Zl
cmxheQoKdW5tb3VudF9vdmVybGF5IDo9IGRhdGEuZnJhbWV3b3JrLnVubW91bnRfb3ZlcmxheQoK
Y3JlYXRlX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5jcmVhdGVfY29udGFpbmVyCgpleGVj
X2luX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5leGVjX2luX2NvbnRhaW5lcgoKZXhlY19l
eHRlcm5hbCA6PSBkYXRhLmZyYW1ld29yay5leGVjX2V4dGVybmFsCgpzaHV0ZG93bl9jb250YWlu
ZXIgOj0gZGF0YS5mcmFtZXdvcmsuc2h1dGRvd25fY29udGFpbmVyCgpzaWduYWxfY29udGFpbmVy
X3Byb2Nlc3MgOj0gZGF0YS5mcmFtZXdvcmsuc2lnbmFsX2NvbnRhaW5lcl9wcm9jZXNzCgpwbGFu
OV9tb3VudCA6PSBkYXRhLmZyYW1ld29yay5wbGFuOV9tb3VudAoKcGxhbjlfdW5tb3VudCA6PSBk
YXRhLmZyYW1ld29yay5wbGFuOV91bm1vdW50CgpnZXRfcHJvcGVydGllcyA6PSBkYXRhLmZyYW1l
d29yay5nZXRfcHJvcGVydGllcwoKZHVtcF9zdGFja3MgOj0gZGF0YS5mcmFtZXdvcmsuZHVtcF9z
dGFja3MKCnJ1bnRpbWVfbG9nZ2luZyA6PSBkYXRhLmZyYW1ld29yay5ydW50aW1lX2xvZ2dpbmcK
CmxvYWRfZnJhZ21lbnQgOj0gZGF0YS5mcmFtZXdvcmsubG9hZF9mcmFnbWVudAoKc2NyYXRjaF9t
b3VudCA6PSBkYXRhLmZyYW1ld29yay5zY3JhdGNoX21vdW50CgpzY3JhdGNoX3VubW91bnQgOj0g
ZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF91bm1vdW50CgpyZWFzb24gOj0geyJlcnJvcnMiOiBkYXRh
LmZyYW1ld29yay5lcnJvcnN9Cg=="""
            }
        }

        (containers, fragments) = extract_confidential_properties(policy)

        self.assertEqual(containers[0]["id"], "rust:1.52.1")
        self.assertEqual(
            fragments[0]["feed"], "mcr.microsoft.com/aci/aci-cc-infra-fragment"
        )

    def test_inject_policy_into_template(self):
        template = """
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "variables": {
                "image": "python:3.6.14-slim-buster"
            },


            "parameters": {
                "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"simple-container-group"
                },

                "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container"
                },
                "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
                },
                "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
                },
                "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
                },
                "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
                }
            },
            "resources": [
                {
                "name": "[parameters('containergroupname')]",
                "type": "Microsoft.ContainerInstance/containerGroups",
                "apiVersion": "2023-05-01",
                "location": "[parameters('location')]",
                "properties": {
                    "containers": [
                    {
                        "name": "[parameters('containername')]",

                        "properties": {
                        "image": "[variables('image')]",
                        "command": [
                            "python3"
                        ],
                        "ports": [
                            {
                            "port": "[parameters('port')]"
                            }
                        ],
                        "resources": {
                            "requests": {
                            "cpu": "[parameters('cpuCores')]",
                            "memoryInGb": "[parameters('memoryInGb')]"
                            }
                        },
                        "volumeMounts": [
                                    {
                                        "name": "filesharevolume",
                                        "mountPath": "/aci/logs",
                                        "readOnly": false
                                    },
                                    {
                                        "name": "secretvolume",
                                        "mountPath": "/aci/secret",
                                        "readOnly": true
                                    }
                                ]
                        }
                    }
                    ],
                    "volumes": [
                        {
                            "name": "filesharevolume",
                            "azureFile": {
                                "shareName": "shareName1",
                                "storageAccountName": "storage-account-name",
                                "storageAccountKey": "storage-account-key"
                            }
                        },
                        {

                            "name": "secretvolume",
                            "secret": {
                                "mysecret1": "secret1",
                                "mysecret2": "secret2"
                            }
                        }

                    ],
                    "osType": "Linux",
                    "restartPolicy": "OnFailure",
                    "confidentialComputeProperties": {
                    "IsolationType": "SevSnp"
                    },
                    "ipAddress": {
                    "type": "Public",
                    "ports": [
                        {
                        "protocol": "Tcp",
                        "port": "[parameters( 'port' )]"
                        }
                    ]
                    }
                }
                }
            ],
            "outputs": {
                "containerIPv4Address": {
                "type": "string",
                "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
                }
            }
        }
        """
        filename = "test_template.json"
        # write template to file for testing
        with open(filename, "w") as f:
            f.write(template)

        with self.assertRaises(SystemExit) as exc_info:
            acipolicygen_confcom(None, filename, None, None, None, None)

        self.assertEqual(exc_info.exception.code, 0)

        with open(filename, "r") as f:
            template_with_policy = load_json_from_str(f.read())

            # check if template contains confidential compute policy

            self.assertIn(
                config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES,
                template_with_policy[config.ACI_FIELD_RESOURCES][0][
                    config.ACI_FIELD_TEMPLATE_PROPERTIES
                ],
            )
            self.assertTrue(
                isinstance(
                    template_with_policy[config.ACI_FIELD_RESOURCES][0][
                        config.ACI_FIELD_TEMPLATE_PROPERTIES
                    ][config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES][
                        config.ACI_FIELD_TEMPLATE_CCE_POLICY
                    ],
                    str,
                )
            )
            self.assertTrue(
                len(
                    template_with_policy[config.ACI_FIELD_RESOURCES][0][
                        config.ACI_FIELD_TEMPLATE_PROPERTIES
                    ][config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES]
                )
                > 0
            )
        # delete test file
        os.remove(filename)
