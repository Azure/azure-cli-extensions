from .data_collector import SharedDataCollector
from .knowledge_base import KnowledgeBase
from .types import DebugStep


class Orchestrator():
    def __init__(self) -> None:
        self.steps = []
        self.shared_data_collector = SharedDataCollector()
        self.knowledge_base = KnowledgeBase()

    def run(self, scenario: str) -> None:
        self.steps = self.knowledge_base.get_debug_steps_by_scenario(scenario)
        current_steps = []
        next_steps = self.steps
        while next_steps:
            current_steps = next_steps
            next_steps = []
            for step in current_steps:
                if isinstance(step, DebugStep):
                    step.attch_shared_data_collector(self.shared_data_collector)
                step.run()
                next_steps.extend(step.get_next_steps())
