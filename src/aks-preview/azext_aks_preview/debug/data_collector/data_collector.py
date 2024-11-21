from typing import Dict
from random import randint
import asyncio
from ..common.consts import DEBUG_TOOL_DIR
from ..controller.tool_manager import ToolManager
import json


class DataCollector:
    def __init__(self, tool_manager: ToolManager) -> None:
        self.tool_dir = DEBUG_TOOL_DIR
        self.tool_manager = tool_manager

    def clean():
        # clean up the resources used by the data collector
        pass

    def export():
        # export the data to a file/remote storage
        pass


class KubernetesDataCollector(DataCollector):
    def __init__(self, tool_manager: ToolManager) -> None:
        super().__init__(tool_manager)

    async def get_pod(self, name: str = None, namespace: str = None, label: Dict[str, str] = None):
        self.tool_manager.local_install_kubectl()
        args = []
        if name:
            args.append(name)
        if namespace:
            args.extend(["-n", namespace])
        if label:
            args.append("-l")
            for k, v in label.items():
                args.append(f"{k}={v},")
            args.append(args.pop().rstrip(","))
        cmd = "kubectl get po " + " ".join(args) + " -o json"
        print("running command: ", cmd)
        p_get_pod = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        pod_info = await p_get_pod.communicate()
        return json.loads(pod_info[0])

    async def get_cm(self, name: str = None, namespace: str = None):
        self.tool_manager.local_install_kubectl()
        args = []
        if name:
            args.append(name)
        if namespace:
            args.extend(["-n", namespace])
        cmd = "kubectl get cm " + " ".join(args) + " -o json"
        print("running command: ", cmd)
        p_get_cm = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        cm_info = await p_get_cm.communicate()
        return json.loads(cm_info[0])

    async def get_node(self, name: str = None):
        self.tool_manager.local_install_kubectl()
        args = []
        if name:
            args.append(name)
        cmd = "kubectl get node " + " ".join(args) + " -o json"
        print("running command: ", cmd)
        p_get_node = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        node_info = await p_get_node.communicate()
        return json.loads(node_info[0])


class InspektorGadgetDataCollector(DataCollector):
    def __init__(self, tool_manager: ToolManager) -> None:
        super().__init__(tool_manager)

    async def get_run_trace_dns(self, namespace: str = None, pod_name: str = None, node_name: str = None):
        self.tool_manager.local_install_kubectl()
        self.tool_manager.local_install_kubectl_inspektor_gadget()
        self.tool_manager.remote_install_inspektor_gadget()
        args = []
        if namespace:
            args.extend(["--namespace", namespace])
        if pod_name:
            args.extend(["--pod", pod_name])
        if node_name:
            args.extend(["--node", node_name])
        cmd = "kubectl gadget run trace dns " + " ".join(args) + " -o json"
        print("running command: ", cmd)
        p_run_trace_dns = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        trace_dns_info, _ = await p_run_trace_dns.communicate()
        return json.loads(trace_dns_info) if trace_dns_info else None
