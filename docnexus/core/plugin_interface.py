from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class PluginInterface(ABC):
    """
    Abstract Base Class for all DocNexus plugins.
    Enforces a strict contract for initialization, cleanup, and metadata.
    """

    @abstractmethod
    def get_meta(self) -> Dict[str, Any]:
        """
        Return metadata about the plugin.
        Required keys: 'name', 'version', 'description', 'author'.
        """
        pass

    @abstractmethod
    def initialize(self, registry: Any) -> None:
        """
        Initialize the plugin.
        :param registry: Reference to the PluginRegistry singleton.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Cleanup resources before shutdown.
        """
        pass

    def get_features(self) -> List[Any]:
        """
        Return a list of Features or Algorithms provided by this plugin.
        Default implementation returns empty list.
        """
        return []
