import types

from TKT.cli import load_library


class TestLoadLibrary:
    def test_existing_module(self):
        module = load_library("TKT.cli")
        assert isinstance(module, types.ModuleType)
        assert hasattr(module, "load_library")
        assert module.load_library is load_library

    def test_non_existing_module(self):
        module = load_library("non_existing_module_12345")
        assert module is None

    def test_builtin_module(self):
        module = load_library("sys")
        assert isinstance(module, types.ModuleType)
        assert hasattr(module, "platform")

    def test_reimport_same_module(self):
        module1 = load_library("math")
        module2 = load_library("math")
        assert module1 is module2  # Python caches modules in sys.modules
