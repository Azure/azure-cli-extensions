from ..common.types import DebugStep, StepBuilder
from .knowledge_base_action import NoActionStep, ActionStepPrompt


class DebugStepCoreDNSPodRunning(DebugStep):
    entry_step_for_scenarios = ["dns"]

    def __init__(self, data=None) -> None:
        super().__init__(data=data)

    async def run(self) -> None:
        pods = await self.data_broker.k8s_data_collector.get_pod(label={"k8s-app": "kube-dns"}, namespace="kube-system")
        all_running = True
        for pod in pods["items"]:
            if pod["status"]["phase"] != "Running":
                self.next_steps.append(StepBuilder(ActionStepPrompt, "CoreDNS pod is not running"))
                all_running = False
        if all_running:
            self.next_steps.append(StepBuilder(DebugStepIGTraceDNSNode, {}))
            self.summary = "CoreDNS pod is running"
        else:
            self.summary = "CoreDNS pod is not running"


class DebugStepCoreDNSConfigMapValid(DebugStep):
    entry_step_for_scenarios = ["dns"]

    def __init__(self, data=None) -> None:
        super().__init__(data=data)

    async def run(self) -> None:
        data = await self.data_broker.k8s_data_collector.get_cm(name="coredns", namespace="kube-system")
        if data["data"]["Corefile"]:
            self.next_steps.append(StepBuilder(DebugStepIGTraceDNSPod, {}))
        else:
            self.next_steps.append(StepBuilder(ActionStepPrompt, "CoreDNS config map is not valid"))


class DebugStepIGTraceDNSNode(DebugStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)

    async def run(self) -> None:
        nodes = await self.data_broker.k8s_data_collector.get_node()
        node_0_name = nodes["items"][0]["metadata"]["name"]
        data = await self.data_broker.ig_data_collector.get_run_trace_dns(node_name=node_0_name)
        if data:
            self.summary = "IG trace DNS node have been captured"
        else:
            self.summary = "IG trace DNS node have no data"
        self.next_steps.append(StepBuilder(NoActionStep, {}))
        self.next_steps.append(StepBuilder(DebugStepDemoException, {}))


class DebugStepIGTraceDNSPod(DebugStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)

    async def run(self) -> None:
        data = await self.data_broker.k8s_data_collector.get_pod(label={"k8s-app": "cloud-node-manager"}, namespace="kube-system")
        pod_0_name = data["items"][0]["metadata"]["name"]
        data = await self.data_broker.ig_data_collector.get_run_trace_dns(namespace="kube-system", pod_name=pod_0_name)
        if data:
            self.summary = "IG trace DNS pod have been captured"
        else:
            self.summary = "IG trace DNS pod have no data"
        self.next_steps.append(StepBuilder(NoActionStep, {}))
        self.next_steps.append(StepBuilder(DebugStepDemoCircular, {"abc": "xyz"}))


class DebugStepDemoCircular(DebugStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)

    async def run(self) -> None:
        self.summary = "demo"
        self.next_steps.append(StepBuilder(DebugStepDemoCircular, self.data))


class DebugStepDemoException(DebugStep):
    def __init__(self, data=None) -> None:
        super().__init__(data=data)

    async def run(self) -> None:
        raise Exception("demo exception")
