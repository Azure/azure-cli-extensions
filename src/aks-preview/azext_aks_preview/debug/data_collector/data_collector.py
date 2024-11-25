import asyncio
import json
import os
from typing import Dict

from azure.cli.core.commands import progress
from knack.log import get_logger

from ..common.consts import DEBUG_KUBECONFIG_PATH, DEBUG_TOOL_DIR
from ..common.utils import poll_helper
from ..controller.tool_manager import ToolManager

logger = get_logger(__name__)


class DataCollector:
    def __init__(self, tool_manager: ToolManager) -> None:
        self.tool_dir = DEBUG_TOOL_DIR
        self.tool_manager = tool_manager
        self.copied_os_env = os.environ.copy()
        self.copied_os_env["KUBECONFIG"] = DEBUG_KUBECONFIG_PATH
        self.progress_hook = progress.ProgressHook()
        self.progress_hook.init_progress(progress.get_progress_view(False))

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
        logger.debug("[data collector] kubectl get po command: %s", cmd)
        p_get_pod = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=self.copied_os_env)
        data = await poll_helper(self.progress_hook, p_get_pod.communicate(), f"Collecting data: get_pod with command: {cmd}")
        return json.loads(data[0])

    async def get_cm(self, name: str = None, namespace: str = None):
        self.tool_manager.local_install_kubectl()
        args = []
        if name:
            args.append(name)
        if namespace:
            args.extend(["-n", namespace])
        cmd = "kubectl get cm " + " ".join(args) + " -o json"
        logger.debug("[data collector] kubectl get cm command: %s", cmd)
        p_get_cm = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=self.copied_os_env)
        data = await poll_helper(self.progress_hook, p_get_cm.communicate(), f"Collecting data: get_cm with command: {cmd}")
        return json.loads(data[0])

    async def get_node(self, name: str = None):
        self.tool_manager.local_install_kubectl()
        args = []
        if name:
            args.append(name)
        cmd = "kubectl get node " + " ".join(args) + " -o json"
        logger.debug("[data collector] kubectl get node command: %s", cmd)
        p_get_node = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=self.copied_os_env)
        data = await poll_helper(self.progress_hook, p_get_node.communicate(), f"Collecting data: get_node with command: {cmd}")
        return json.loads(data[0])


class InspektorGadgetDataCollector(DataCollector):
    def __init__(self, tool_manager: ToolManager) -> None:
        super().__init__(tool_manager)

    async def get_run_trace_dns(self, namespace: str = None, pod_name: str = None, node_name: str = None, timeout: int = 15):
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
        if timeout:
            args.extend(["--timeout", str(timeout)])
        cmd = "kubectl gadget run trace_dns " + " ".join(args) + " -o json"
        logger.debug("[data collector] kubectl gadget run trace dns command: %s", cmd)
        p_run_trace_dns = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=self.copied_os_env)
        data, _ = await poll_helper(self.progress_hook, p_run_trace_dns.communicate(), f"Collecting data: trace_dns with command: {cmd}")
        return json.loads(data) if data else None
