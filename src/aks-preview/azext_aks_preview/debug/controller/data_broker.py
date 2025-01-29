from ..data_collector.data_collector import (InspektorGadgetDataCollector,
                                             KubernetesDataCollector)
from .tool_manager import ToolManager


class DataBroker:
    def __init__(self, tool_manager: ToolManager) -> None:
        self.tool_manager = tool_manager
        self.k8s_data_collector = KubernetesDataCollector(tool_manager)
        self.ig_data_collector = InspektorGadgetDataCollector(tool_manager)

    def close(self):
        self.k8s_data_collector.progress_hook.end()
        self.ig_data_collector.progress_hook.end()
