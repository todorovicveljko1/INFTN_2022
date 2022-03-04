
import time
from typing import TypeVar

from src.decision_logic.blocks.base import ActionState, BaseBlock
from src.utils.mapData import MapData

T = TypeVar('T', bound='DebugService')


class DebugService:

    _instance: T = None

    @classmethod
    def getIstance(cls) -> T:
        if cls._instance is None:
            cls._instance = DebugService()
        return cls._instance

    def __init__(self) -> None:
        self.turn = -1
        self.debug = {}
        self.data = MapData()

        pass

    def nextTurn(self) -> None:
        self.turn += 1
        self.debug = {}
        self.data = MapData()

    def addToDebug(self, block: BaseBlock) -> None:
        self.debug[block._id] = {"time": 0, "status": ActionState.PENDING.name}

    def startTime(self, _id: int) -> None:
        self.debug[_id]['time'] = time.perf_counter_ns()

    def endTime(self, _id: int, status: ActionState = ActionState.SUCCESS) -> None:
        self.debug[_id]['time'] = time.perf_counter_ns() - \
            self.debug[_id]['time']
        self.debug[_id]['status'] = status.name

    def toJSON(self):
        return {
            "debug": self.debug,
            "data": self.data.toJson(),
        }
