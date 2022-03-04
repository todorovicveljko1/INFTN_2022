from typing import Any, Callable

from src.utils.debugService import DebugService
from .base import ActionState, BaseBlock


class DecisionBlock(BaseBlock):
    def __init__(self,
                 condition: Callable[[], bool],
                 true: BaseBlock,
                 false: BaseBlock,
                 debug=False
                 ) -> None:
        super().__init__(debug=debug)
        self.condition = condition
        self.true = true
        self.false = false

    def handle(self) -> tuple[ActionState, Any]:
        if self.debug:
            return self._handle_debug()
        else:
            return self._handle()

    def _handle(self) -> tuple[ActionState, Any]:
        condition_ret = self.condition()
        if condition_ret:
            return self.true.handle()
        else:
            return self.false.handle()

    def _handle_debug(self) -> tuple[ActionState, Any]:
        DS = DebugService.getIstance()
        DS.startTime(self._id)
        condition_ret = self.condition()
        if condition_ret:
            ret = self.true.handle()
            DS.endTime(self._id, ret[0])
            return ret
        else:
            ret = self.false.handle()
            DS.endTime(self._id, ret[0])
            return ret

    def _debug_data_preset(self):
        DebugService.getIstance().addToDebug(self)
        self.true._debug_data_preset()
        self.false._debug_data_preset()

    def toJSON(self):

        return {
            "_id": self._id,
            "_type": self._type,
            "method": self.condition.__name__,
            "childrens": [self.true.toJSON(), self.false.toJSON()]
        }
