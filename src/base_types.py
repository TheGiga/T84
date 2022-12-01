from typing import Any

from src.errors import UniqueIdAlreadyTaken


class Unique:
    __instances__: dict[int: Any] = {}

    def __init__(self, uid: int, cls: Any):
        if uid in self.__instances__:
            raise UniqueIdAlreadyTaken(uid)

        self.uid = uid
        self.__instances__[uid] = cls

    @classmethod
    def get_from_id(cls, uid: int):
        return cls.__instances__.get(uid)


# Basically flags, but I was too lazy to make them somewhat special.

class Inventoriable:
    pass
