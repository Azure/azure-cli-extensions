# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import subprocess
import azext_confcom.config as config
import azext_confcom.os_util as os_util
from azext_confcom.template_util import extract_containers_from_text
from azext_confcom.security_policy import (
    load_policy_from_json,
    load_policy_from_virtual_node_yaml_str,
    OutputType,
    decompose_confidential_properties
)
from azext_confcom.custom import (
    acipolicygen_confcom,
    acifragmentgen_confcom,
)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class PolicyGeneratingVirtualNode(unittest.TestCase):
    # NOTE: Virtual Node mounts everything as emptyDir, so the inputs look different
    # but outputs will be the same
    custom_json = """
{
            "version": "1.0",
            "containers": [
                {
                    "name": "simple-container",
                    "containerImage": "mcr.microsoft.com/azurelinux/base/python:3.12",
                    "environmentVariables": [
                        {
                            "name":"PATH",
                            "value":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                            "strategy":"string"
                        }
                    ],
                    "command": ["python3"],
                    "workingDir": "",
                    "mounts": [
                        {
                            "mountType": "emptyDir",
                            "mountPath": "/aci/logs",
                            "readonly": false
                        },
                         {
                            "mountType": "emptyDir",
                            "mountPath": "/aci/secret",
                            "readonly": true
                        }
                    ]
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

    custom_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: simple-container-pod
spec:
  containers:
  - name: simple-container
    image: mcr.microsoft.com/azurelinux/base/python:3.12
    command: ["python3"]
    env:
    - name: PATH
      value: "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    volumeMounts:
    - mountPath: /aci/logs
      name: azure-file
      readOnly: false
    - mountPath: /aci/secret
      name: secret-volume
      readOnly: true
  volumes:
  - name: azure-file
    azureFile:
      secretName: azure-secret
      shareName: <your-file-share-name>
      readOnly: false
  - name: secret-volume
    secret:
      secretName: <your-secret-name>
"""

    custom_yaml_configmap = """
---
apiVersion: v1
kind: Pod
metadata:
  name: simple-container-pod
spec:
  containers:
    - name: simple-container
      image: mcr.microsoft.com/azurelinux/base/python:3.12
      command:
        - python3
      env:
        - name: PATH
          value: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        - name: key1
          valueFrom:
            configMapKeyRef:
              name: configmap-name
              key: key1
        - name: key2
          valueFrom:
            configMapKeyRef:
              name: configmap-name
              key: key2
        - name: key3
          valueFrom:
            configMapKeyRef:
              name: configmap-name
              key: key3
        - name: key4
          valueFrom:
            configMapKeyRef:
              name: configmap-name
              key: key4
        - name: key5
          valueFrom:
            configMapKeyRef:
              name: configmap-name
              key: key5
      volumeMounts:
        - mountPath: /aci/configmap
          name: configmap-volume
  volumes:
    - name: configmap-volume
      configMap:
        name: configmap-name

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: configmap-name
data:
  key1: value1
  key2: value2
  key3: value3
  key4: value4
binaryData:
  key5: dmFsdWU1

"""

    custom_yaml_secret = """
---
apiVersion: v1
kind: Pod
metadata:
  name: simple-container-pod
spec:
  containers:
    - name: simple-container
      image: mcr.microsoft.com/azurelinux/base/python:3.12
      command:
        - python3
      env:
        - name: PATH
          value: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        - name: key1
          valueFrom:
            secretKeyRef:
              name: secret-name
              key: key1
        - name: key2
          valueFrom:
            secretKeyRef:
              name: secret-name
              key: key2
        - name: key3
          valueFrom:
            secretKeyRef:
              name: secret-name
              key: key3
        - name: key4
          valueFrom:
            secretKeyRef:
              name: secret-name
              key: key4
        - name: key5
          valueFrom:
            secretKeyRef:
              name: secret-name
              key: key5
      volumeMounts:
        - mountPath: /aci/secret
          name: secret-volume
          readOnly: true
  volumes:
    - name: secret-volume
      secret:
        secretName: secret-name

---
apiVersion: v1
kind: Secret
metadata:
  name: secret-name
data:
  key1: dmFsdWUx
  key2: dmFsdWUy
  key3: dmFsdWUz
  key4: dmFsdWU0
stringData:
  key5: value5

"""

    custom_yaml_init_containers = """
---
apiVersion: v1
kind: Pod
metadata:
  name: simple-container-pod
  labels:
    azure.workload.identity/use: "true"
spec:
  initContainers:
    - name: init-container
      image: mcr.microsoft.com/azurelinux/distroless/base:3.0
      command:
        - echo "hello world!"
      env:
        - name: PATH
          value: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
  containers:
    - name: simple-container
      image: mcr.microsoft.com/azurelinux/base/python:3.12
      command:
        - python3
"""

    custom_yaml_volume_claim = """
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: mcr.microsoft.com/azurelinux/distroless/base:3.0
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadOnlyMany" ]
      resources:
        requests:
          storage: 1Gi
"""

    custom_yaml_command = """
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "container"
  replicas: 2
  selector:
    matchLabels:
      app: container
  template:
    metadata:
      labels:
        app: container
    spec:
      containers:
      - name: container
        image: mcr.microsoft.com/aci/msi-atlas-adapter:master_20201203.1
        args: ["test", "values"]
        ports:
        - containerPort: 80
          name: web
"""
    @classmethod
    def setUpClass(cls):
        cls.key_dir_parent = os.path.join(TEST_DIR, '..', '..', '..', 'samples', 'certs')
        cls.key = os.path.join(cls.key_dir_parent, 'intermediateCA', 'private', 'ec_p384_private.pem')
        cls.chain = os.path.join(cls.key_dir_parent, 'intermediateCA', 'certs', 'www.contoso.com.chain.cert.pem')
        if not os.path.exists(cls.key) or not os.path.exists(cls.chain):
            script_path = os.path.join(cls.key_dir_parent, 'create_certchain.sh')

            arg_list = [
                script_path,
            ]
            os.chmod(script_path, 0o755)

            # NOTE: this will raise an exception if it's run on windows and the key/cert files don't exist
            item = subprocess.run(
                arg_list,
                check=False,
                shell=True,
                cwd=cls.key_dir_parent,
                env=os.environ.copy(),
            )

            if item.returncode != 0:
                raise Exception("Error creating certificate chain")

    def test_compare_policy_sources(self):
        custom_policy = load_policy_from_json(self.custom_json)
        custom_policy.populate_policy_content_for_all_images()
        virtual_node_policy = load_policy_from_virtual_node_yaml_str(self.custom_yaml)[0]
        virtual_node_policy.populate_policy_content_for_all_images()
        custom_policy_output = custom_policy.get_serialized_output()
        custom_containers, custom_fragments = decompose_confidential_properties(custom_policy_output)
        virtual_node_output = virtual_node_policy.get_serialized_output()
        virtual_node_containers, virtual_node_fragments = decompose_confidential_properties(virtual_node_output)
        # NOTE: env vars and mounts will be different due to VN2 needing a different environment
        # test the fragments
        self.assertEqual(custom_fragments, virtual_node_fragments)
        # test the image layers
        self.assertEqual(custom_containers[0].get("layers"), virtual_node_containers[0].get("layers"))
        # test the image command
        self.assertEqual(custom_containers[0].get("command"), virtual_node_containers[0].get("command"))


    def test_virtual_node_policy_fragments(self):
        fragment_filename = "policy_file.json"
        yaml_filename = "policy_file.yaml"
        rego_filename = "example_file"
        import_filename = "my_fragments.json"
        signed_file_path = f"{rego_filename}.rego.cose"
        try:

          os_util.write_str_to_file(fragment_filename, self.custom_json2)
          os_util.write_str_to_file(yaml_filename, self.custom_yaml)
          acifragmentgen_confcom(None, fragment_filename, None, rego_filename, "1", "test_feed_file", self.key, self.chain, None)

          # create import file
          acifragmentgen_confcom(None, None, None, None, None, None, None, None, "1", fragment_path=signed_file_path, generate_import=True, fragments_json=import_filename)
          # add path into the fragment import
          import_data = os_util.load_json_from_file(import_filename)
          import_data[config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS][0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_PATH] = signed_file_path
          os_util.write_json_to_file(import_filename, import_data)

          # create policy using import statement
          acipolicygen_confcom(None, None, None, None, yaml_filename, None, None, fragments_json=import_filename, exclude_default_fragments=True, include_fragments=True)

          # count all the vn2 specific env vars to amke sure they're all there
          fragment_content = os_util.str_to_base64(os_util.load_str_from_file(f"{rego_filename}.rego"))
          containers, _ = decompose_confidential_properties(fragment_content)

          env_vars = containers[0].get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS)

          vn2_env_var_count = 0
          vn2_env_vars = [x.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_NAME) for x in config.VIRTUAL_NODE_ENV_RULES]

          for env_var in env_vars:
              name = env_var.get(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE).split("=")[0]
              if name in vn2_env_vars:
                  vn2_env_var_count += 1
          self.assertEqual(len(vn2_env_vars), vn2_env_var_count)

          output_yaml = os_util.load_yaml_from_file(yaml_filename)
          output_containers, output_fragments = decompose_confidential_properties(output_yaml.get(config.VIRTUAL_NODE_YAML_METADATA).get(config.VIRTUAL_NODE_YAML_ANNOTATIONS).get(config.VIRTUAL_NODE_YAML_POLICY))

          self.assertTrue(config.DEFAULT_REGO_FRAGMENTS not in output_fragments)
          for container in output_containers:
              if container.get(config.POLICY_FIELD_CONTAINERS_NAME) == "simple-container":
                  self.fail("policy contains container covered by fragment")
        finally:

          os_util.force_delete_silently(fragment_filename)
          os_util.force_delete_silently(yaml_filename)
          os_util.force_delete_silently(import_filename)
          os_util.force_delete_silently(signed_file_path)
          os_util.force_delete_silently(f"{rego_filename}.rego")


    def test_configmaps(self):
        virtual_node_policy = load_policy_from_virtual_node_yaml_str(self.custom_yaml_configmap)[0]
        virtual_node_policy.populate_policy_content_for_all_images()
        container_start = "containers := "
        containers = json.loads(extract_containers_from_text(virtual_node_policy.get_serialized_output(OutputType.PRETTY_PRINT), container_start))
        # get the env vars from the first container
        # we should have 4 env vars from the configmap
        all_rules = [
            env_var[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE]
            for env_var in
            containers[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS]
        ]

        self.assertTrue("key1=value1" in all_rules)
        self.assertTrue("key2=value2" in all_rules)
        self.assertTrue("key3=value3" in all_rules)
        self.assertTrue("key4=value4" in all_rules)
        self.assertTrue("key5=value5" in all_rules)
        # get the configmap mount from the first container
        mount_destinations = [
            mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION]
            for mount in
            containers[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS]
        ]
        self.assertTrue("/aci/configmap" in mount_destinations)

    def test_secrets(self):
        virtual_node_policy = load_policy_from_virtual_node_yaml_str(self.custom_yaml_secret)[0]
        virtual_node_policy.populate_policy_content_for_all_images()
        container_start = "containers := "
        containers = json.loads(extract_containers_from_text(virtual_node_policy.get_serialized_output(OutputType.PRETTY_PRINT), container_start))
        # get the env vars from the first container
        # we should have 4 env vars from the secret
        all_rules = [
            env_var[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE]
            for env_var in
            containers[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS]
        ]

        self.assertTrue("key1=value1" in all_rules)
        self.assertTrue("key2=value2" in all_rules)
        self.assertTrue("key3=value3" in all_rules)
        self.assertTrue("key4=value4" in all_rules)
        self.assertTrue("key5=value5" in all_rules)
        # get the secret mount from the first container
        mount_destinations = [
            mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION]
            for mount in
            containers[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS]
        ]
        self.assertTrue("/aci/secret" in mount_destinations)

    def test_init_containers(self):
        virtual_node_policy = load_policy_from_virtual_node_yaml_str(self.custom_yaml_init_containers)[0]
        virtual_node_policy.populate_policy_content_for_all_images()
        container_start = "containers := "
        containers = json.loads(extract_containers_from_text(virtual_node_policy.get_serialized_output(OutputType.PRETTY_PRINT), container_start))
        # see if we have both containers in the policy. Also includes the pause container
        self.assertEqual(len(containers), 3)
        # see if the init container is in the policy
        self.assertEqual(containers[0][config.POLICY_FIELD_CONTAINERS_NAME], "simple-container")
        # see if the main container is in the policy
        self.assertEqual(containers[1][config.POLICY_FIELD_CONTAINERS_NAME], "init-container")

    def test_workload_identity(self):
        virtual_node_policy = load_policy_from_virtual_node_yaml_str(self.custom_yaml_init_containers)[0]
        virtual_node_policy.populate_policy_content_for_all_images()
        container_start = "containers := "
        containers = json.loads(extract_containers_from_text(virtual_node_policy.get_serialized_output(OutputType.PRETTY_PRINT), container_start))

        # have to extract the name from the pattern
        env_rule_names = [(env_rule['pattern']).split("=")[0] for env_rule in containers[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS]]
        mounts = [mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION] for mount in containers[0][config.ACI_FIELD_CONTAINERS_MOUNTS]]

        for var in config.VIRTUAL_NODE_ENV_RULES_WORKLOAD_IDENTITY:
          self.assertTrue(var['name'] in env_rule_names)
        for mount in config.DEFAULT_MOUNTS_WORKLOAD_IDENTITY_VIRTUAL_NODE:
            self.assertTrue(mount['mountPath'] in mounts)

    def test_volume_claim(self):
        virtual_node_policy = load_policy_from_virtual_node_yaml_str(self.custom_yaml_volume_claim)[0]
        virtual_node_policy.populate_policy_content_for_all_images()
        container_start = "containers := "
        containers = json.loads(extract_containers_from_text(virtual_node_policy.get_serialized_output(OutputType.PRETTY_PRINT), container_start))
        # get the volume mount from the first container
        mounts = [
            mount
            for mount in
            containers[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS]
        ]
        self.assertTrue("/usr/share/nginx/html" in [mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION] for mount in mounts])
        mount = [mount for mount in mounts if mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION] == "/usr/share/nginx/html"][0]
        self.assertTrue("ro" in mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS])

        # get the nginx mount and make sure it is readonly
        containers[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS]

    def test_custom_args(self):
        virtual_node_policy = load_policy_from_virtual_node_yaml_str(self.custom_yaml_command)[0]
        virtual_node_policy.populate_policy_content_for_all_images()
        container_start = "containers := "
        containers = json.loads(extract_containers_from_text(virtual_node_policy.get_serialized_output(OutputType.PRETTY_PRINT), container_start))
        command = containers[0].get("command")

        self.assertEqual(command[-2:], ["test", "values"])