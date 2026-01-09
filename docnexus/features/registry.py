from enum import Enum, auto
from typing import Callable, List, Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

class FeatureState(Enum):
    STANDARD = auto()
    EXPERIMENTAL = auto()

class FeatureType(Enum):
    ALGORITHM = auto() # Markdown processing, text transformation
    UI_EXTENSION = auto() # Legacy/Other
    EXPORT_HANDLER = auto()

class Feature:
    def __init__(self, name: str, handler: Callable[[str], Any], state: FeatureState, feature_type: FeatureType = FeatureType.ALGORITHM, meta: Dict = None):
        self.name = name
        self.handler = handler
        self.state = state
        self.type = feature_type
        self.meta = meta or {}

class Pipeline:
    """
    A sequence of algorithms (Features) to be executed in order.
    The 'Backbone' of document processing.
    """
    def __init__(self, name: str):
        self.name = name
        self._steps: List[Callable[[str], str]] = []

    def add_step(self, handler: Callable[[str], str]):
        self._steps.append(handler)

    def run(self, content: str) -> str:
        """Execute the pipeline on the content."""
        for step in self._steps:
            try:
                content = step(content)
            except Exception as e:
                logger.error(f"Pipeline {self.name} step {step.__name__ if hasattr(step, '__name__') else 'unknown'} failed: {e}")
                # specific strategy for failure? For now, log and continue with partial content
        return content
    
    def __iter__(self):
        """Allow iteration for backward compatibility if needed."""
        return iter(self._steps)

class PluginRegistry:
    """
    Singleton Registry to hold all discovered plugin modules/features.
    Ensure shared state across the application.
    """
    _instance = None
    _plugins = []
    _custom_slots: Dict[str, List[str]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginRegistry, cls).__new__(cls)
            cls._instance._plugins = []
            cls._instance = super(PluginRegistry, cls).__new__(cls)
            cls._instance._plugins = []
            cls._instance._custom_slots = {}
            cls._instance._blueprints = []
        return cls._instance

    def register(self, plugin_or_feature: Any):
        """Register a plugin module or feature."""
        # Avoid duplicate registration
        if plugin_or_feature not in self._plugins:
            self._plugins.append(plugin_or_feature)
            logger.info(f"PluginRegistry: Registered {plugin_or_feature}")

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

    def get_all_plugins(self) -> List[Any]:
        return self._plugins

    def register_blueprint(self, bp: Any):
        """Register a Flask Blueprint."""
        if bp not in self._blueprints:
            self._blueprints.append(bp)
            logger.info(f"PluginRegistry: Registered blueprint {bp.name}")

    def register_blueprints(self, app):
        """Register all collected blueprints with the Flask app."""
        for bp in self._blueprints:
            try:
                app.register_blueprint(bp)
                logger.info(f"Registered blueprint: {bp.name}")
            except Exception as e:
                logger.error(f"Failed to register blueprint {bp.name}: {e}")
    
    def initialize_all(self):
        """
        Optional: Trigger initialization logic on all plugins if they have it.
        """
        for plugin in self._plugins:
            # Check for standard initialize
            if hasattr(plugin, 'initialize'):
                try:
                    plugin.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize plugin {plugin}: {e}")
            # Check for legacy initialize(registry) if strictly needed, though we moved to DI
                except Exception as e:
                    logger.error(f"Failed to initialize plugin {plugin}: {e}")

class FeatureManager:
    """
    Facade that aggregates features from the PluginRegistry and manages Pipelines.
    """
    def __init__(self, registry: Optional[Any] = None):
        self._features: List[Feature] = []
        self._registry = registry

    def register(self, feature: Feature):
        """Register a feature manually (Core features)."""
        self._features.append(feature)

    def refresh(self):
        """Pull features from the attached PluginRegistry."""
        if not self._registry:
            return
        
        logger.info("FeatureManager: Refreshing features from Registry...")
        # Clear existing plugin features to avoid duplicates (preserving core if mixed, but here simpler)
        # Actually, self._features grows indefinitely? Let's reset it to safe core state? 
        # For now, just logging.
        plugins = self._registry.get_all_plugins()
        count = 0
        for plugin in plugins:
            # Duck typing check instead of strict isinstance to survive import/reload cycles
            if hasattr(plugin, 'name') and hasattr(plugin, 'type') and hasattr(plugin, 'handler'):
                 # Check for existing feature by name
                 existing_idx = next((i for i, f in enumerate(self._features) if f.name == plugin.name), -1)
                 
                 if existing_idx >= 0:
                     # Update/Replace existing feature
                     # This ensures that if the plugin reloaded with new metadata (e.g. installed=True), 
                     # we use the latest version.
                     old_feature = self._features[existing_idx]
                     self._features[existing_idx] = plugin
                     logger.info(f"FeatureManager: Updated feature '{plugin.name}' (State: {plugin.state})")
                 else:
                    self._features.append(plugin)
                    count += 1
                    logger.debug(f"Registered plugin feature (duck-typed): {plugin.name}")
            elif hasattr(plugin, 'get_features'):
                 # Legacy path (should be unused now)
                 pass

        logger.info(f"FeatureManager: Loaded/Updated features. Total: {len(self._features)}")

    def is_feature_installed(self, feature: Feature) -> bool:
        """
        Centralized validation for feature availability.
        Checks:
        1. 'installed' meta flag (Plugins)
        2. Any future license checks or dependency checks
        """
        # Default to True (Core features usually don't have this flag)
        installed = feature.meta.get('installed', True)
        
        # DEBUG LOGGING for validation
        if not installed:
            logger.debug(f"FeatureManager: BLOCKED access to uninstalled feature '{feature.name}'")
        else:
            # logger.debug(f"FeatureManager: ALLOWED access to feature '{feature.name}'")
            pass
            
        return installed

    def get_export_handler(self, format_ext: str) -> Optional[Callable]:
        """
        Retrieve a registered export handler for a specific format extension.
        """
        logger.debug(f"FeatureManager: Looking for export handler for '{format_ext}'...")
        
        for feature in self._features:
            # Flexible type checking
            ft_type = str(feature.type) # e.g. "FeatureType.EXPORT_HANDLER"
            
            if "EXPORT_HANDLER" in ft_type:
                match = False
                # Check meta 'extension' tag first
                if getattr(feature, 'meta', {}).get('extension') == format_ext:
                    match = True
                # Fallback to name match
                elif feature.name == format_ext or feature.name == f"{format_ext}_export":
                   match = True
                   
                if match:
                    # Enforce Centralized Control
                    if self.is_feature_installed(feature):
                        logger.info(f"FeatureManager: Found and Verified handler for {format_ext} ({feature.name})")
                        return feature.handler
                    else:
                        logger.warning(f"FeatureManager: Found handler for {format_ext} ({feature.name}) but it is NOT INSTALLED.")
                        # Continue searching? Or return None immediately to block?
                        # If we find a match but it's uninstalled, we should probably stop and return None 
                        # to prevent finding a "fallback" (though unlikely for same ext).
                        # returning None triggers the 404 MISSING_PLUGIN workflow.
                        return None
        
        logger.warning(f"FeatureManager: No handler found for {format_ext}. Available: {[f.name for f in self._features]}")
        return None

    def build_pipeline(self, enable_experimental: bool) -> Pipeline:
        """
        Build the standard processing pipeline.
        Returns a Pipeline object.
        """
        pipeline = Pipeline("StandardPipeline")
        
        # Sort or prioritize? 
        # Currently we rely on insertion order: Core features first (registered in app.py), then Plugins.
        for f in self._features:
            if f.type != FeatureType.ALGORITHM:
                continue

            # Enforce Centralized Control
            if not self.is_feature_installed(f):
                continue
                
            if f.state == FeatureState.STANDARD:
                pipeline.add_step(f.handler)
            elif enable_experimental and f.state == FeatureState.EXPERIMENTAL:
                pipeline.add_step(f.handler)
        
        return pipeline
