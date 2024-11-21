from ..common.types import DebugStep
from .knowledge_base_action import NoActionStep, ActionStepPrompt


class DebugStepCoreDNSPodRunning(DebugStep):
    def __init__(self) -> None:
        super().__init__()
        self.applicable_scenarios.append("dns")

    async def run(self) -> None:
        pods = await self.data_broker.k8s_data_collector.get_pod(label={"k8s-app": "kube-dns"}, namespace="kube-system")
        all_running = True
        for pod in pods["items"]:
            if pod["status"]["phase"] != "Running":
                self.next_steps.append(ActionStepPrompt("CoreDNS pod is not running"))
                all_running = False
        if all_running:
            self.next_steps.append(DebugStepIGTraceDNSNode)
            self.summary = "CoreDNS pod is running"
        else:
            self.summary = "CoreDNS pod is not running"


class DebugStepCoreDNSConfigMapValid(DebugStep):
    def __init__(self) -> None:
        super().__init__()
        self.applicable_scenarios.append("dns")

    async def run(self) -> None:
        data = await self.data_broker.k8s_data_collector.get_cm(name="coredns", namespace="kube-system")
        if data["data"]["Corefile"]:
            self.next_steps.append(DebugStepIGTraceDNSNode)
        else:
            self.next_steps.append(ActionStepPrompt("CoreDNS config map is not valid"))


class DebugStepIGTraceDNSNode(DebugStep):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        nodes = await self.data_broker.k8s_data_collector.get_node()
        node_0_name = nodes["items"][0]["metadata"]["name"]
        data = await self.data_broker.ig_data_collector.get_run_trace_dns(node_name=node_0_name)
        if data:
            self.summary = "IG trace DNS node have been captured"
        else:
            self.summary = "IG trace DNS node have no data"
        self.next_steps.append(NoActionStep)


class DebugStepIGTraceDNSPod(DebugStep):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        data = await self.data_broker.k8s_data_collector.get_pod(label={"k8s-app": "cloud-node-manager"}, namespace="kube-system")
        pod_0_name = data["items"][0]["metadata"]["name"]
        data = await self.data_broker.ig_data_collector.get_run_trace_dns(namespace="kube-system", pod_name=pod_0_name)
        if data:
            self.summary = "IG trace DNS pod have been captured"
        else:
            self.summary = "IG trace DNS pod have no data"
        self.next_steps.append(NoActionStep)
