import json


class Config:
    DEFAULTS = {"max_retries": 3, "backoff_base": 2}


    def __init__(self, values: dict):
        self.values = values


    @classmethod
    def load(cls, path="./data/config.json"):
        try:
            with open(path) as f:
                return cls(json.load(f))
        except FileNotFoundError:
            return cls(cls.DEFAULTS.copy())


    def save(self, path="./data/config.json"):
        with open(path, "w") as f:
            json.dump(self.values, f)


    def set(self, k, v):
        self.values[k] = v


    def get(self, k):
        return self.values.get(k)