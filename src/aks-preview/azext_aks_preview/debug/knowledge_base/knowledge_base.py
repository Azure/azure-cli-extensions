from typing import Dict, List

from ..common.types import DebugStep, ActionStep
from .knowledge_base_debug import DebugStepCoreDNSPodRunning, DebugStepCoreDNSConfigMapValid, DebugStepIGTraceDNSNode, DebugStepIGTraceDNSPod
from .knowledge_base_action import NoActionStep, ActionStepPrompt


class KnowledgeBase:
    def __init__(self) -> None:
        self.debug_steps: Dict[str, DebugStep] = {
            "DebugStepCoreDNSPodRunning": DebugStepCoreDNSPodRunning(),
            "DebugStepCoreDNSConfigMapValid": DebugStepCoreDNSConfigMapValid(),
            "DebugStepIGTraceDNSNode": DebugStepIGTraceDNSNode(),
            "DebugStepIGTraceDNSPod": DebugStepIGTraceDNSPod(),
        }

    def get_debug_steps_by_scenario(self, scenario: str) -> List[DebugStep]:
        results = []
        for v in self.debug_steps.values():
            if scenario in v.applicable_scenarios:
                results.append(v)
        return results
