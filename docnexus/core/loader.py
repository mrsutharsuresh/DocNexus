import sys
import os
import importlib.util
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Constants
PLUGIN_FILE_NAME = "plugin.py"
DEV_PLUGIN_DIR_NAME = "plugins_dev"
PROD_PLUGIN_DIR_NAME = "plugins"

def get_base_path() -> Path:
    """
    Determine the base path of the application.
    Handles PyInstaller's sys._MEIPASS logic.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        # For plugins adjacent to EXE, we use sys.executable dir
        # For plugins embedded (if any), we'd use sys._MEIPASS
        # Strategy: Look for 'plugins' folder next to EXE
        return Path(sys.executable).parent
    else:
        # Running as source
        # Base path is the project root (assuming run.py is at root)
        return Path(os.path.abspath("."))

def get_plugin_paths() -> List[Path]:
    """
    Return a list of directories to scan for plugins based on environment.
    """
    paths = []
    base_path = get_base_path()
    
    # Check for Prod Plugins folder (dist/plugins)
    prod_plugins = base_path / PROD_PLUGIN_DIR_NAME
    if prod_plugins.exists() and prod_plugins.is_dir():
        paths.append(prod_plugins)
        
    # Check for Dev Plugins folder (docnexus/plugins_dev)
    # Note: In source, 'docnexus' is usually a subdir of CWD
    dev_plugins = base_path / "docnexus" / DEV_PLUGIN_DIR_NAME
    if dev_plugins.exists() and dev_plugins.is_dir():
        paths.append(dev_plugins)
        
    logger.debug(f"Plugin scan paths: {[str(p) for p in paths]}")
    return paths

def load_plugins_from_path(plugin_dir: Path) -> None:
    """
    Scan a specific directory for plugins and load them.
    Expects structure: plugin_dir/my_plugin/plugin.py
    """
    if not plugin_dir.exists():
        return

    logger.info(f"Scanning for plugins in: {plugin_dir}")

    # Iterate over subdirectories
    for item in plugin_dir.iterdir():
        if item.is_dir():
            plugin_path = item / PLUGIN_FILE_NAME
            if plugin_path.exists():
                load_single_plugin(item.name, plugin_path)

def load_single_plugin(name: str, path: Path) -> None:
    """
    Import and instantiate a plugin from a file path.
    """
    try:
        logger.info(f"Loading plugin '{name}' from {path}")
        
        spec = importlib.util.spec_from_file_location(f"plugins.{name}", str(path))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            logger.info(f"Successfully loaded module for plugin: {name}")
            
            # Note: We rely on the plugin code itself to register with the registry locally.
            # Usually: PluginRegistry().register(MyPlugin()) in the module body or init.
            
    except Exception as e:
        logger.error(f"Failed to load plugin '{name}': {e}", exc_info=True)

def load_plugins() -> None:
    """
    Main entry point to discover and load all available plugins.
    """
    search_paths = get_plugin_paths()
    for path in search_paths:
        load_plugins_from_path(path)
