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
    *   **Shared**:
        *   `HEADER_RIGHT`: Icons/Buttons in the top navigation bar.
    *   **Index Page (`index.html`)**:
        *   `MAIN_TOP`: Just below header, above content grid.
        *   `FOOTER_RIGHT`: Bottom right corner.
    *   **View Page (`view.html`)**:
        *   `EXPORT_MENU`: Inside the "Export" dropdown.
        *   `SIDEBAR_BOTTOM`: Bottom of the right-side TOC sidebar.
        *   `CONTENT_START`: Top of the document content area.
        *   `CONTENT_END`: Bottom of the document content area.

### 5. Feature Framework (Registry Facade)

Refactored in v1.2.3, the `FeatureManager` acts as a facade, pulling capabilities ("Features") from registered plugins.

#### Feature Types
*   **ALGORITHM**: Text transformation logic (e.g., standardizing headers, converting tables, generating TOCs). Chained together in a `Pipeline`.
*   **UI_EXTENSION**: Legacy/Misc UI logic.
*   **EXPORT_HANDLER**: Custom export logic (e.g., PDF, DOCX).

#### Pipeline Backbone
The `Pipeline` class represents a sequence of `ALGORITHM` features.
1.  **Construction**: `FeatureManager.build_pipeline(enable_experimental)`
2.  **Execution**: `pipeline.run(markdown_content)`
3.  **Lego Blocks**: Plugins can provide their own "blocks" (Algorithms) which are automatically inserted into the pipeline.

#### Declaring Features
Plugins override `get_features()` to expose their capabilities:

```python
def get_features(self) -> List[Any]:
    return [
        Feature("MY_ALGORITHM", self.my_handler, FeatureState.STANDARD, FeatureType.ALGORITHM)
    ]
```

## Usage

### Registration
Plugins are registered via `PluginRegistry().register(instance)`. This is typically done by the plugin loader (`loader.py`).

### Initialization
1.  **Loader**: `loader.py` scans appropriate directories (including `sys._MEIPASS` when frozen).
2.  **Registration**: Plugins register themselves.
3.  **App Startup**: `app.py` calls `PluginRegistry().initialize_all()`.
4.  **Feature Refresh**: `app.py` calls `FEATURES.refresh()` to pull features from initialized plugins into the `FeatureManager`.

## Directory Structure
*   `docnexus/core/plugin_interface.py`: The Contract (ABC).
*   `docnexus/core/registry.py`: The State (Singleton PluginRegistry).
*   `docnexus/core/loader.py`: The Discovery (File Scanner).
*   `docnexus/features/registry.py`: The Facade (FeatureManager & Pipeline).
