# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import azext_confcom.config as config
from azext_confcom.template_util import extract_containers_from_text
from azext_confcom.security_policy import (
    load_policy_from_str,
    load_policy_from_virtual_node_yaml_str,
    OutputType,
    decompose_confidential_properties
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
                    "containerImage": "mcr.microsoft.com/cbl-mariner/distroless/python:3.9-nonroot",
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

    custom_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: simple-container-pod
spec:
  containers:
  - name: simple-container
    image: mcr.microsoft.com/cbl-mariner/distroless/python:3.9-nonroot
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
      image: mcr.microsoft.com/cbl-mariner/distroless/python:3.9-nonroot
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
      image: mcr.microsoft.com/cbl-mariner/distroless/python:3.9-nonroot
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
      image: mcr.microsoft.com/cbl-mariner/distroless/minimal:2.0
      command:
        - echo "hello world!"
      env:
        - name: PATH
          value: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
  containers:
    - name: simple-container
      image: mcr.microsoft.com/cbl-mariner/distroless/python:3.9-nonroot
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
        image: mcr.microsoft.com/cbl-mariner/distroless/minimal:2.0
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

    def test_compare_policy_sources(self):
        custom_policy = load_policy_from_str(self.custom_json)
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

        for var in config.VIRTUAL_NODE_ENV_RULES_WORKLOAD_IDENTITY:
          self.assertTrue(var['name'] in env_rule_names)

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