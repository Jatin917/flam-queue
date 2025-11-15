import json
from pathlib import Path


class Config:
    DEFAULTS = {"max_retries": 3, "backoff_base": 2}

    @staticmethod
    def _get_config_path():
        """Get the absolute path to the config file, creating directory if needed."""
        # Get the directory where this config.py file is located
        config_dir = Path(__file__).parent
        data_dir = config_dir / "data"
        # Create data directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        return data_dir / "config.json"

    def __init__(self, values: dict):
        self.values = values

    @classmethod
    def load(cls, path=None):
        if path is None:
            path = cls._get_config_path()
        else:
            path = Path(path)
            # Create parent directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, "r") as f:
                text = f.read().strip()
                if not text:
                    # empty file → use defaults
                    return cls(cls.DEFAULTS.copy())
                data = json.loads(text)
                return cls(data)
        except FileNotFoundError:
            return cls(cls.DEFAULTS.copy())

    def save(self, path=None):
        if path is None:
            path = self._get_config_path()
        else:
            path = Path(path)
            # Create parent directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(self.values, f, indent=2)


    def set(self, k, v):
        self.values[k] = v


    def get(self, k):
        return self.values.get(k)