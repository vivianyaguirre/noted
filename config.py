# config.py  
import os


try:
    import tomllib as _toml  
    _OPEN_MODE = "rb"; _LOAD = _toml.load
except ModuleNotFoundError:
    import toml as _toml      
    _OPEN_MODE = "r";  _LOAD = _toml.load

class Config:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"config.toml not found at: {path}")
        try:
            with open(path, _OPEN_MODE) as f:
                self._data = _LOAD(f)
        except Exception as e:
            raise RuntimeError(f"Failed to parse TOML at {path}: {e}") from e

    def __getattr__(self, name: str):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Missing config key: {name}")

_here = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_here, "config.toml")


config = Config(_config_path)
