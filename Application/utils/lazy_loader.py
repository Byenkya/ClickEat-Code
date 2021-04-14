import importlib
import types

class LazyLoader:
    def __init__(self, lib_name):
        self.lib_name = lib_name
        self._mod = None

    def _load_module(self):
        module = importlib.import_module(self.lib_name)
        return module

    def __getattr__(self, attr):
        try:
            if self._mod is None:
                self._mod = self._load_module()
            return getattr(self._mod, attr)

        except Exception as e:
            print("Lazy loading error: ", e)
            raise

    def __dir__(self):
        if self._mod is None:
            module = self._load_module()
        return dir(module)
