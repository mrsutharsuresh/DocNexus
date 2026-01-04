# Plugin Development Guide

Welcome to the DocNexus Plugin Ecosystem! This guide will help you build, test, and publish plugins that work seamlessly with DocNexus Core.

## 🏗️ The "Passive" Philosophy

DocNexus uses a **Passive Plugin Architecture**. This means your plugin should **NOT** import any code from the `docnexus` package directly. Instead, the Core application **injects** the necessary classes and API handles into your plugin at runtime.

**Why?**
- **Stability**: Prevents "Split-Brain" issues where your plugin uses a different version of a class than the Core.
- **Portability**: Your plugin works on any version of DocNexus that supports the API protocol.
- **Sandboxing**: Errors in your plugin are less likely to crash the whole application.

---

## 🚀 Getting Started

### 1. Prerequisities
- A working installation of DocNexus (see [Quick Start](../README.md)).
- Python 3.10+.

### 2. Plugin Structure
A plugin is simply a folder inside `docnexus/plugins/`. It must contain at least a `plugin.py`.

```text
docnexus/
└── plugins/
    └── my_awesome_plugin/   <-- Your unique plugin ID
        ├── plugin.py        <-- REQUIRED: The entry point
        ├── config.yaml      <-- Optional
        └── assets/          <-- Optional styles/scripts
```

---

## 💻 Writing Your First Plugin

The only requirement for `plugin.py` is that it defines a function called `get_features()`.

### The `get_features()` Hook

When DocNexus loads your plugin, it calls `get_features()`. Before doing so, it **injects** the following classes into your global namespace:
- `Feature`
- `FeatureType`
- `FeatureState`
- `PluginRegistry`

**Do NOT import these at the top of your file.**

### Example: "Hello World" UI Slot

This plugin adds a custom message to the Sidebar.

**`docnexus/plugins/hello_world/plugin.py`**:
```python
import logging

# Set up your own logger
logger = logging.getLogger(__name__)

def get_features():
    """
    Entry point called by DocNexus Loader.
    Returns a list of Feature objects.
    """
    
    # 1. Access Injected Classes
    # (These are available as globals at runtime)
    _Registry = globals().get('PluginRegistry')
    _Feature = globals().get('Feature')
    _FeatureType = globals().get('FeatureType')
    
    # 2. Register a UI Slot
    # Slots allow you to inject HTML into specific areas of the app
    reg = _Registry() # Singleton instance
    
    html_content = """
    <div style="padding: 10px; background: #e0e7ff; border-radius: 8px; margin-top: 10px;">
        <strong>🚀 Hello Builder!</strong><br>
        Your plugin is running.
    </div>
    """
    
    # Available Slots: HEADER_RIGHT, SIDEBAR_BOTTOM, CONTENT_START, CONTENT_END, EXPORT_MENU
    reg.register_slot('SIDEBAR_BOTTOM', html_content)
    
    logger.info("Hello World plugin initialized!")

    # 3. Return Features (Optional if just using slots, but good practice)
    # This makes your plugin show up in the "Installed Features" list (future)
    return [
        _Feature(
            name="Hello World UI",
            feature_type=_FeatureType.UI_EXTENSION,
            handler=None # No backend logic needed for static HTML
        )
    ]
```

### Example: Advanced Feature (Export Handler)

**`docnexus/plugins/my_exporter/plugin.py`**:
```python
def custom_export_logic(html_content):
    return b"processed binary data"

def get_features():
    _Feature = globals().get('Feature')
    _FeatureType = globals().get('FeatureType')
    
    # Register a new export capabilities
    # This will handle /api/export/custom requests
    return [
        _Feature(
            name="Custom Exporter",
            feature_type=_FeatureType.EXPORT_HANDLER,
            handler=custom_export_logic
        )
    ]
```

---

## 🧪 Testing Your Plugin

1.  **Develop Locally**:
    Create your plugin folder in `d:\Code\DocNexusCorp\DocNexus\docnexus\plugins\<your_plugin_name>`.
    
2.  **Run DocNexus**:
    ```bash
    docnexus start
    # or
    python run.py
    ```
    
3.  **Verify**:
    - Check the logs (`docnexus.log`) for "Loaded plugin: <your_plugin_name>".
    - Open the web UI (`http://localhost:8000`) and see if your changes (like UI slots) are visible.

---

## 📦 Publishing to Marketplace

To package your plugin for distribution:
1.  Ensure all your code is self-contained in your folder.
2.  Remove `__pycache__`.
3.  Zip the folder: `my_awesome_plugin.zip`.

Users will install it by simply extracting it into their `plugins/` directory.

## ⚠️ Best Practices

1.  **Error Handling**: Wrap your logic in `try/except` blocks. If your plugin crashes, it shouldn't take down the server.
2.  **No Core Imports**: Never write `from docnexus.core import ...`. Always rely on injected globals or widely available standard libraries (json, requests, etc.).
3.  **Assets**: If you need images or CSS, use `base64` encoding inline for simplicity, or host them externally if possible, as local asset serving from plugin folders requires advanced configuration.
