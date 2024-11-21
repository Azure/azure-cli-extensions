from .tool_manager import ToolManager
from ..data_collector.data_collector import KubernetesDataCollector, InspektorGadgetDataCollector


class DataBroker:
    def __init__(self, tool_manager: ToolManager) -> None:
        self.tool_manager = tool_manager
        self.k8s_data_collector = KubernetesDataCollector(tool_manager)
        self.ig_data_collector = InspektorGadgetDataCollector(tool_manager)
