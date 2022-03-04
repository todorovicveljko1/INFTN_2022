from typing import Any, Callable, Iterable
from src.decision_logic.blocks.action import ActionBlock
from src.decision_logic.blocks.base import ActionState, BaseBlock
from src.decision_logic.blocks.sequence import SequenceBlock
from src.decision_logic.blocks.decision import DecisionBlock
from src.utils.jsonService import JsonService
from src.utils.debugService import DebugService


class DecisionLogic(BaseBlock):
    def __init__(self, debug=False) -> None:
        super().__init__(debug=debug)
        self.root: BaseBlock = None

    def handle(self) -> tuple[ActionState, Any]:
        if self.debug:
            return self._handle_debug()
        else:
            return self._handle()

    def _handle(self) -> tuple[ActionState, Any]:
        return self.root.handle()

    def _handle_debug(self) -> tuple[ActionState, Any]:
        self._debug_data_preset()
        DebugService.getIstance().startTime(self._id)
        ret = self.root.handle()
        DebugService.getIstance().endTime(self._id, ret[0])
        return ret

    def _debug_data_preset(self):
        DS = DebugService.getIstance()
        if DS.turn != -1:
            JsonService.getIstance().addTurn(DS.toJSON())
        DS.nextTurn()
        DS.addToDebug(self)
        self.root._debug_data_preset()

    # Sequenc builder
    def _SEQ(self, seq: Iterable[BaseBlock]) -> SequenceBlock:
        return SequenceBlock(seq, debug=self.debug)

    # Action lookup
    def _ACT(self, method: Callable[[], Any]) -> ActionBlock:
        return ActionBlock(method, debug=self.debug)
    # If block

    def _IF(self, condition: Callable[[], bool], true: BaseBlock, false: BaseBlock = BaseBlock()) -> DecisionBlock:
        return DecisionBlock(condition, true, false, debug=self.debug)

    def toJSON(self):
        return {"_id": self._id, "_type": self._type, "root": self.root.toJSON()}

    def setToJsonService(self):
        DS = DebugService.getIstance()
        JsonService.getIstance().addTurn(DS.toJSON())
        JsonService.getIstance().setBase(self._id, self._type, self.root.toJSON())
