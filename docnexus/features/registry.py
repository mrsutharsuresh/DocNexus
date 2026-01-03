from enum import Enum, auto
from typing import Callable, List, Optional, Any
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
    def __init__(self, name: str, handler: Callable[[str], str], state: FeatureState, feature_type: FeatureType = FeatureType.ALGORITHM):
        self.name = name
        self.handler = handler
        self.state = state
        self.type = feature_type

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
        plugins = self._registry.get_all_plugins()
        count = 0
        for plugin in plugins:
            if hasattr(plugin, 'get_features'):
                try:
                    features = plugin.get_features()
                    for f in features:
                        if isinstance(f, Feature):
                            self._features.append(f)
                            count += 1
                            logger.debug(f"Registered plugin feature: {f.name}")
                except Exception as e:
                    logger.error(f"Failed to get features from plugin {plugin}: {e}")
        logger.info(f"FeatureManager: Loaded {count} features from plugins.")

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

            if f.state == FeatureState.STANDARD:
                pipeline.add_step(f.handler)
            elif enable_experimental and f.state == FeatureState.EXPERIMENTAL:
                pipeline.add_step(f.handler)
        
        return pipeline
