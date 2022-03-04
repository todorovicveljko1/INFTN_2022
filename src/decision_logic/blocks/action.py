from typing import Any, Callable

from src.utils.debugService import DebugService
from .base import BaseBlock, ActionState


class ActionBlock(BaseBlock):
    def __init__(self, method: Callable[[], Any], debug=False) -> None:
        super().__init__(debug=debug)
        self.method = method

    def handle(self) -> tuple[ActionState, Any]:
        if self.debug:
            return self._handle_debug()
        else:
            return self._handle()

    def _handle(self) -> tuple[ActionState, Any]:
        ret = self.method()
        if ret is None or ret is False:
            return (ActionState.FAIL, ret)
        return (ActionState.SUCCESS, ret)

    def _handle_debug(self) -> tuple[ActionState, Any]:
        DS = DebugService.getIstance()
        DS.startTime(self._id)
        ret = self.method()
        if ret is None or ret is False:
            DS.endTime(self._id, ActionState.FAIL)
            return (ActionState.FAIL, ret)

        DS.endTime(self._id, ActionState.SUCCESS)
        return (ActionState.SUCCESS, ret)

    def _debug_data_preset(self):
        DebugService.getIstance().addToDebug(self)

    def toJSON(self):
        return {"_id": self._id, "_type": self._type, "method": self.method.__name__}
