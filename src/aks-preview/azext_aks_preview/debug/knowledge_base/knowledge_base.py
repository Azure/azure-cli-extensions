from typing import Dict, List, Type

from ..common.types import DebugStep, StepBuilder
from .knowledge_base_debug import (DebugStepCoreDNSConfigMapValid,
                                   DebugStepCoreDNSPodRunning,
                                   DebugStepIGTraceDNSNode,
                                   DebugStepIGTraceDNSPod)


class KnowledgeBase:
    def __init__(self) -> None:
        self.debug_steps: Dict[str, Type[DebugStep]] = {
            "DebugStepCoreDNSPodRunning": DebugStepCoreDNSPodRunning,
            "DebugStepCoreDNSConfigMapValid": DebugStepCoreDNSConfigMapValid,
            "DebugStepIGTraceDNSNode": DebugStepIGTraceDNSNode,
            "DebugStepIGTraceDNSPod": DebugStepIGTraceDNSPod,
        }

    def get_debug_steps_by_scenario(self, scenario: str) -> List[StepBuilder]:
        results: List[StepBuilder] = []
        for v in self.debug_steps.values():
            if scenario in v.entry_step_for_scenarios:
                results.append(StepBuilder(v, {}))
        return results
