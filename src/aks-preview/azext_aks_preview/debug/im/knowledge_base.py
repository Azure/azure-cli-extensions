from typing import Dict, List

from .types import DebugStep, ActionStep
from .knowledge_base_debug import DebugStepA, DebugStepB, DebugStepC
from .knowledge_base_action import ActionStepA, ActionStepB, ActionStepC


class KnowledgeBase:
    def __init__(self) -> None:
        self.debug_steps: Dict[str, DebugStep] = {
            "a": DebugStepA(),
            "b": DebugStepB(),
            "c": DebugStepC()
        }
        self.action_steps: Dict[str, ActionStep] = {
            "a": ActionStepA(),
            "b": ActionStepB(),
            "c": ActionStepC()
        }

    def get_debug_step_by_name(self, name: str) -> DebugStep:
        return self.debug_steps[name]

    def get_action_step_by_name(self, name: str) -> ActionStep:
        return self.action_steps[name]

    def get_debug_steps_by_scenario(self, scenario: str) -> List[DebugStep]:
        results = []
        for v in self.debug_steps.values():
            if scenario in v.tags:
                results.append(v)
        return results
