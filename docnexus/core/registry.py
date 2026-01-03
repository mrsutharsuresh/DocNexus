import logging
from typing import Dict, Optional, List
from .plugin_interface import PluginInterface

logger = logging.getLogger(__name__)

class PluginRegistry:
    """
    Singleton Registry for managing DocNexus plugins.
    Handles registration, retrieval, and lifecycle events.
    """
    _instance = None
    _plugins: Dict[str, PluginInterface] = {}
    _custom_slots: Dict[str, List[str]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginRegistry, cls).__new__(cls)
            cls._instance._plugins = {}
            cls._instance._custom_slots = {}
        return cls._instance

    def register_slot(self, slot_name: str, content: str) -> None:
        """
        Register content for a specific UI slot.
        Appends the content to the list for that slot.
        """
        if slot_name not in self._custom_slots:
            self._custom_slots[slot_name] = []
        self._custom_slots[slot_name].append(content)
        logger.debug(f"Registered content for slot: {slot_name}")

    def get_slots(self, slot_name: str) -> List[str]:
        """
        Retrieve all content registered for a specific slot.
        Returns a list of safe HTML strings.
        """
        return self._custom_slots.get(slot_name, [])

    def register(self, plugin: PluginInterface) -> None:
        """
        Register a new plugin instance.
        Validates the interface and metadata.
        """
        if not isinstance(plugin, PluginInterface):
            raise TypeError("Plugin must inherit from PluginInterface")

        meta = plugin.get_meta()
        name = meta.get('name')
        
        if not name:
            raise ValueError("Plugin metadata must include 'name'")
            
        if name in self._plugins:
            logger.warning(f"Plugin '{name}' is already registered. Overwriting.")
            
        self._plugins[name] = plugin
        logger.info(f"Registered plugin: {name} v{meta.get('version', '0.0.0')}")

    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Retrieve a specific plugin by name."""
        return self._plugins.get(name)

    def get_all_plugins(self) -> List[PluginInterface]:
        """Return a list of all registered plugins."""
        return list(self._plugins.values())

    def initialize_all(self) -> None:
        """
        Initialize all registered plugins.
        """
        for name, plugin in self._plugins.items():
            try:
                plugin.initialize(self)
                logger.info(f"Initialized plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin '{name}': {e}", exc_info=True)

    def shutdown_all(self) -> None:
        """
        Shutdown all plugins in reverse order of registration (conceptually).
        """
        for name, plugin in self._plugins.items():
            try:
                plugin.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down plugin '{name}': {e}")
