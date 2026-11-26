# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from tarfile import TarFile
from unittest.mock import patch

import azext_confcom.config as config
import docker
import requests
from azext_confcom.cose_proxy import CoseSignToolProxy
from azext_confcom.custom import acifragmentgen_confcom, acipolicygen_confcom
from azext_confcom.errors import AccContainerError
from azext_confcom.oras_proxy import pull, push_fragment_to_registry
from azext_confcom.os_util import (delete_silently, force_delete_silently,
                                   load_json_from_file, load_json_from_str,
                                   load_str_from_file, str_to_base64,
                                   write_str_to_file)
from azext_confcom.security_policy import (OutputType, UserContainerImage,
                                           load_policy_from_json)
from azext_confcom.template_util import (
    DockerClient, case_insensitive_dict_get, decompose_confidential_properties,
    extract_containers_and_fragments_from_text, extract_containers_from_text)
from azext_confcom.tests.latest.test_confcom_tar import create_tar_file
from azure.cli.testsdk import ScenarioTest
from knack.util import CLIError

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
SAMPLES_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", '..', '..', '..', 'samples'))


class FragmentMountEnforcement(unittest.TestCase):
    custom_json = """
    {
        "version": "1.0",
        "containers": [
            {
                "name": "test-container",
                "properties": {
                    "image": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                    "environmentVariables": [
                        {
                            "name": "PATH",
                            "value": "/customized/path/value"
                        },
                        {
                            "name": "TEST_REGEXP_ENV",
                            "value": "test_regexp_env_[[:alpha:]]*",
                            "regex": true
                        }
                    ],
                    "command": ["rustc", "--help"],
                    "volumeMounts": [
                        {
                            "name": "azurefile",
                            "mountPath": "/mount/azurefile",
                            "mountType": "azureFile",
                            "readonly": true
                        }
                    ]
                }
            }
        ]
    }
    """
    custom_json2 = """
{
  "version": "1.0",
  "fragments": [],
  "scenario": "vn2",
  "containers": [
    {
      "name": "simple-container",
      "properties": {
        "image": "mcr.microsoft.com/azurelinux/base/python:3.12",
        "environmentVariables": [
          {
            "name": "PATH",
            "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
          }
        ],
        "command": [
          "python3"
        ],
        "securityContext": {
            "allowPrivilegeEscalation": true,
            "privileged": true
        },
        "volumeMounts": [
          {
            "name": "logs",
            "mountType": "emptyDir",
            "mountPath": "/aci/logs",
            "readonly": false
          },
          {
            "name": "secret",
            "mountType": "emptyDir",
            "mountPath": "/aci/secret",
            "readonly": true
          }
        ]
      }
    }
  ]
}
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_json(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_fragment_user_container_customized_mounts(self):
        image = next(
            (
                img
                for img in self.aci_policy.get_images()
                if isinstance(img, UserContainerImage) and img.base == "mcr.microsoft.com/azurelinux/distroless/base"
            ),
            None,
        )

        self.assertIsNotNone(image)
        data = image.get_policy_json()

        self.assertEqual(
            len(
                case_insensitive_dict_get(
                    data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
                )
            ),
            2,
        )
        mount = case_insensitive_dict_get(
            data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
        )[0]
        resolv_mount = case_insensitive_dict_get(
            data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
        )[1]
        self.assertIsNotNone(resolv_mount)
        self.assertEqual(
            case_insensitive_dict_get(mount, "source"),
            "sandbox:///tmp/atlas/azureFileVolume/.+",
        )
        self.assertEqual(
            case_insensitive_dict_get(
                resolv_mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION
            ),
            "/etc/resolv.conf",
        )
        self.assertEqual(
            resolv_mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS][2], "rw"
        )

    def test_fragment_user_container_mount_injected_dns(self):
        image = next(
            (
                img
                for img in self.aci_policy.get_images()
                if isinstance(img, UserContainerImage) and img.base == "mcr.microsoft.com/azurelinux/distroless/base"
            ),
            None,
        )

        self.assertIsNotNone(image)
        data = image.get_policy_json()
        self.assertEqual(
            len(
                case_insensitive_dict_get(
                    data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
                )
            ),
            2,
        )
        mount = case_insensitive_dict_get(
            data, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS
        )[1]
        self.assertIsNotNone(mount)
        self.assertEqual(
            case_insensitive_dict_get(
                mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_SOURCE
            ),
            "sandbox:///tmp/atlas/resolvconf/.+",
        )
        self.assertEqual(
            case_insensitive_dict_get(
                mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION
            ),
            "/etc/resolv.conf",
        )
        self.assertEqual(
            mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS][2], "rw"
        )

    def test_virtual_node_policy_fragment_generation(self):
        try:
            fragment_filename = "policy_fragment_file.json"
            write_str_to_file(fragment_filename, self.custom_json2)
            rego_filename = "example_fragment_file"
            acifragmentgen_confcom(None, fragment_filename, None, rego_filename, "1", "test_feed_file", None, None, None)

            containers, _ = decompose_confidential_properties(str_to_base64(load_str_from_file(f"{rego_filename}.rego")))

            custom_container = containers[0]
            vn2_privileged_mounts = [x.get(config.ACI_FIELD_CONTAINERS_MOUNTS_PATH) for x in config.DEFAULT_MOUNTS_PRIVILEGED_VIRTUAL_NODE]
            vn2_mounts = [x.get(config.ACI_FIELD_CONTAINERS_MOUNTS_PATH) for x in config.DEFAULT_MOUNTS_VIRTUAL_NODE]

            vn2_mount_count = 0
            priv_mount_count = 0
            for mount in custom_container.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS):
                mount_name = mount.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION)

                if mount_name in vn2_privileged_mounts:
                    priv_mount_count += 1
                if mount_name in vn2_mounts:
                    vn2_mount_count += 1
            if priv_mount_count != len(vn2_privileged_mounts):
                self.fail("policy does not contain privileged vn2 mounts")
            if vn2_mount_count != len(vn2_mounts):
                self.fail("policy does not contain default vn2 mounts")
        finally:
            force_delete_silently([fragment_filename, f"{rego_filename}.rego"])

class FragmentGenerating(unittest.TestCase):
    custom_json = """
      {
        "version": "1.0",
        "containers": [
            {
                "name": "sidecar-container",
                "properties": {
                    "image": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1",
                    "environmentVariables": [
                    {
                        "name": "IDENTITY_API_VERSION",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "IDENTITY_HEADER",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "IDENTITY_SERVER_THUMBPRINT",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "ACI_MI_CLIENT_ID_.+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "ACI_MI_RES_ID_.+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "HOSTNAME",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "TERM",
                        "value": "xterm",
                        "regex": false
                    },
                    {
                        "name": "PATH",
                        "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                    },
                    {
                        "name": "(?i)(FABRIC)_.+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_Id+",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_ServiceName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_ApplicationName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_CodePackageName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "Fabric_ServiceDnsName",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "ACI_MI_DEFAULT",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "TokenProxyIpAddressEnvKeyName",
                        "value": "[ContainerToHostAddress|Fabric_NodelPOrFQDN]",
                        "regex": true
                    },
                    {
                        "name": "ContainerToHostAddress",
                        "value": "sidecar-container"
                    },
                    {
                        "name": "Fabric_NetworkingMode",
                        "value": ".+",
                        "regex": true
                    },
                    {
                        "name": "azurecontainerinstance_restarted_by",
                        "value": ".+",
                        "regex": true
                    }
                ],
                "command": ["/bin/sh","-c","until ./msiAtlasAdapter; do echo $? restarting; done"],
                "mounts": null
                }
            }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_json(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy


    def test_fragment_omit_id(self):
        output = self.aci_policy.get_serialized_output(
            output_type=OutputType.RAW, rego_boilerplate=False, omit_id=True
        )
        output_json = load_json_from_str(output)

        self.assertNotIn("id", output_json[0])

        # test again with omit_id=False
        output2 = self.aci_policy.get_serialized_output(
            output_type=OutputType.RAW, rego_boilerplate=False
        )
        output_json2 = load_json_from_str(output2)

        self.assertIn("id", output_json2[0])


    def test_fragment_injected_sidecar_container_msi(self):
        image = self.aci_policy.get_images()[0]
        env_vars = [
            {
                "name": "IDENTITY_API_VERSION",
                "value": ".+",
            },
            {
                "name": "IDENTITY_HEADER",
                "value": ".+",
            },
            {
                "name": "IDENTITY_SERVER_THUMBPRINT",
                "value": ".+",
            },
            {
                "name": "ACI_MI_CLIENT_ID_.+",
                "value": ".+",
            },
            {
                "name": "ACI_MI_RES_ID_.+",
                "value": ".+",
            },
            {
                "name": "HOSTNAME",
                "value": ".+",
            },
            {
                "name": "TERM",
                "value": "xterm",
            },
            {
                "name": "PATH",
                "value": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            },
            {
                "name": "(?i)(FABRIC)_.+",
                "value": ".+",
            },
            {
                "name": "Fabric_Id+",
                "value": ".+",
            },
            {
                "name": "Fabric_ServiceName",
                "value": ".+",
            },
            {
                "name": "Fabric_ApplicationName",
                "value": ".+",
            },
            {
                "name": "Fabric_CodePackageName",
                "value": ".+",
            },
            {
                "name": "Fabric_ServiceDnsName",
                "value": ".+",
            },
            {
                "name": "ACI_MI_DEFAULT",
                "value": ".+",
            },
            {
                "name": "TokenProxyIpAddressEnvKeyName",
                "value": "[ContainerToHostAddress|Fabric_NodelPOrFQDN]",
            },
            {
                "name": "ContainerToHostAddress",
                "value": "sidecar-container",
            },
            {
                "name": "Fabric_NetworkingMode",
                "value": ".+",
            },
            {
                "name": "azurecontainerinstance_restarted_by",
                "value": ".+",
            }
        ]
        command = ["/bin/sh", "-c", "until ./msiAtlasAdapter; do echo $? restarting; done"]
        self.assertEqual(image.base, "mcr.microsoft.com/aci/msi-atlas-adapter")
        self.assertIsNotNone(image)

        self.assertEqual(image._command, command)
        env_names = list(map(lambda x: x['pattern'], image._environmentRules + image._extraEnvironmentRules))
        for env_var in env_vars:
            self.assertIn(env_var['name'] + "=" + env_var['value'], env_names)

        expected_workingdir = "/root/"
        self.assertEqual(image._workingDir, expected_workingdir)


class FragmentPolicyGeneratingTarfile(unittest.TestCase):
    custom_json= """
    {
        "version" : "1.0",
        "containers": [
            {
                "name": "simple-container",
                "properties": {
                    "image": "mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64",
                    "environmentVariables": [
                    {
                        "name": "PORT",
                        "value": "8080"
                    }
                ],
                "command": ["/bin/bash","-c","while sleep 5; do cat /mnt/input/access.log; done"],
                "mounts": null
                }
            }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls) -> None:
        path = os.path.dirname(__file__)
        cls.path = path

    def test_tar_file_fragment(self):
        try:
            with tempfile.TemporaryDirectory() as folder:
                filename = os.path.join(folder, "oci.tar")
                filename2 = os.path.join(folder, "oci2.tar")

                tar_mapping_file = {"mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64": filename2}
                create_tar_file(filename)
                with TarFile(filename, "r") as tar:
                    tar.extractall(path=folder)

                with TarFile.open(filename2, mode="w") as out_tar:
                    out_tar.add(os.path.join(folder, "index.json"), "index.json")
                    out_tar.add(os.path.join(folder, "blobs"), "blobs", recursive=True)

                with load_policy_from_json(self.custom_json) as aci_policy:
                    aci_policy.populate_policy_content_for_all_images(
                        tar_mapping=tar_mapping_file
                    )

                    clean_room_fragment_text = aci_policy.generate_fragment("payload", "1", OutputType.RAW)
                    self.assertIsNotNone(clean_room_fragment_text)
        except Exception as e:
            raise AccContainerError("Could not get image from tar file") from e


class FragmentPolicyGeneratingDebugMode(unittest.TestCase):
    custom_json = """
      {
        "version": "1.0",
        "containers": [
            {
            "name": "test-container",
            "properties": {
                    "image": "mcr.microsoft.com/azurelinux/distroless/base:3.0",
                "environmentVariables": [

                ],
                "command": ["python3"]
            }
        }
        ]
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_json(cls.custom_json, debug_mode=True) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_debug_processes(self):
        policy = self.aci_policy.get_serialized_output(
            output_type=OutputType.RAW, rego_boilerplate=True
        )
        self.assertIsNotNone(policy)

        # see if debug mode is enabled
        containers, _ = extract_containers_and_fragments_from_text(policy)

        self.assertTrue(containers[0]["allow_stdio_access"])
        self.assertTrue(containers[0]["exec_processes"][0]["command"] == ["/bin/sh"])


class FragmentSidecarValidation(unittest.TestCase):
    custom_json = """
      {
    "version": "1.0",
    "containers": [
        {
            "name": "test-container",
            "properties": {
                "image": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": ".+",
                        "regex": true
                    }
                ],
                "command": [
                    "/bin/sh",
                    "-c",
                    "until ./msiAtlasAdapter; do echo $? restarting; done"
                ],
                "workingDir": "/root/",
                "mounts": null
            }
        }
    ]
}
    """
    custom_json2 = """
      {
    "version": "1.0",
    "containers": [
        {
            "name": "test-container",
            "properties": {
                "image": "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1",
                "environmentVariables": [
                {"name": "PATH",
                "value":"/",
                "strategy":"string"}
                ],
                "command": [
                    "/bin/sh",
                    "-c",
                    "until ./msiAtlasAdapter; do echo $? restarting; done"
                ],
                "workingDir": "/root/",
                "mounts": null
            }
        }
    ]
}
    """

    aci_policy = None
    existing_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_json(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy
        with load_policy_from_json(cls.custom_json2) as aci_policy2:
            aci_policy2.populate_policy_content_for_all_images()
            cls.aci_policy2 = aci_policy2

    def test_fragment_sidecar(self):
        is_valid, diff = self.aci_policy.validate_sidecars()
        self.assertTrue(is_valid)
        self.assertTrue(not diff)

    def test_fragment_sidecar_stdio_access_default(self):
        self.assertTrue(
            json.loads(
                self.aci_policy.get_serialized_output(
                    output_type=OutputType.RAW, rego_boilerplate=False
                )
            )[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS]
        )

    def test_fragment_incorrect_sidecar(self):

        is_valid, diff = self.aci_policy2.validate_sidecars()

        self.assertFalse(is_valid)
        expected_diff = {
            "mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1": {
                "env_rules": [
                    "environment variable with rule "
                    + "'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'"
                    + " does not match strings or regex in policy rules"
                ]
            }
        }

        self.assertEqual(diff, expected_diff)


class FragmentPolicySigning(unittest.TestCase):
    custom_json = """
{
    "version": "1.0",
    "containers": [
        {
            "name": "my-image",
            "properties": {
                "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
                "execProcesses": [
                    {
                        "command": [
                            "echo",
                            "Hello World"
                        ]
                    }
                ],
                "volumeMounts": [
                    {
                        "name": "azurefile",
                        "mountPath": "/mount/azurefile",
                        "mountType": "azureFile",
                        "readOnly": true
                    }
                ],
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": "/customized/path/value"
                    },
                    {
                        "name": "TEST_REGEXP_ENV",
                        "value": "test_regexp_env(.*)",
                        "regex": true
                    }
                ]
            }
        }
    ]
}
    """
    custom_json2 = """
{
    "version": "1.0",
    "fragments": [
    ],
    "containers": [
        {
            "name": "my-image",
            "properties": {
                "image": "mcr.microsoft.com/azurelinux/busybox:1.36",
                "execProcesses": [
                    {
                        "command": [
                            "sleep",
                            "infinity"
                        ]
                    }
                ],
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": "/another/customized/path/value"
                    },
                    {
                        "name": "TEST_REGEXP_ENV2",
                        "value": "test_regexp_env2(.*)",
                        "regex": true
                    }
                ]
            }
        },
        {
            "name": "my-image",
            "properties": {
                "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
                "execProcesses": [
                    {
                        "command": [
                            "echo",
                            "Hello World"
                        ]
                    }
                ],
                "volumeMounts": [
                    {
                        "name": "azurefile",
                        "mountPath": "/mount/azurefile",
                        "mountType": "azureFile",
                        "readOnly": true
                    }
                ],
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": "/customized/path/value"
                    },
                    {
                        "name": "TEST_REGEXP_ENV",
                        "value": "test_regexp_env(.*)",
                        "regex": true
                    }
                ]
            }
        }
    ]
}
    """
    @classmethod
    def setUpClass(cls):
        cls.key_dir_parent = Path(tempfile.gettempdir(), "certchain")
        cls.key_dir_parent.mkdir(parents=True, exist_ok=True)
        cls.key = os.path.join(cls.key_dir_parent, 'intermediateCA', 'private', 'ec_p384_private.pem')
        cls.chain = os.path.join(cls.key_dir_parent, 'intermediateCA', 'certs', 'www.contoso.com.chain.cert.pem')
        if not os.path.exists(cls.key) or not os.path.exists(cls.chain):
            script_path = os.path.join(SAMPLES_DIR, "certs", 'create_certchain.sh')

            arg_list = [
                script_path,
                cls.key_dir_parent.as_posix(),
            ]
            os.chmod(script_path, 0o755)

            # NOTE: this will raise an exception if it's run on windows and the key/cert files don't exist
            item = subprocess.run(
                arg_list,
                check=False,
                shell=False,
                env=os.environ.copy(),
            )

            if item.returncode != 0:
                raise Exception("Error creating certificate chain")

        with load_policy_from_json(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy
        with load_policy_from_json(cls.custom_json2) as aci_policy2:
            aci_policy2.populate_policy_content_for_all_images()
            cls.aci_policy2 = aci_policy2

    def test_signing(self):
        filename = "payload.rego"
        feed = "test_feed"
        algo = "ES384"
        out_path = filename + ".cose"

        fragment_text = self.aci_policy.generate_fragment("payload", 1, OutputType.RAW)
        try:
            write_str_to_file(filename, fragment_text)

            cose_proxy = CoseSignToolProxy()
            iss = cose_proxy.create_issuer(self.chain)

            cose_proxy.cose_sign(filename, self.key, self.chain, feed, iss, algo, out_path)
            self.assertTrue(os.path.exists(filename))
            self.assertTrue(os.path.exists(out_path))
        except Exception as e:
            raise e
        finally:
            delete_silently([filename, out_path])

    def test_generate_import(self):
        filename = "payload4.rego"
        feed = "test_feed"
        algo = "ES384"
        out_path = filename + ".cose"

        fragment_text = self.aci_policy.generate_fragment("payload4", "1", OutputType.RAW)
        try:
            write_str_to_file(filename, fragment_text)

            cose_proxy = CoseSignToolProxy()
            iss = cose_proxy.create_issuer(self.chain)
            cose_proxy.cose_sign(filename, self.key, self.chain, feed, iss, algo, out_path)

            import_statement = cose_proxy.generate_import_from_path(out_path, "1")
            self.assertTrue(import_statement)
            self.assertEqual(
                import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISSUER,""),iss
            )
            self.assertEqual(
                import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED,""),feed
            )
            self.assertEqual(
                import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN,""), "1"
            )
            self.assertEqual(
                import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_INCLUDES,[]),[config.POLICY_FIELD_CONTAINERS, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS]
            )

        except Exception as e:
            raise e
        finally:
            delete_silently([filename, out_path])

    def test_local_fragment_references(self):
        filename = "payload2.rego"
        filename2 = "payload3.rego"
        fragment_json = "fragment_local.json"
        feed = "test_feed"
        feed2 = "test_feed2"
        algo = "ES384"
        out_path = filename + ".cose"
        out_path2 = filename2 + ".cose"

        fragment_text = self.aci_policy.generate_fragment("payload2", "1", OutputType.RAW)

        try:
            write_str_to_file(filename, fragment_text)
            write_str_to_file(fragment_json, self.custom_json2)

            cose_proxy = CoseSignToolProxy()
            iss = cose_proxy.create_issuer(self.chain)
            cose_proxy.cose_sign(filename, self.key, self.chain, feed, iss, algo, out_path)

            # this will insert the import statement from the first fragment into the second one
            acifragmentgen_confcom(
                None, None, None, None, None, None, None, None, generate_import=True, minimum_svn="1", fragments_json=fragment_json, fragment_path=out_path
            )
            # put the "path" field into the import statement
            temp_json = load_json_from_file(fragment_json)
            temp_json["fragments"][0]["path"] = out_path

            write_str_to_file(fragment_json, json.dumps(temp_json))

            acifragmentgen_confcom(
                None, fragment_json, None, "payload3", "1", feed2, self.key, self.chain, None, output_filename=filename2
            )

            # make sure all of our output files exist
            self.assertTrue(os.path.exists(filename2))
            self.assertTrue(os.path.exists(out_path2))
            self.assertTrue(os.path.exists(fragment_json))
            # check the contents of the unsigned rego file
            rego_str = load_str_from_file(filename2)
            # see if the import statement is in the rego file
            self.assertTrue("test_feed" in rego_str)
            self.assertTrue(out_path not in rego_str)
            # make sure the image covered by the first fragment isn't in the second fragment
            self.assertFalse("mcr.microsoft.com/acc/samples/aci/helloworld:2.9" in rego_str)
        except Exception as e:
            raise e
        finally:
            delete_silently([filename, out_path, filename2, out_path2, fragment_json])


class FragmentVirtualNode(unittest.TestCase):
    custom_json = """
{
    "version": "1.0",
    "scenario": "vn2",
    "labels": {
        "azure.workload.identity/use": true
    },
    "containers": [
        {
            "name": "test-container",
            "properties": {
                "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": ".+",
                        "regex": true
                    }
                ],
                "command": [
                    "/bin/sh",
                    "-c",
                    "while true; do echo 'Hello World'; done"
                ],
                "securityContext": {
                    "privileged": true
                }
            }
        }
    ]
}
"""
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_json(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

    def test_fragment_vn2_env_vars(self):
        image = self.aci_policy.get_images()[0]
        env_names = [i.get('pattern') for i in image._get_environment_rules()]
        env_rules = [f"{i.get('name')}={i.get('value')}" for i in config.VIRTUAL_NODE_ENV_RULES]
        for env_rule in env_rules:
            self.assertIn(env_rule, env_names)

    def test_fragment_vn2_workload_identity_env_vars(self):
        image = self.aci_policy.get_images()[0]
        env_names = [i.get('pattern') for i in image._get_environment_rules()]
        env_rules = [f"{i.get('name')}={i.get('value')}" for i in config.VIRTUAL_NODE_ENV_RULES_WORKLOAD_IDENTITY]
        for env_rule in env_rules:
            self.assertIn(env_rule, env_names)

    def test_fragment_vn2_user_mounts(self):
        image = self.aci_policy.get_images()[0]
        mount_destinations = [i.get('destination') for i in image._get_mounts_json()]
        default_mounts = [i.get('mountPath') for i in config.DEFAULT_MOUNTS_VIRTUAL_NODE + config.DEFAULT_MOUNTS_USER_VIRTUAL_NODE]
        for default_mount in default_mounts:
            self.assertIn(default_mount, mount_destinations)

    def test_fragment_vn2_privileged_mounts(self):
        image = self.aci_policy.get_images()[0]
        mount_destinations = [i.get('destination') for i in image._get_mounts_json()]
        default_mounts = [i.get('mountPath') for i in config.DEFAULT_MOUNTS_PRIVILEGED_VIRTUAL_NODE]
        for default_mount in default_mounts:
            self.assertIn(default_mount, mount_destinations)

    def test_fragment_vn2_workload_identity_mounts(self):
        image = self.aci_policy.get_images()[0]
        mount_destinations = [i.get('destination') for i in image._get_mounts_json()]
        default_mounts = [i.get('mountPath') for i in config.DEFAULT_MOUNTS_WORKLOAD_IDENTITY_VIRTUAL_NODE]
        for default_mount in default_mounts:
            self.assertIn(default_mount, mount_destinations)


# class FragmentRegistryInteractions(ScenarioTest):
#     custom_json = """
# {
#     "version": "1.0",
#     "fragments": [
#     ],
#     "containers": [
#         {
#             "name": "my-image2",
#             "properties": {
#                 "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
#                 "execProcesses": [
#                     {
#                         "command": [
#                             "echo",
#                             "Hello World"
#                         ]
#                     }
#                 ],
#                 "volumeMounts": [
#                     {
#                         "name": "azurefile",
#                         "mountPath": "/mount/azurefile",
#                         "mountType": "azureFile",
#                         "readOnly": true
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "PATH",
#                         "value": "/customized/path/value"
#                     },
#                     {
#                         "name": "TEST_REGEXP_ENV",
#                         "value": "test_regexp_env(.*)",
#                         "regex": true
#                     }
#                 ]
#             }
#         }
#     ]
# }
#     """


#     custom_json2 = """
# {
#     "version": "1.0",
#     "fragments": [
#     ],
#     "containers": [
#         {
#             "name": "my-image",
#             "properties": {
#                 "image": "mcr.microsoft.com/azurelinux/busybox:1.36",
#                 "execProcesses": [
#                     {
#                         "command": [
#                             "sleep",
#                             "infinity"
#                         ]
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "PATH",
#                         "value": "/another/customized/path/value"
#                     },
#                     {
#                         "name": "TEST_REGEXP_ENV2",
#                         "value": "test_regexp_env2(.*)",
#                         "regex": true
#                     }
#                 ]
#             }
#         },
#         {
#             "name": "my-image2",
#             "properties": {
#                 "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
#                 "execProcesses": [
#                     {
#                         "command": [
#                             "echo",
#                             "Hello World"
#                         ]
#                     }
#                 ],
#                 "volumeMounts": [
#                     {
#                         "name": "azurefile",
#                         "mountPath": "/mount/azurefile",
#                         "mountType": "azureFile",
#                         "readOnly": true
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "PATH",
#                         "value": "/customized/path/value"
#                     },
#                     {
#                         "name": "TEST_REGEXP_ENV",
#                         "value": "test_regexp_env(.*)",
#                         "regex": true
#                     }
#                 ]
#             }
#         }
#     ]
# }
# """

#     custom_json3 = """
#     {
#         "version": "1.0",
#         "fragments": [
#         ],
#         "containers": [
#             {
#                 "name": "my-image",
#                 "properties": {
#                     "image": "localhost:5000/helloworld:2.9",
#                     "execProcesses": [
#                         {
#                             "command": [
#                                 "echo",
#                                 "Hello World"
#                             ]
#                         }
#                     ],
#                     "volumeMounts": [
#                         {
#                             "name": "azurefile",
#                             "mountPath": "/mount/azurefile",
#                             "mountType": "azureFile",
#                             "readOnly": true
#                         }
#                     ],
#                     "environmentVariables": [
#                         {
#                             "name": "PATH",
#                             "value": "/customized/path/value"
#                         },
#                         {
#                             "name": "TEST_REGEXP_ENV",
#                             "value": "test_regexp_env(.*)",
#                             "regex": true
#                         }
#                     ]
#                 }
#             }
#         ]
#     }
#     """

#     @classmethod
#     def setUpClass(cls):
#         # start the zot registry
#         cls.zot_image = "ghcr.io/project-zot/zot-linux-amd64:latest"
#         cls.registry = "localhost:5000"
#         registry_name = "myregistry"

#         # Initialize Docker client
#         try:
#             with DockerClient() as client:
#                 client.images.pull(cls.zot_image)

#                 # Replace output = subprocess.run("docker ps -a", capture_output=True, shell=True)
#                 # Check if container already exists
#                 existing_containers = client.containers.list(all=True, filters={"name": registry_name})

#                 # Replace subprocess.run(f"docker run --name {registry_name} -d -p 5000:5000 {cls.zot_image}", shell=True)
#                 if not existing_containers:
#                     try:
#                         client.containers.run(
#                             cls.zot_image,
#                             name=registry_name,
#                             ports={'5000/tcp': 5000},
#                             detach=True
#                         )
#                     except docker.errors.APIError as e:
#                         raise Exception(f"Error starting registry container: {e}")
#                 else:
#                     # Start the container if it exists but is not running
#                     container = existing_containers[0]
#                     if container.status != 'running':
#                         container.start()
#         except docker.errors.ImageNotFound:
#             raise Exception(f"Could not pull image {cls.zot_image}")
#         except docker.errors.APIError as e:
#             raise Exception(f"Error pulling image {cls.zot_image}: {e}")
#         except docker.errors.DockerException as e:
#             raise Exception(f"Docker is not available: {e}")

#         cls.key_dir_parent = os.path.join(SAMPLES_DIR, 'certs')
#         cls.key = os.path.join(cls.key_dir_parent, 'intermediateCA', 'private', 'ec_p384_private.pem')
#         cls.chain = os.path.join(cls.key_dir_parent, 'intermediateCA', 'certs', 'www.contoso.com.chain.cert.pem')
#         if not os.path.exists(cls.key) or not os.path.exists(cls.chain):
#             script_path = os.path.join(cls.key_dir_parent, 'create_certchain.sh')

#             arg_list = [
#                 script_path,
#             ]
#             os.chmod(script_path, 0o755)

#             # NOTE: this will raise an exception if it's run on windows and the key/cert files don't exist
#             item = subprocess.run(
#                 arg_list,
#                 check=False,
#                 shell=True,
#                 cwd=cls.key_dir_parent,
#                 env=os.environ.copy(),
#             )

#             if item.returncode != 0:
#                 raise Exception("Error creating certificate chain")

#         with load_policy_from_json(cls.custom_json) as aci_policy:
#             aci_policy.populate_policy_content_for_all_images()
#             cls.aci_policy = aci_policy
#         with load_policy_from_json(cls.custom_json2) as aci_policy2:
#             aci_policy2.populate_policy_content_for_all_images()
#             cls.aci_policy2 = aci_policy2

#         # stall while we wait for the registry to start running
#         result = requests.get(f"http://{cls.registry}/v2/_catalog")
#         counter = 0
#         retry_limit = 10
#         while result.status_code != 200:
#             time.sleep(1)
#             result = requests.get(f"http://{cls.registry}/v2/_catalog")
#             counter += 1
#             if counter == retry_limit:
#                 raise Exception("Could not start local registry in time")


#     def test_generate_import_from_remote(self):
#         filename = "payload5.rego"
#         feed = f"{self.registry}/test_feed:test_tag"
#         algo = "ES384"
#         out_path = filename + ".cose"

#         fragment_text = self.aci_policy.generate_fragment("payload4", "1", OutputType.RAW)
#         temp_filename = "temp.json"
#         try:
#             write_str_to_file(filename, fragment_text)

#             cose_proxy = CoseSignToolProxy()
#             iss = cose_proxy.create_issuer(self.chain)
#             cose_proxy.cose_sign(filename, self.key, self.chain, feed, iss, algo, out_path)
#             push_fragment_to_registry(feed, out_path)

#             # this should download and create the import statement
#             acifragmentgen_confcom(None, None, None, None, None, None, None, None, "1", generate_import=True, fragment_path=feed, fragments_json=temp_filename)
#             import_file = load_json_from_file(temp_filename)
#             import_statement = import_file.get(config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS)[0]

#             self.assertTrue(import_statement)
#             self.assertEqual(
#                 import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISSUER,""),iss
#             )
#             self.assertEqual(
#                 import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED,""),feed
#             )
#             self.assertEqual(
#                 import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN,""), "1"
#             )
#             self.assertEqual(
#                 import_statement.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_INCLUDES,[]),[config.POLICY_FIELD_CONTAINERS, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS]
#             )

#         except Exception as e:
#             raise e
#         finally:
#             delete_silently([filename, out_path, temp_filename])

    # def test_remote_fragment_references(self):
    #     filename = "payload6.rego"
    #     filename2 = "payload7.rego"
    #     first_fragment = "first_fragment.json"
    #     fragment_json = "fragment_remote.json"
    #     feed = f"{self.registry}/test_feed:v1"
    #     feed2 = f"{self.registry}/test_feed2:v2"
    #     out_path = filename + ".cose"
    #     out_path2 = filename2 + ".cose"

    #     # fragment_text = self.aci_policy.generate_fragment("payload6", 1, OutputType.RAW)

    #     try:
    #         write_str_to_file(first_fragment, self.custom_json)
    #         write_str_to_file(fragment_json, self.custom_json2)
    #         acifragmentgen_confcom(
    #             None, first_fragment, None, "payload7", "1", feed, self.key, self.chain, None, output_filename=filename
    #         )

    #         # this will insert the import statement from the first fragment into the second one
    #         acifragmentgen_confcom(
    #             None, None, None, None, None, None, None, None, generate_import=True, minimum_svn="1", fragments_json=fragment_json, fragment_path=out_path
    #         )

    #         push_fragment_to_registry(feed, out_path)

    #         acifragmentgen_confcom(
    #             None, fragment_json, None, "payload7", "1", feed2, self.key, self.chain, None, output_filename=filename2
    #         )

    #         # make sure all of our output files exist
    #         self.assertTrue(os.path.exists(filename2))
    #         self.assertTrue(os.path.exists(out_path2))
    #         self.assertTrue(os.path.exists(fragment_json))
    #         # check the contents of the unsigned rego file
    #         rego_str = load_str_from_file(filename2)
    #         # see if the import statement is in the rego file
    #         self.assertTrue(feed in rego_str)
    #         # make sure the image covered by the first fragment isn't in the second fragment
    #         self.assertFalse("mcr.microsoft.com/acc/samples/aci/helloworld:2.9" in rego_str)
    #     except Exception as e:
    #         raise e
    #     finally:
    #         delete_silently([filename, out_path, filename2, out_path2, fragment_json, first_fragment])

    # def test_incorrect_minimum_svn(self):
    #     filename = "payload8.rego"
    #     filename2 = "payload9.rego"
    #     fragment_json = "fragment.json"
    #     feed = f"{self.registry}/test_feed:v3"
    #     feed2 = f"{self.registry}/test_feed2:v4"
    #     algo = "ES384"
    #     out_path = filename + ".cose"
    #     out_path2 = filename2 + ".cose"

    #     fragment_text = self.aci_policy.generate_fragment("payload8", "1", OutputType.RAW)

    #     try:
    #         write_str_to_file(filename, fragment_text)
    #         write_str_to_file(fragment_json, self.custom_json2)

    #         cose_proxy = CoseSignToolProxy()
    #         iss = cose_proxy.create_issuer(self.chain)
    #         cose_proxy.cose_sign(filename, self.key, self.chain, feed, iss, algo, out_path)


    #         # this will insert the import statement from the first fragment into the second one
    #         acifragmentgen_confcom(
    #             None, None, None, None, None, None, None, None, generate_import=True, minimum_svn="2", fragments_json=fragment_json, fragment_path=out_path
    #         )
    #         # put the "path" field into the import statement
    #         push_fragment_to_registry(feed, out_path)
    #         acifragmentgen_confcom(
    #             None, fragment_json, None, "payload9", "1", feed2, self.key, self.chain, None, output_filename=filename2
    #         )

    #         # make sure all of our output files exist
    #         self.assertTrue(os.path.exists(filename2))
    #         self.assertTrue(os.path.exists(out_path2))
    #         self.assertTrue(os.path.exists(fragment_json))
    #         # check the contents of the unsigned rego file
    #         rego_str = load_str_from_file(filename2)
    #         # see if the import statement is in the rego file
    #         self.assertTrue("test_feed" in rego_str)
    #         # make sure the image covered by the first fragment is in the second fragment because the svn prevents usage
    #         self.assertTrue("mcr.microsoft.com/acc/samples/aci/helloworld:2.9" in rego_str)
    #     except Exception as e:
    #         raise e
    #     finally:
    #         delete_silently([filename, out_path, filename2, out_path2, fragment_json])

    # def test_image_attached_fragment_coverage(self):
    #     # Initialize Docker client
    #     try:
    #         with DockerClient() as client:
    #              # Replace subprocess.run(f"docker tag mcr.microsoft.com/acc/samples/aci/helloworld:2.9 {self.registry}/helloworld:2.9", shell=True)
    #             try:
    #                 source_image = client.images.get("mcr.microsoft.com/acc/samples/aci/helloworld:2.9")
    #                 source_image.tag(f"{self.registry}/helloworld:2.9")
    #             except docker.errors.ImageNotFound:
    #                 # Try to pull the image first
    #                 try:
    #                     client.images.pull("mcr.microsoft.com/acc/samples/aci/helloworld:2.9")
    #                     source_image = client.images.get("mcr.microsoft.com/acc/samples/aci/helloworld:2.9")
    #                     source_image.tag(f"{self.registry}/helloworld:2.9")
    #                 except docker.errors.APIError as e:
    #                     raise Exception(f"Could not pull or tag image: {e}")
    #             except docker.errors.APIError as e:
    #                 raise Exception(f"Error tagging image: {e}")

    #              # Replace subprocess.run(f"docker push {self.registry}/helloworld:2.9", timeout=30, shell=True)
    #             try:
    #                 # Note: Docker SDK push returns a generator of status updates
    #                 push_logs = client.images.push(f"{self.registry}/helloworld:2.9", stream=True, decode=True)
    #                 # Consume the generator to ensure push completes
    #                 for log in push_logs:
    #                     if 'error' in log:
    #                         raise Exception(f"Push failed: {log['error']}")
    #             except docker.errors.APIError as e:
    #                 raise Exception(f"Error pushing image: {e}")
    #     except docker.errors.DockerException as e:
    #         raise Exception(f"Docker is not available: {e}")

    #     filename = "container_image_attached.json"
    #     rego_filename = "temp_namespace"
    #     try:
    #         write_str_to_file(filename, self.custom_json3)
    #         acifragmentgen_confcom(
    #             None,
    #             filename,
    #             None,
    #             rego_filename,
    #             "1",
    #             "temp_feed",
    #             self.key,
    #             self.chain,
    #             "1",
    #             f"{self.registry}/helloworld:2.9",
    #             upload_fragment=True,
    #         )


    #         # this will insert the import statement into the original container.json
    #         acifragmentgen_confcom(
    #             f"{self.registry}/helloworld:2.9", None, None, None, None, None, None, None, generate_import=True, minimum_svn="1", fragments_json=filename
    #         )

    #         # try to generate the policy again to make sure there are no containers in the resulting rego
    #         with self.assertRaises(SystemExit) as exc_info:
    #             acifragmentgen_confcom(
    #                 None,
    #                 filename,
    #                 None,
    #                 "temp_namespace2",
    #                 "1",
    #                 "temp_feed2",
    #                 None,
    #                 None,
    #                 "1",
    #                 f"{self.registry}/helloworld:2.9",
    #             )
    #         self.assertEqual(exc_info.exception.code, 1)

    #     except Exception as e:
    #         raise e
    #     finally:
    #         force_delete_silently([filename, f"{rego_filename}.rego", f"{rego_filename}.rego.cose"])

    # def test_incorrect_pull_location(self):
    #     with self.assertRaises(SystemExit) as exc_info:
    #         _ = pull(f"{self.registry}/fake_artifact")
    #     self.assertEqual(exc_info.exception.code, 1)

    # def test_reserved_namespace(self):
    #     filename = "container_image_attached2.json"
    #     rego_filename = "policy"
    #     with self.assertRaises(CLIError) as exc_info:
    #         try:
    #             write_str_to_file(filename, self.custom_json)
    #             self.cmd(f"confcom acifragmentgen -i {filename} --namespace policy --svn 1")
    #         except Exception as e:
    #             raise e
    #         finally:
    #             force_delete_silently([filename, f"{rego_filename}.rego"])

    # def test_invalid_svn(self):
    #     filename = "container_image_attached3.json"
    #     rego_filename = "myfile"
    #     with self.assertRaises(CLIError) as exc_info:
    #         try:
    #             write_str_to_file(filename, self.custom_json)
    #             self.cmd(f"confcom acifragmentgen -i {filename} --namespace policy --svn 0")
    #         except Exception as e:
    #             raise e
    #         finally:
    #             force_delete_silently([filename, f"{rego_filename}.rego"])

# class ExtendedFragmentTests(ScenarioTest):
#     """Extended test cases for fragment operations following the requested scenarios."""

#     custom_json_multi_container = """
# {
#     "version": "1.0",
#     "fragments": [],
#     "containers": [
#         {
#             "name": "first-container",
#             "properties": {
#                 "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
#                 "execProcesses": [
#                     {
#                         "command": ["echo", "First Container"]
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "CONTAINER_TYPE",
#                         "value": "first"
#                     }
#                 ]
#             }
#         },
#         {
#             "name": "second-container",
#             "properties": {
#                 "image": "mcr.microsoft.com/azurelinux/busybox:1.36",
#                 "execProcesses": [
#                     {
#                         "command": ["echo", "Second Container"]
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "CONTAINER_TYPE",
#                         "value": "second"
#                     }
#                 ]
#             }
#         }
#     ]
# }
#     """

#     custom_json_stdio_disabled = """
# {
#     "version": "1.0",
#     "fragments": [],
#     "containers": [
#         {
#             "name": "stdio-disabled-container",
#             "properties": {
#                 "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
#                 "execProcesses": [
#                     {
#                         "command": ["echo", "No stdio access"]
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "STDIO_DISABLED",
#                         "value": "true"
#                     }
#                 ]
#             }
#         }
#     ]
# }
#     """

#     @classmethod
#     def setUpClass(cls):
#         cls.registry = "localhost:5000"
#         cls.key_dir_parent = os.path.join(SAMPLES_DIR, 'certs')
#         cls.key = os.path.join(cls.key_dir_parent, 'intermediateCA', 'private', 'ec_p384_private.pem')
#         cls.chain = os.path.join(cls.key_dir_parent, 'intermediateCA', 'certs', 'www.contoso.com.chain.cert.pem')

    # def test_upload_signed_fragment_to_registry(self):
    #     """Test uploading a signed fragment to the registry."""
    #     filename = "signed_fragment.rego"
    #     feed = f"{self.registry}/signed_fragment:v1"
    #     algo = "ES384"
    #     out_path = filename + ".cose"

    #     try:
    #         # Create a simple fragment policy
    #         with load_policy_from_json(self.custom_json_multi_container) as policy:
    #             policy.populate_policy_content_for_all_images()
    #             fragment_text = policy.generate_fragment("signed_fragment", "1", OutputType.RAW)

    #         write_str_to_file(filename, fragment_text)

    #         # Sign and upload to registry
    #         cose_proxy = CoseSignToolProxy()
    #         iss = cose_proxy.create_issuer(self.chain)
    #         cose_proxy.cose_sign(filename, self.key, self.chain, feed, iss, algo, out_path)

    #         # Upload to registry
    #         push_fragment_to_registry(feed, out_path)

    #         # Verify we can pull it back
    #         pulled_fragment = pull(feed)
    #         self.assertIsNotNone(pulled_fragment)

    #     except Exception as e:
    #         raise e
    #     finally:
    #         force_delete_silently([filename, out_path])

    # def test_attach_fragment_to_different_image(self):
    #     """Test attaching a fragment to a different image than the one it was created for."""
    #     filename = "different_image_fragment.json"
    #     rego_filename = "different_image_rego"

    #     try:
    #         write_str_to_file(filename, self.custom_json_multi_container)

    #         # Create fragment for first image but try to attach to second
    #         acifragmentgen_confcom(
    #             None,
    #             filename,
    #             None,
    #             rego_filename,
    #             "1",
    #             "test_feed_different",
    #             self.key,
    #             self.chain,
    #             "1",
    #             "mcr.microsoft.com/azurelinux/busybox:1.36",  # Different from the one in JSON
    #             upload_fragment=False,
    #         )

    #         # Verify the fragment was created
    #         self.assertTrue(os.path.exists(f"{rego_filename}.rego"))

    #     except Exception as e:
    #         raise e
    #     finally:
    #         force_delete_silently([filename, f"{rego_filename}.rego", f"{rego_filename}.rego.cose"])

#     def test_remote_pull_failure_path(self):
#         """Test failure path when trying to pull from non-existent registry location."""
#         with self.assertRaises(SystemExit) as exc_info:
#             _ = pull(f"{self.registry}/nonexistent_fragment:v1")
#         self.assertEqual(exc_info.exception.code, 1)

#     def test_mixed_fragments_and_standalone_fragments_import(self):
#         """Test import JSON with both 'fragments' and 'standaloneFragments' sections."""
#         mixed_json = """
# {
#     "version": "1.0",
#     "fragments": [
#         {
#             "feed": "localhost:5000/fragment1:v1",
#             "issuer": "test_issuer",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }
#     ],
#     "standaloneFragments": [
#         {
#             "feed": "localhost:5000/standalone1:v1",
#             "issuer": "test_issuer",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }
#     ],
#     "containers": []
# }
#         """

#         filename = "mixed_fragments.json"
#         try:
#             write_str_to_file(filename, mixed_json)

#             # This should handle both fragment types
#             with load_policy_from_json(mixed_json) as policy:
#                 policy.populate_policy_content_for_all_images()
#                 output = policy.generate_fragment("mixed_fragments", "1", OutputType.RAW)
#                 self.assertIsNotNone(output)

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently(filename)

#     def test_import_json_as_array(self):
#         """Test import JSON that is just an array instead of object."""
#         array_json = """
# [
#     {
#         "feed": "localhost:5000/array_fragment:v1",
#         "issuer": "test_issuer",
#         "minimum_svn": "1",
#         "includes": ["containers", "fragments"]
#     }
# ]
#         """

#         filename = "array_import.json"
#         try:
#             write_str_to_file(filename, array_json)

#             # This should fail or handle gracefully
#             with self.assertRaises((ValueError, CLIError, SystemExit)):
#                 with load_policy_from_json(array_json) as policy:
#                     policy.populate_policy_content_for_all_images()

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently(filename)

#     def test_disable_stdio_access(self):
#         """Test fragment generation with stdio access disabled."""
#         filename = "stdio_disabled.json"
#         rego_filename = "stdio_disabled_rego"

#         try:
#             write_str_to_file(filename, self.custom_json_stdio_disabled)

#             acifragmentgen_confcom(
#                 None,
#                 filename,
#                 None,
#                 rego_filename,
#                 "1",
#                 "stdio_test_feed",
#                 None,
#                 None,
#                 None,
#                 disable_stdio=True,
#             )

#             # Verify stdio access is disabled in the generated policy
#             rego_content = load_str_from_file(f"{rego_filename}.rego")
#             containers, _ = decompose_confidential_properties(str_to_base64(rego_content))

#             # Check that stdio access is disabled
#             self.assertFalse(containers[0].get("allow_stdio_access", True))

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently([filename, f"{rego_filename}.rego"])

#     def test_tar_input_processing(self):
#         """Test processing tar and tar-mapping inputs."""
#         tar_filename = "test_input.tar"
#         mapping_filename = "test_mapping.json"

#         try:
#             # Create a simple tar mapping
#             tar_mapping = {
#                 "tar_file": tar_filename,
#                 "containers": [
#                     {
#                         "name": "tar-container",
#                         "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9"
#                     }
#                 ]
#             }

#             write_str_to_file(mapping_filename, json.dumps(tar_mapping))

#             # Create empty tar file for testing
#             with open(tar_filename, 'wb') as f:
#                 f.write(b'')

#             # This should handle tar input gracefully or fail with appropriate error
#             with self.assertRaises((FileNotFoundError, CLIError, SystemExit)):
#                 acifragmentgen_confcom(
#                     None,
#                     mapping_filename,
#                     tar_filename,
#                     "tar_test_rego",
#                     "1",
#                     "tar_test_feed",
#                     None,
#                     None,
#                     None
#                 )

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently([tar_filename, mapping_filename])

#     def test_fragment_target_image_consistency(self):
#         """Test that fragment always lands on the intended image with and without --image-target."""
#         filename = "target_consistency.json"
#         rego_filename = "target_consistency_rego"
#         target_image = "mcr.microsoft.com/acc/samples/aci/helloworld:2.9"

#         try:
#             write_str_to_file(filename, self.custom_json_multi_container)

#             # Test with explicit image target
#             acifragmentgen_confcom(
#                 None,
#                 filename,
#                 None,
#                 rego_filename,
#                 "1",
#                 "target_test_feed",
#                 None,
#                 None,
#                 "1",
#                 target_image
#             )

#             # Verify the fragment contains the correct image
#             rego_content = load_str_from_file(f"{rego_filename}.rego")
#             self.assertIn(target_image, rego_content)

#             # Test without explicit image target (should use from JSON)
#             acifragmentgen_confcom(
#                 None,
#                 filename,
#                 None,
#                 f"{rego_filename}_no_target",
#                 "1",
#                 "target_test_feed_2",
#                 None,
#                 None,
#                 None
#             )

#             # Should contain images from JSON
#             rego_content_2 = load_str_from_file(f"{rego_filename}_no_target.rego")
#             self.assertIn("mcr.microsoft.com/acc/samples/aci/helloworld:2.9", rego_content_2)

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently([filename, f"{rego_filename}.rego", f"{rego_filename}_no_target.rego"])

#     def test_two_imports_same_feed_different_namespaces(self):
#         """Test two imports that reference the same feed but expect different namespaces."""
#         # Note: This is actually testing an edge case where the same feed is referenced
#         # but the system might expect different namespace handling
#         container_json = """
# {
#     "version": "1.0",
#     "containers": [
#         {
#             "name": "shared-feed-container",
#             "properties": {
#                 "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
#                 "execProcesses": [
#                     {
#                         "command": ["echo", "Shared Feed Test"]
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "SHARED_FEED_TEST",
#                         "value": "true"
#                     }
#                 ]
#             }
#         }
#     ]
# }
#         """

#         feed = f"{self.registry}/shared_feed:v1"
#         namespace = "actual_namespace"

#         fragment_file = "shared_feed_fragment.rego"
#         container_file = "shared_feed_container.json"
#         import_file = "same_feed_diff_namespace.json"

#         try:
#             write_str_to_file(container_file, container_json)

#             # Create and push fragment with a specific namespace
#             with load_policy_from_json(container_json) as policy:
#                 policy.populate_policy_content_for_all_images()
#                 fragment_text = policy.generate_fragment(namespace, "1", OutputType.RAW)

#             write_str_to_file(fragment_file, fragment_text)

#             # Sign and push fragment
#             cose_proxy = CoseSignToolProxy()
#             iss = cose_proxy.create_issuer(self.chain)
#             cose_proxy.cose_sign(fragment_file, self.key, self.chain, feed, iss, "ES384", fragment_file + ".cose")
#             push_fragment_to_registry(feed, fragment_file + ".cose")

#             # Create import JSON that references the same feed twice
#             # The system should handle this gracefully since it's the same fragment
#             import_json = f"""
# {{
#     "version": "1.0",
#     "fragments": [
#         {{
#             "feed": "{feed}",
#             "issuer": "{iss}",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }},
#         {{
#             "feed": "{feed}",
#             "issuer": "{iss}",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }}
#     ],
#     "containers": []
# }}
#             """

#             write_str_to_file(import_file, import_json)

#             # This should work since it's the same feed/fragment being referenced twice
#             with load_policy_from_json(import_json) as policy:
#                 policy.populate_policy_content_for_all_images()
#                 output = policy.generate_fragment("same_feed_diff_namespace", "1", OutputType.RAW)
#                 self.assertIsNotNone(output)

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently([container_file, fragment_file, fragment_file + ".cose", import_file])

#     def test_two_imports_same_feed_and_namespace(self):
#         """Test two imports that share both feed and namespace."""
#         # Create a single fragment and try to import it twice
#         container_json = """
# {
#     "version": "1.0",
#     "containers": [
#         {
#             "name": "duplicate-test-container",
#             "properties": {
#                 "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
#                 "execProcesses": [
#                     {
#                         "command": ["echo", "Duplicate Test"]
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "DUPLICATE_TEST",
#                         "value": "true"
#                     }
#                 ]
#             }
#         }
#     ]
# }
#         """

#         feed = f"{self.registry}/duplicate_feed:v1"
#         namespace = "duplicate_namespace"

#         fragment_file = "duplicate_fragment.rego"
#         container_file = "duplicate_container.json"
#         import_file = "duplicate_imports.json"

#         try:
#             write_str_to_file(container_file, container_json)

#             # Create and push fragment
#             with load_policy_from_json(container_json) as policy:
#                 policy.populate_policy_content_for_all_images()
#                 fragment_text = policy.generate_fragment(namespace, "1", OutputType.RAW)

#             write_str_to_file(fragment_file, fragment_text)

#             # Sign and push fragment
#             cose_proxy = CoseSignToolProxy()
#             iss = cose_proxy.create_issuer(self.chain)
#             cose_proxy.cose_sign(fragment_file, self.key, self.chain, feed, iss, "ES384", fragment_file + ".cose")
#             push_fragment_to_registry(feed, fragment_file + ".cose")

#             # Create import JSON that references the same fragment twice
#             import_json = f"""
# {{
#     "version": "1.0",
#     "fragments": [
#         {{
#             "feed": "{feed}",
#             "issuer": "{iss}",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }},
#         {{
#             "feed": "{feed}",
#             "issuer": "{iss}",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }}
#     ],
#     "containers": []
# }}
#             """

#             write_str_to_file(import_file, import_json)

#             # This should either deduplicate gracefully or handle duplicate imports appropriately
#             with load_policy_from_json(import_json) as policy:
#                 policy.populate_policy_content_for_all_images()
#                 output = policy.generate_fragment("duplicate_imports", "1", OutputType.RAW)
#                 self.assertIsNotNone(output)

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently([container_file, fragment_file, fragment_file + ".cose", import_file])

#     def test_two_imports_same_namespace_different_feeds(self):
#         """Test two imports that share namespace but have different feeds."""
#         # Create two fragments with the same namespace but different feeds
#         container_json = """
# {
#     "version": "1.0",
#     "containers": [
#         {
#             "name": "test-container",
#             "properties": {
#                 "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
#                 "execProcesses": [
#                     {
#                         "command": ["echo", "Hello World"]
#                     }
#                 ],
#                 "environmentVariables": [
#                     {
#                         "name": "PATH",
#                         "value": "/usr/local/bin"
#                     }
#                 ]
#             }
#         }
#     ]
# }
#         """

#         feed1 = f"{self.registry}/feed1:v1"
#         feed2 = f"{self.registry}/feed2:v1"
#         same_namespace = "conflicting_namespace"

#         fragment1_file = "fragment1.rego"
#         fragment2_file = "fragment2.rego"
#         container_file = "container.json"
#         import_file = "same_namespace_diff_feeds.json"

#         try:
#             write_str_to_file(container_file, container_json)

#             # Create first fragment with specific namespace
#             with load_policy_from_json(container_json) as policy:
#                 policy.populate_policy_content_for_all_images()
#                 fragment1_text = policy.generate_fragment(same_namespace, "1", OutputType.RAW)

#             write_str_to_file(fragment1_file, fragment1_text)

#             # Sign and push first fragment
#             cose_proxy = CoseSignToolProxy()
#             iss = cose_proxy.create_issuer(self.chain)
#             cose_proxy.cose_sign(fragment1_file, self.key, self.chain, feed1, iss, "ES384", fragment1_file + ".cose")
#             push_fragment_to_registry(feed1, fragment1_file + ".cose")

#             # Create second fragment with same namespace
#             fragment2_text = policy.generate_fragment(same_namespace, "1", OutputType.RAW)
#             write_str_to_file(fragment2_file, fragment2_text)

#             # Sign and push second fragment
#             cose_proxy.cose_sign(fragment2_file, self.key, self.chain, feed2, iss, "ES384", fragment2_file + ".cose")
#             push_fragment_to_registry(feed2, fragment2_file + ".cose")

#             # Create import JSON that references both fragments
#             import_json = f"""
# {{
#     "version": "1.0",
#     "fragments": [
#         {{
#             "feed": "{feed1}",
#             "issuer": "{iss}",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }},
#         {{
#             "feed": "{feed2}",
#             "issuer": "{iss}",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }}
#     ],
#     "containers": []
# }}
#             """

#             write_str_to_file(import_file, import_json)

#             # This should fail due to namespace conflict when fragments are evaluated
#             with self.assertRaises((CLIError, SystemExit, ValueError)):
#                 acipolicygen_confcom(
#                     import_file,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     include_fragments=True,
#                 )

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently([container_file, fragment1_file, fragment1_file + ".cose", fragment2_file, fragment2_file + ".cose", import_file])

#     def test_mixed_case_feed_namespace_strings(self):
#         """Test handling of mixed case feed and namespace strings."""
#         mixed_case_json = """
# {
#     "version": "1.0",
#     "fragments": [
#         {
#             "feed": "localhost:5000/MixedCase_Feed:V1",
#             "issuer": "Test_Issuer",
#             "minimum_svn": "1",
#             "includes": ["containers", "fragments"]
#         }
#     ],
#     "containers": []
# }
#         """

#         filename = "mixed_case.json"
#         try:
#             write_str_to_file(filename, mixed_case_json)

#             with load_policy_from_json(mixed_case_json) as policy:
#                 policy.populate_policy_content_for_all_images()
#                 output = policy.generate_fragment("MixedCase_NameSpace", "1", OutputType.RAW)
#                 self.assertIsNotNone(output)

#                 # Verify case is preserved
#                 self.assertIn("MixedCase_Feed", output)
#                 self.assertIn("MixedCase_NameSpace", output)

#         except Exception as e:
#             raise e
#         finally:
#             force_delete_silently(filename)


class InitialFragmentErrors(ScenarioTest):
    def test_invalid_input(self):
        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --image mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 -i fakepath/parameters.json --namespace fake_namespace --svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide either an image name or an input file to generate a fragment")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --generate-import --minimum-svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide either a fragment path or " +
            "an image name to generate an import statement")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --image mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 -k fakepath/key.pem --namespace fake_namespace --svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide both --key and --chain to sign a fragment")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --fragment-path ./fragment.json --image mcr.microsoft.com/aci/msi-atlas-adapter:master_20201210.1 --namespace fake_namespace --svn 1 --minimum-svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Must provide --generate-import to specify a fragment path")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --input ./input.json --namespace example --svn -1")
        self.assertEqual(wrapped_exit.exception.args[0], "--svn must be an integer")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --input ./input.json --namespace policy --svn 1")
        self.assertEqual(wrapped_exit.exception.args[0], "Namespace 'policy' is reserved")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acifragmentgen --algo fake_algo --key ./key.pem --chain ./cert-chain.pem --namespace example --svn 1 -i ./input.json")
        self.assertEqual(wrapped_exit.exception.args[0], f"Algorithm 'fake_algo' is not supported. Supported algorithms are {config.SUPPORTED_ALGOS}")

    def test_reserved_namespace_validation(self):
        """Test additional reserved namespace validation scenarios."""

        for namespace in config.RESERVED_FRAGMENT_NAMES:
            filename = f"reserved_test_{namespace.lower()}.json"
            try:
                write_str_to_file(filename, """{"version": "1.0", "containers": [{"properties": {"image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9"}, "name": "hello"}]}""")

                with self.assertRaises(CLIError) as exc_info:
                    self.cmd(f"confcom acifragmentgen -i {filename} --namespace {namespace} --svn 1")

                self.assertIn("reserved", exc_info.exception.args[0].lower())

            finally:
                force_delete_silently(filename)

    def test_bad_svn_validation(self):
        """Test various invalid SVN values."""
        invalid_svns = ["-1", "abc", "1.5"]

        for svn in invalid_svns:
            filename = f"bad_svn_test_{hash(svn) % 1000}.json"
            try:
                write_str_to_file(filename,
                """{"version": "1.0", "containers": [{"properties": {"image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9"}, "name": "hello"}]}"""
                )

                with self.assertRaises(CLIError):
                    self.cmd(f"confcom acifragmentgen -i {filename} --namespace test --svn {svn}")

            finally:
                force_delete_silently(filename)


class FragmentContainerBindings(unittest.TestCase):
    def setUp(self):
        # Import after conftest.py run_on_wheel so these modules and our mocks
        # use the same wheel module instances.
        from azext_confcom import fragment_util, security_policy

        self.fragment_util = fragment_util
        self.security_policy = security_policy
        self.fragment = {
            "feed": "contoso.azurecr.io/example",
            "includes": ["containers"],
            "issuer": "did:x509:test",
            "minimum_svn": "1",
            "container_name": "app",
            "parameters": {"command": ["echo", "hello"]},
        }

    def _load_policy(self, source, containers, platform="linux/amd64", init_containers=None):
        if source == "json":
            return self.security_policy.load_policy_from_json(
                json.dumps({"version": "1.0", "containers": containers, "fragments": [self.fragment]}),
                platform=platform,
            )
        if source == "arm":
            return self.security_policy.load_policy_from_arm_template_str(
                json.dumps({
                    "resources": [{
                        "type": "Microsoft.ContainerInstance/containerGroups",
                        "properties": {"containers": containers, "initContainers": init_containers or []},
                    }],
                }),
                None,
                rego_imports=[self.fragment],
                platform=platform,
            )[0]
        return self.security_policy.load_policy_from_virtual_node_yaml_str(
            json.dumps({
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": "test-pod"},
                "spec": {"containers": containers, "initContainers": init_containers or []},
            }),
            rego_imports=[self.fragment],
            platform=platform,
        )[0]

    # Verify resolve_fragment_imports preserves per-import parameters and leaves the input unchanged.
    def test_resolve_fragment_imports_preserves_parameter_instances(self):
        fragment_without_container_name = {
            key: value for key, value in self.fragment.items() if key not in ("container_name", "parameters")
        }
        fragment_for_other_container = copy.deepcopy(self.fragment)
        fragment_for_other_container["container_name"] = "other"
        fragment_for_other_container["parameters"]["command"] = ["echo", "other"]
        fragment_without_parameters = dict(self.fragment)
        fragment_without_parameters.pop("parameters")
        fragments = [
            fragment_without_container_name,
            self.fragment,
            fragment_for_other_container,
            fragment_without_parameters,
        ]
        original_fragments = copy.deepcopy(fragments)

        # The second import for "app" is retained with parameters defaulted to {}.
        expected_fragment_with_default_parameters = dict(fragment_without_parameters)
        expected_fragment_with_default_parameters["parameters"] = {}

        fragments_without_container_name, fragments_by_container_name = self.fragment_util.resolve_fragment_imports(
            fragments, ["app", "other"]
        )

        self.assertEqual(fragments_without_container_name, [fragment_without_container_name])
        self.assertEqual(
            fragments_by_container_name["app"], [self.fragment, expected_fragment_with_default_parameters]
        )
        self.assertEqual(fragments_by_container_name["other"], [fragment_for_other_container])
        fragments_by_container_name["app"][0]["parameters"]["command"].append("changed")
        self.assertEqual(fragments, original_fragments)

    # Verify resolve_fragment_imports rejects invalid fields and parameters without a container_name.
    def test_resolve_fragment_imports_rejects_invalid_fields(self):
        for invalid_fields, expected_message in [
            ({"container_name": None}, "container_name must be a non-empty string"),
            ({"container_name": ""}, "container_name must be a non-empty string"),
            ({"container_name": " "}, "container_name must be a non-empty string"),
            ({"container_name": 1}, "container_name must be a non-empty string"),
            ({"parameters": []}, "parameters must be an object"),
            ({"parameters": None}, "parameters must be an object"),
            ({"minimum_svn": "invalid"}, "can only be a string with an integer value"),
        ]:
            with self.subTest(fields=invalid_fields):
                fragment_with_invalid_fields = dict(self.fragment)
                fragment_with_invalid_fields.update(invalid_fields)
                with self.assertLogs(level="ERROR") as error_logs:
                    with self.assertRaises(SystemExit):
                        self.fragment_util.resolve_fragment_imports([fragment_with_invalid_fields], ["app"])
                self.assertIn(expected_message, error_logs.output[0])

        with self.assertRaises(SystemExit):
            self.fragment_util.resolve_fragment_imports(["not an object"], ["app"])
        fragment_without_container_name = dict(self.fragment)
        fragment_without_container_name.pop("container_name")
        with self.assertLogs(level="ERROR") as error_logs:
            with self.assertRaises(SystemExit):
                self.fragment_util.resolve_fragment_imports([fragment_without_container_name], ["app"])
        self.assertIn(
            "container_name is required for fragment imports that specify parameters.", error_logs.output[0]
        )

    # Verify resolve_fragment_imports requires exactly one case-sensitive container name match.
    def test_resolve_fragment_imports_requires_one_exact_container_name_match(self):
        for container_names in ([], ["App"], ["app", "app"]):
            with self.subTest(container_names=container_names):
                with self.assertLogs(level="ERROR") as error_logs:
                    with self.assertRaises(SystemExit):
                        self.fragment_util.resolve_fragment_imports([self.fragment], container_names)
                expected_message = f"must match exactly one container; found {container_names.count('app')}"
                self.assertIn(expected_message, error_logs.output[0])

    # Verify get_all_fragment_contents only passes imports without container_name to the fragment pull function.
    def test_get_all_fragment_contents_skips_imports_with_container_name(self):
        fragment_without_container_name = {
            key: value for key, value in self.fragment.items() if key not in ("container_name", "parameters")
        }
        with patch(
            "azext_confcom.oras_proxy.pull_all_standalone_fragments", return_value=([], [])
        ) as pull_all_standalone_fragments:
            fragment_contents = self.fragment_util.get_all_fragment_contents(
                [], [fragment_without_container_name, self.fragment]
            )
        self.assertEqual(fragment_contents, [])
        pull_all_standalone_fragments.assert_called_once_with([fragment_without_container_name])

    # Verify policy loaders serialize fragment-only policies with the requested platform's container defaults.
    def test_policy_loaders_serialize_fragment_only_policies_for_requested_platform(self):
        for source in ("json", "arm", "yaml"):
            for platform in ("linux/amd64", "windows/amd64"):
                with self.subTest(source=source, platform=platform):
                    policy = self._load_policy(source, [{"name": "app"}], platform)
                    policy.populate_policy_content_for_all_images()
                    output = policy.get_serialized_output(self.security_policy.OutputType.RAW)
                    serialized_fragments = json.loads(extract_containers_from_text(output, "fragments := "))
                    expected_serialized_fragment = {
                        key: value for key, value in self.fragment.items() if key != "container_name"
                    }
                    self.assertIn(expected_serialized_fragment, serialized_fragments)
                    serialized_containers = json.loads(extract_containers_from_text(output, "containers := "))
                    expected_containers = config.DEFAULT_CONTAINERS if platform.startswith("linux") else []
                    self.assertEqual(serialized_containers, expected_containers)

    # Verify policy loaders retain inline containers without fragment imports alongside container-name imports.
    def test_policy_loaders_retain_containers_without_fragment_imports(self):
        image = "mcr.microsoft.com/azurelinux/distroless/base:3.0"
        for source in ("json", "arm", "yaml"):
            with self.subTest(source=source):
                container_without_fragment_import = {"name": "other", "properties": {"image": image}}
                if source == "yaml":
                    container_without_fragment_import = {"name": "other", "image": image}
                with patch("azext_confcom.security_policy.validate_image_platform"):
                    policy = self._load_policy(source, [{"name": "app"}, container_without_fragment_import])
                self.assertEqual([container.get_container_image() for container in policy.get_images()], [image])
                self.assertIn(self.fragment, policy.get_fragments())

    # Verify ARM and YAML loaders match init container names and reject names shared with regular containers.
    def test_policy_loaders_match_init_container_names_and_reject_duplicate_names(self):
        image = "mcr.microsoft.com/azurelinux/distroless/base:3.0"
        for source in ("arm", "yaml"):
            with self.subTest(source=source):
                regular_container = {"name": "other", "properties": {"image": image}}
                if source == "yaml":
                    regular_container = {"name": "other", "image": image}
                with patch("azext_confcom.security_policy.validate_image_platform"):
                    policy = self._load_policy(source, [regular_container], init_containers=[{"name": "app"}])
                self.assertEqual([container.get_container_image() for container in policy.get_images()], [image])
                self.assertIn(self.fragment, policy.get_fragments())
                with self.assertRaises(SystemExit):
                    self._load_policy(source, [{"name": "app"}], init_containers=[{"name": "app"}])

    # Verify loaders reject container_name matches in multiple container groups (ARM) or pods (YAML).
    def test_policy_loaders_reject_duplicate_container_names_across_container_groups_or_pods(self):
        container_group_resource = {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "properties": {"containers": [{"name": "app"}]},
        }
        pod = {"kind": "Pod", "metadata": {"name": "pod"}, "spec": {"containers": [{"name": "app"}]}}
        for source in ("arm", "yaml"):
            with self.subTest(source=source):
                with self.assertLogs(level="ERROR") as error_logs:
                    with self.assertRaises(SystemExit):
                        if source == "arm":
                            self.security_policy.load_policy_from_arm_template_str(
                                json.dumps({"resources": [container_group_resource, container_group_resource]}),
                                None,
                                rego_imports=[self.fragment],
                            )
                        else:
                            self.security_policy.load_policy_from_virtual_node_yaml_str(
                                json.dumps(pod) + "\n---\n" + json.dumps(pod),
                                rego_imports=[self.fragment],
                            )
                self.assertIn("must match exactly one container; found 2", error_logs.output[0])

    # Verify load_policy_from_arm_template_str accepts imports targeting parameter- or variable-based container names.
    def test_load_policy_from_arm_template_str_matches_parameter_and_variable_container_names(self):
        template = {
            "parameters": {"name": {"type": "string", "defaultValue": "default"}},
            "variables": {"name": "app"},
            "resources": [{
                "type": "Microsoft.ContainerInstance/containerGroups",
                "properties": {"containers": [{"name": "[parameters('name')]"}]},
            }],
        }
        for expression in ("[parameters('name')]", "[variables('name')]"):
            with self.subTest(expression=expression):
                template["resources"][0]["properties"]["containers"][0]["name"] = expression
                policies = self.security_policy.load_policy_from_arm_template_str(
                    json.dumps(template),
                    json.dumps({"parameters": {"name": {"value": "app"}}}),
                    rego_imports=[self.fragment],
                )
                self.assertEqual(policies[0].get_images(), [])
                self.assertIn(self.fragment, policies[0].get_fragments())


class FragmentEnvironmentRuleFormat(unittest.TestCase):
    def setUp(self):
        from azext_confcom import container, custom, security_policy, template_util

        self.container = container
        self.custom = custom
        self.security_policy = security_policy
        self.template_util = template_util

    def _generate(self, source="image", platform="linux/amd64", **kwargs):
        image = "contoso.azurecr.io/app:latest"
        image_info = {
            "Os": platform.split("/")[0],
            "Architecture": "amd64",
            "Env": ["IMAGE_ONLY=a=b", "OVERRIDE=image-value", "EMPTY="],
            "Cmd": ["app"],
            "WorkingDir": "/",
            "User": "",
        }
        with tempfile.TemporaryDirectory() as folder:
            input_path = Path(folder) / "input.json"
            input_path.write_text(json.dumps({
                "containers": [{
                    "name": "app",
                    "properties": {
                        "image": image,
                        "environmentVariables": [
                            {"name": "OVERRIDE", "value": "custom-value"},
                            {"name": "CUSTOM_.+", "value": "value=(one|two)", "regex": True},
                        ],
                    },
                }],
            }))
            output_path = Path(folder) / "output.rego"
            with patch.object(self.security_policy, "validate_image_platform"), \
                    patch.object(self.security_policy, "get_image_info", return_value=(image_info, None)), \
                    patch.object(self.security_policy, "SecurityPolicyProxy") as proxy, \
                    patch.object(self.custom, "get_all_fragment_contents", return_value=[]):
                proxy.return_value.get_policy_image_layers.return_value = {"layers": ["test-layer"]}
                self.custom.acifragmentgen_confcom(
                    image_name=image if source == "image" else None,
                    input_path=str(input_path) if source == "json" else None,
                    tar_mapping_location=None,
                    namespace="envformat",
                    svn="1",
                    feed=None,
                    key=None,
                    chain=None,
                    minimum_svn=None,
                    output_filename=str(output_path),
                    no_print=True,
                    platform=platform,
                    **kwargs,
                )
            text = output_path.read_text()
        containers, _ = self.template_util.extract_containers_and_fragments_from_text(text)
        return text, containers[0]

    def test_pattern_default_is_unchanged(self):
        for source in ("image", "json"):
            with self.subTest(source=source):
                default_text, container = self._generate(source=source)
                pattern_text, _ = self._generate(source=source, env_rule_format="pattern")
                self.assertEqual(default_text, pattern_text)
                self.assertIn(
                    {"pattern": "IMAGE_ONLY=a=b", "strategy": "string", "required": False},
                    container["env_rules"],
                )
                self.assertTrue(all("pattern" in rule and "name" not in rule for rule in container["env_rules"]))

    def test_name_value_format_preserves_image_input_and_injected_rules(self):
        for source in ("image", "json"):
            for platform in ("linux/amd64", "windows/amd64"):
                with self.subTest(source=source, platform=platform):
                    text, container = self._generate(
                        source=source,
                        platform=platform,
                        env_rule_format="name-value",
                        prerelease_policy_api=platform.startswith("linux"),
                    )
                    self.assertIn('framework_version := "0.5.0"', text)
                    self.assertEqual(container["layers"], ["test-layer"])
                    _, pattern_container = self._generate(
                        source=source,
                        platform=platform,
                        prerelease_policy_api=platform.startswith("linux"),
                    )
                    pattern_rules = [{
                        "pattern": f'{rule["name"]}={rule["value"]}',
                        "strategy": rule["value_strategy"],
                        "required": rule["required"],
                    } for rule in container["env_rules"]]
                    self.assertEqual(pattern_rules, pattern_container["env_rules"])
                    rules = {rule["name"]: rule for rule in container["env_rules"]}
                    self.assertTrue(all("pattern" not in rule for rule in rules.values()))
                    self.assertEqual(rules["IMAGE_ONLY"], {
                        "name": "IMAGE_ONLY", "name_strategy": "string",
                        "value": "a=b", "value_strategy": "string", "required": False,
                    })
                    self.assertEqual(rules["EMPTY"]["value"], "")
                    self.assertEqual(
                        rules["OVERRIDE"]["value"], "custom-value" if source == "json" else "image-value"
                    )
                    self.assertEqual(
                        sum(rule["name"] == "OVERRIDE" for rule in container["env_rules"]), 1
                    )
                    if source == "json":
                        self.assertEqual(rules["CUSTOM_.+"], {
                            "name": "CUSTOM_.+", "name_strategy": "re2",
                            "value": "value=(one|two)", "value_strategy": "re2", "required": False,
                        })
                    if platform.startswith("linux"):
                        self.assertEqual(rules["TERM"], {
                            "name": "TERM", "name_strategy": "string",
                            "value": "xterm", "value_strategy": "string", "required": False,
                        })
                    else:
                        self.assertNotIn("TERM", rules)
                        self.assertEqual(rules["IDENTITY_ENDPOINT"]["value_strategy"], "re2")

    def test_name_value_format_retains_required_flag(self):
        rules = self.container.extract_env_rules({
            "environmentVariables": [{"name": "REQUIRED", "value": "", "strategy": "string", "required": True}],
        }, env_rule_format="name-value")
        self.assertEqual(rules, [{
            "name": "REQUIRED", "name_strategy": "string",
            "value": "", "value_strategy": "string", "required": True,
        }])

    def test_name_value_format_rejects_deployed_linux_framework_and_import_generation(self):
        for options, message in (
            ({}, "Use --prerelease-policy-api"),
            ({"generate_import": True}, "cannot be used with --generate-import"),
        ):
            with self.subTest(options=options), self.assertLogs(level="ERROR") as logs:
                with self.assertRaises(SystemExit):
                    self._generate(env_rule_format="name-value", **options)
                self.assertIn(message, logs.output[0])

        with patch.object(self.security_policy, "validate_image_platform"), self.assertLogs(level="ERROR") as logs:
            with self.assertRaises(SystemExit):
                self.security_policy.load_policy_from_image_name(
                    "contoso.azurecr.io/app:latest", env_rule_format="name-value"
                )
            self.assertIn("Use --prerelease-policy-api", logs.output[0])

    def test_name_value_format_checks_selected_framework_version(self):
        for platform, prerelease, setting, version, supported in (
            ("linux/amd64", False, "DEFAULT_POLICY_FRAMEWORK_VERSION", "0.5.0", True),
            ("linux/amd64", False, "DEFAULT_POLICY_FRAMEWORK_VERSION", "0.10.0", True),
            ("linux/amd64", True, "PRERELEASE_POLICY_FRAMEWORK_VERSION", "0.4.99", False),
            ("windows/amd64", False, "PRERELEASE_POLICY_FRAMEWORK_VERSION", "0.4.99", False),
        ):
            with self.subTest(platform=platform, version=version), \
                    patch.object(self.security_policy.config, setting, version), \
                    patch.object(self.security_policy, "package_version", return_value="test-version"):
                options = {
                    "platform": platform,
                    "prerelease_policy_api": prerelease,
                    "env_rule_format": "name-value",
                }
                if supported:
                    text, _ = self._generate(**options)
                    self.assertIn(f'framework_version := "{version}"', text)
                else:
                    with self.assertLogs(level="ERROR") as logs, self.assertRaises(SystemExit):
                        self._generate(**options)
                    self.assertIn("confcom test-version", logs.output[0])
                    self.assertIn("Use --prerelease-policy-api", logs.output[0])

    def test_fragment_coverage_does_not_ignore_name_value_rules(self):
        with patch.object(self.security_policy, "validate_image_platform"):
            policy = self.security_policy.load_policy_from_image_name(
                "contoso.azurecr.io/app:latest", prerelease_policy_api=True, env_rule_format="name-value"
            )
        image = policy.get_images()[0]
        image.get_environment_rules().append({
            "name": "Port", "name_strategy": "string",
            "value": "8080", "value_strategy": "string", "required": False,
        })
        fragment = image.get_policy_json()
        policy.set_fragment_contents([fragment])
        self.assertTrue(policy.should_eliminate_container_covered_by_fragments(image))
        fragment["env_rules"][0]["value"] = "different"
        self.assertFalse(policy.should_eliminate_container_covered_by_fragments(image))
        fragment["env_rules"] = [{
            "pattern": f'{rule["name"]}={rule["value"]}',
            "strategy": rule["value_strategy"],
            "required": rule["required"],
        } for rule in image.get_policy_json()["env_rules"]]
        self.assertFalse(policy.should_eliminate_container_covered_by_fragments(image))
