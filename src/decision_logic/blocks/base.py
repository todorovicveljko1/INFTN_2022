from enum import Enum
from typing import Any


class ActionState(Enum):
    FAIL = 0
    SUCCESS = 1
    PENDING = 2


class BaseBlock:
    ID: int = 0

    def __init__(self, debug=False) -> None:
        # Basic info setup
        self._id: int = BaseBlock.ID
        self._type: str = self.__class__.__name__
        self.debug: bool = debug
        BaseBlock.ID += 1

    def handle(self) -> tuple[ActionState, Any]:
        return (ActionState.FAIL, None)

    def _debug_data_preset(self):
        pass

    def toJSON(self):
        pass
