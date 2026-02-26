# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Optional
import yaml

from azext_confcom import config
from azext_confcom.lib.platform import (
    PRIVILEDGED_CAPABILITIES,
    VN2_PRIVILEGED_MOUNTS,
    VN2_WORKLOAD_IDENTITY_ENV_RULES,
    VN2_WORKLOAD_IDENTITY_MOUNTS,
)
from azext_confcom.lib.policy import ContainerUser
from azext_confcom.lib.containers import (
    from_image as container_from_image,
    merge_containers,
)


def find_vn2_containers(vn2_template):
    for key, value in vn2_template.items():
        if key in ("containers", "initContainers"):
            yield from value
        elif isinstance(value, dict):
            result = find_vn2_containers(value)
            if result is not None:
                yield from result
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = find_vn2_containers(item)
                    if result is not None:
                        yield from result


def vn2_container_env_rules(template: dict, container: dict, template_variables: dict):

    for env_var in container.get("env", []):

        if "value" in env_var:
            is_special = re.match('^===VIRTUALNODE2.CC.THIM.(.+)===$', env_var.get('value'))
            yield {
                "pattern": f"{env_var.get('name')}={'.*' if is_special else env_var.get('value')}",
                "strategy": "re2" if is_special else "string",
                "required": False,
            }

        elif "valueFrom" in env_var:

            if "configMapKeyRef" in env_var.get('valueFrom') or "secretKeyRef" in env_var.get('valueFrom'):
                var_ref = (
                    env_var.get('valueFrom').get("configMapKeyRef", None) or
                    env_var.get('valueFrom').get("secretKeyRef", None)
                )
                yield {
                    "pattern": f"{env_var.get('name')}={template_variables[var_ref.get('name')][var_ref.get('key')]}",
                    "strategy": "string",
                    "required": False,
                }

            elif "fieldRef" in env_var.get('valueFrom'):
                # Existing behaviour is to wildcard this, there is a correct implementation below
                yield {
                    "pattern": f"{env_var.get('name')}=.*",
                    "strategy": "re2",
                    "required": False,
                }
                # value = template
                # for part in env_var.get('valueFrom').get("fieldRef", {}).get("fieldPath", "").split("."):
                #     value = value.get(part, {})
                # yield {
                #     "pattern": f"{env_var.get('name')}={value}",
                #     "strategy": "string",
                #     "required": False,
                # })

            elif "resourceFieldRef" in env_var.get('valueFrom'):
                ref = env_var.get('valueFrom').get("resourceFieldRef", {})
                ref_container_name = ref.get("containerName") or container.get("name")
                ref_container = next(
                    (
                        c for c in template["spec"]["containers"]
                        if c.get("name") == ref_container_name
                    ),
                    None,
                )
                if ref_container is None:
                    continue
                value = ref_container.get("resources", {})
                for part in ref["resource"].split("."):
                    value = value.get(part, {})
                yield {
                    "pattern": f"{env_var.get('name')}={value}",
                    "strategy": "string",
                    "required": False,
                }


def vn2_container_mounts(template: dict, container: dict) -> list[dict]:

    volume_claim_access = {
        v["metadata"]["name"]: v.get("spec", {}).get("accessModes", [])
        for v in template.get("spec", {}).get("volumeClaimTemplates", [])
    }
    volume_defs = {
        v["name"]: [k for k in v.keys() if k != "name"][0]
        for v in template.get("spec", {}).get("volumes", [])
    }

    return [
        {
            "destination": m.get("mountPath"),
            "options": [
                "rbind",
                "rshared",
                "ro" if (
                    m.get("readOnly") or
                    "ReadOnlyMany" in volume_claim_access.get(m.get("name"), []) or
                    volume_defs.get(m.get("name")) in {"configMap", "secret", "downwardAPI", "projected"}
                ) else "rw"
            ],
            "source": "sandbox:///tmp/atlas/emptydir/.+",
            "type": "bind",
        }
        for m in container.get("volumeMounts", [])
    ]


def containers_from_vn2(
    template: str,
    container_name: Optional[str] = None
) -> str:

    with Path(template).open("r") as f:
        template_yaml = list(yaml.safe_load_all(f))

    # Find containers matching the specified name (if provided)
    template_containers = []
    variables = {}
    for doc in template_yaml:
        if not isinstance(doc, dict):
            continue
        kind = doc.get("kind")
        if kind == "ConfigMap":
            variables[doc["metadata"]["name"]] = {
                **doc.get("data", {}),
                **{k: base64.b64decode(v).decode("utf-8") for k, v in doc.get("binaryData", {}).items()},
            }
        elif kind == "Secret":
            variables[doc["metadata"]["name"]] = {
                **{k: base64.b64decode(v).decode("utf-8") for k, v in doc.get("data", {}).items()},
                **doc.get("stringData", {}),
            }
        elif kind in ["Pod", "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "ReplicaSet"]:
            for container in find_vn2_containers(doc):
                if container_name and container.get("name") != container_name:
                    continue
                template_containers.append((container, doc))

    if container_name:
        if not template_containers:
            raise AssertionError(f"No containers with name {container_name} found.")
        if len(template_containers) > 1:
            raise AssertionError(
                f"Multiple containers with name {container_name} found."
            )
    elif not template_containers:
        raise AssertionError("No containers found.")

    container_defs = []
    for template_container, template_doc in template_containers:
        image_container_def = container_from_image(template_container.get("image"), platform="vn2")

        template_container_def = {
            "name": template_container.get("name"),
            "command": template_container.get("command", []) + template_container.get("args", []),
            "env_rules": (
                [
                    {
                        "pattern": rule.get("pattern") or f"{rule.get('name')}={rule.get('value')}",
                        "strategy": rule.get("strategy", "string"),
                        "required": rule.get("required", False),
                    }
                    for rule in (
                        config.OPENGCS_ENV_RULES
                        + config.FABRIC_ENV_RULES
                        + config.MANAGED_IDENTITY_ENV_RULES
                        + config.ENABLE_RESTART_ENV_RULE
                        + config.VIRTUAL_NODE_ENV_RULES
                    )
                ]
                + list(vn2_container_env_rules(template_doc, template_container, variables))
            ),
            "mounts": vn2_container_mounts(template_doc, template_container),
        }

        # Parse security context
        security_context = (
            template_doc.get("spec", {}).get("securityContext", {})
            | template_container.get("securityContext", {})
        )
        if security_context.get("privileged", False):
            template_container_def["allow_elevated"] = True
            template_container_def["mounts"] += VN2_PRIVILEGED_MOUNTS
            template_container_def["capabilities"] = PRIVILEDGED_CAPABILITIES

        if security_context.get("runAsUser") or security_context.get("runAsGroup"):
            template_container_def["user"] = asdict(ContainerUser())
            if security_context.get("runAsUser"):
                template_container_def["user"]["user_idname"] = {
                    "pattern": str(security_context.get("runAsUser")),
                    "strategy": "id",
                }
            if security_context.get("runAsGroup"):
                template_container_def["user"]["group_idnames"] = [{
                    "pattern": str(security_context.get("runAsGroup")),
                    "strategy": "id",
                }]

        if security_context.get("seccompProfile"):
            template_container_def["seccomp_profile_sha256"] = sha256(
                base64.b64decode(security_context.get("seccompProfile"))
            ).hexdigest()

        if security_context.get("allowPrivilegeEscalation") is False:
            template_container_def["no_new_privileges"] = True

        # Check for workload identity
        labels = template_doc.get("metadata", {}).get("labels", {}) or {}
        if labels.get("azure.workload.identity/use", "false") == "true":
            template_container_def["env_rules"].extend(VN2_WORKLOAD_IDENTITY_ENV_RULES)
            template_container_def["mounts"].extend(VN2_WORKLOAD_IDENTITY_MOUNTS)

        exec_processes = [
            {
                "command": process.get("exec", {}).get("command", []),
                "signals": []
            }
            for process in [
                template_container.get("livenessProbe"),
                template_container.get("readinessProbe"),
                template_container.get("startupProbe"),
                template_container.get("lifecycle", {}).get("postStart"),
                template_container.get("lifecycle", {}).get("preStop"),
            ]
            if process is not None
        ]
        if exec_processes:
            template_container_def["exec_processes"] = exec_processes

        container_defs.append(merge_containers(
            image_container_def,
            template_container_def,
        ))

    return json.dumps(container_defs)
