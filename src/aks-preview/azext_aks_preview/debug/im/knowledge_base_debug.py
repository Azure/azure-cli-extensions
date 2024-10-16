from .types import Step, DebugStep, NoActionStep
from .knowledge_base_action import ActionStepA, ActionStepB, ActionStepC


class DebugStepA(DebugStep):
    def __init__(self) -> None:
        super().__init__()
        self.tags.append("dns")

    def run(self) -> Step:
        data = self.shared_data_collector.get_core_dns_config_map_data()
        if data == "a":
            self.next_steps.append(ActionStepA())
        elif data == "b":
            self.next_steps.append(DebugStepB())
        else:
            self.next_steps.append(NoActionStep())


class DebugStepB(DebugStep):
    def __init__(self) -> None:
        super().__init__()
        self.tags.append("dns")

    def run(self) -> Step:
        data = self.shared_data_collector.get_ig_dns_data()
        if data == "c":
            self.next_steps.append(ActionStepB())
        elif data == "d":
            self.next_steps.append(ActionStepC())
        else:
            self.next_steps.append(NoActionStep())


class DebugStepC(DebugStep):
    def __init__(self) -> None:
        super().__init__()
        self.tags.append("egress")

    def run(self) -> Step:
        self.next_steps.append(NoActionStep())
