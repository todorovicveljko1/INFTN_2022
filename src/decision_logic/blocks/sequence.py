from typing import Any, Iterable

from src.utils.debugService import DebugService
from .base import ActionState, BaseBlock


class SequenceBlock(BaseBlock):
    def __init__(self, seq: Iterable[BaseBlock], debug=False) -> None:
        super().__init__(debug=debug)
        self.seq = seq

    def handle(self) -> tuple[ActionState, Any]:
        if self.debug:
            return self._handle_debug()
        else:
            return self._handle()

    def _handle(self) -> tuple[ActionState, Any]:
        for i in self.seq:
            ret = i.handle()
            if ret[0] is ActionState.SUCCESS:
                return ret
        return (ActionState.FAIL, None)

    def _handle_debug(self) -> tuple[ActionState, Any]:

        DS = DebugService.getIstance()
        DS.startTime(self._id)
        for i in self.seq:
            ret = i.handle()
            if ret[0] is ActionState.SUCCESS:
                DS.endTime(self._id, ActionState.SUCCESS)
                return ret

        DS.endTime(self._id, ActionState.FAIL)
        return (ActionState.FAIL, None)

    def _debug_data_preset(self):
        DebugService.getIstance().addToDebug(self)
        for i in self.seq:
            i._debug_data_preset()

    def toJSON(self):
        return {
            "_id": self._id,
            "_type": self._type,
            "childrens": [seq.toJSON() for seq in self.seq]
        }
