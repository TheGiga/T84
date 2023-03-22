import uuid
from typing import Any

class Unique:
    __instances__: dict[str: Any] = {}

    def __init__(self, cls: Any, key: str = None):

        if not key:
            key = str(uuid.uuid4())

        if key in self.__instances__:
            print(f"⚠ Key {key} is taken, changing to random value.")
            key = str(uuid.uuid4())

        self.key = key
        self.__instances__[key] = cls

    @classmethod
    def get_from_key(cls, key: str) -> Any | None:
        return cls.__instances__.get(key)
