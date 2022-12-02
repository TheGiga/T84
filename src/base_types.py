from typing import Any

from src import UniqueIdAlreadyTaken


class Unique:
    __instances__: dict[int: Any] = {}

    def __init__(self, uid: int, cls: Any):
        if uid in self.__instances__:
            raise UniqueIdAlreadyTaken(uid)

        self.uid = uid
        self.__instances__[uid] = cls

    @property
    def instances(self) -> dict:
        return self.__instances__

    @classmethod
    def get_from_id(cls, uid: int) -> Any:
        return cls.__instances__.get(uid)


# Basically flags, but I was too lazy to make them somewhat special.

class Inventoriable:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
