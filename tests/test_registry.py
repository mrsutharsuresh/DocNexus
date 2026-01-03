import unittest
import sys
import os
from unittest.mock import MagicMock

# Ensure we can import docnexus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from docnexus.core.plugin_interface import PluginInterface
from docnexus.core.registry import PluginRegistry

class MockPlugin(PluginInterface):
    def __init__(self, name="MockPlugin"):
        self.name = name
        self.initialized = False
        self.shutdown_called = False

    def get_meta(self):
        return {'name': self.name, 'version': '1.0.0'}

    def initialize(self, registry):
        self.initialized = True

    def shutdown(self):
        self.shutdown_called = True

class TestRegistry(unittest.TestCase):
    def setUp(self):
        # Reset Singleton for test isolation (hacky but necessary for singletons)
        PluginRegistry._instance = None
        self.registry = PluginRegistry()

    def test_singleton(self):
        reg2 = PluginRegistry()
        self.assertIs(self.registry, reg2)

    def test_register_and_get(self):
        plugin = MockPlugin("TestPlugin")
        self.registry.register(plugin)
        
        retrieved = self.registry.get_plugin("TestPlugin")
        self.assertIs(plugin, retrieved)
        self.assertEqual(len(self.registry.get_all_plugins()), 1)

    def test_initialization(self):
        plugin1 = MockPlugin("P1")
        plugin2 = MockPlugin("P2")
        self.registry.register(plugin1)
        self.registry.register(plugin2)
        
        self.registry.initialize_all()
        
        self.assertTrue(plugin1.initialized)
        self.assertTrue(plugin2.initialized)

    def test_invalid_registration(self):
        with self.assertRaises(TypeError):
            self.registry.register("NotAPlugin") # type: ignore

    def test_missing_metadata(self):
        class BadPlugin(PluginInterface):
            def get_meta(self): return {} # Missing name
            def initialize(self, reg): pass
            def shutdown(self): pass
            
        with self.assertRaises(ValueError):
            self.registry.register(BadPlugin())

if __name__ == '__main__':
    unittest.main()
