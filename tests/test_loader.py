import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docnexus.core.registry import PluginRegistry
from docnexus.core.plugin_interface import PluginInterface

class MockPlugin(PluginInterface):
    def get_meta(self):
        return {'name': 'mock_plugin', 'version': '1.0', 'description': 'Mock', 'author': 'Test'}
    
    def initialize(self, registry):
        pass
        
    def shutdown(self):
        pass

class TestPluginRegistry(unittest.TestCase):
    def setUp(self):
        # Reset singleton state
        PluginRegistry._instance = None
        self.registry = PluginRegistry()

    def test_singleton_behavior(self):
        reg1 = PluginRegistry()
        reg2 = PluginRegistry()
        self.assertIs(reg1, reg2)

    def test_register_plugin(self):
        plugin = MockPlugin()
        self.registry.register(plugin)
        self.assertIsNotNone(self.registry.get_plugin('mock_plugin'))
        self.assertEqual(self.registry.get_plugin('mock_plugin'), plugin)

    def test_register_invalid_plugin(self):
        with self.assertRaises(TypeError):
            self.registry.register("not a plugin")

    def test_register_slot(self):
        self.registry.register_slot("HEADER_RIGHT", "<div>Test</div>")
        slots = self.registry.get_slots("HEADER_RIGHT")
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0], "<div>Test</div>")

if __name__ == '__main__':
    unittest.main()
