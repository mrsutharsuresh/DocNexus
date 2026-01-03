# Plugin Architecture (v1.2.1)

This document outlines the architecture for the DocNexus Plugin System, introduced in v1.2.1.

## Core Concepts

The plugin system is built on two foundational components located in `docnexus/core`:

1.  **PluginInterface (`plugin_interface.py`)**
2.  **PluginRegistry (`registry.py`)**

### 1. PluginInterface (The Contract)

All plugins **MUST** inherit from the abstract base class `PluginInterface`. This enforces a strict contract for lifecycle management.

```python
class PluginInterface(ABC):
    @abstractmethod
    def get_meta(self) -> Dict[str, Any]: ...
    
    @abstractmethod
    def initialize(self, registry: Any) -> None: ...
    
    @abstractmethod
    def shutdown(self) -> None: ...
```

*   **`get_meta()`**: Returns metadata (name, version, author). Used for dependency resolution and UI display.
*   **`initialize(registry)`**: The setup hook. This is where plugins register routes, add UI slots, or hook into the processing pipeline. It receives the `registry` instance to interact with other plugins.
*   **`shutdown()`**: Cleanup hook for closing handles/connections.

### 2. PluginRegistry (The Manager)

The `PluginRegistry` is a **Singleton** that acts as the central hub.

*   **Centralized Tracking**: Maintains a dictionary of all active plugins.
*   **Lifecycle Orchestration**: Responsible for calling `initialize()` and `shutdown()` on all plugins in the correct order.
*   **API Access**: Provides methods like `get_plugin(name)` for inter-plugin communication.

### 3. PluginLoader (`loader.py`)

Introduced in v1.2.2, the loader handles the discovery of plugin modules from the filesystem.

*   **Split-Environment Strategy**:
    *   **Development**: Scans `docnexus/plugins_dev` (typically a junction to the source).
    *   **Production**: Scans `plugins/` directory adjacent to the executable.
*   **Dynamic Import**: Uses `importlib` to load `plugin.py` files found in these directories.
*   **Auto-Registration**: Plugins are expected to register themselves upon import (e.g., `PluginRegistry().register(MyPlugin())`).

### 4. UI Slots (`registry.register_slot`)

Plugins can inject content into predefined areas (Slots) of the UI.

*   **Mechanism**: `registry.register_slot(slot_name, html_content)`
*   **Rendering**: Flask templates iterate over `get_slots(slot_name)` and render the HTML safely.
*   **Available Slots**:
    *   `HEADER_RIGHT`: Icons/Buttons in the top navigation bar.

## Usage

### Registration
Plugins are registered via `PluginRegistry().register(instance)`. This is typically done by the plugin loader or manual registration in `app.py`.

### Initialization
The application calls `load_plugins()` followed by `PluginRegistry().initialize_all()` during startup.

## Future Roadmap

*   **v1.2.3**: UI Slot Integration (React Mount Points).
