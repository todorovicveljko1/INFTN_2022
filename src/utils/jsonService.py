import json
from typing import TypeVar, Type

from .mapData import MapData

T = TypeVar('T', bound='JsonService')


class JsonService:
    _instance: T = None

    @classmethod
    def getIstance(cls) -> T:
        if cls._instance is None:
            cls._instance = JsonService()
        return cls._instance

    def __init__(self) -> None:
        self._id = 0
        self._type = ""
        self.root = None
        self.turns = []
        self.data = MapData()

    def setBase(self, _id: int, _type: str, root):
        self._id = _id
        self._type = _type
        self.root = root

    def setInitMapData(self, data: MapData):
        self.data = data

    def addTurn(self, json):
        self.turns.append(json)

    def toJSON(self):
        return {
            "root": self.root,
            "_id": self._id,
            "_type": self._id,
            "turns": self.turns,
            "data": self.data.toJson(True)
        }
