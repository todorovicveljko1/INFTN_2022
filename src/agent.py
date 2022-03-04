from collections import deque
from src.utils.mapData import MapData
from src.utils.jsonService import JsonService
from src.utils.debugService import DebugService
from src.map import SquareMap
from src.decision_logic.main import DecisionLogic
from send_DTO import Action, InputAction
from src.map import Pos
import intopt
import numpy as np

GAME_LOOP = ["BUY", "PLANT", "WATER", "HARVEST"]

WATER_ID = 0
COST_TABLE = [3600, 1000, 500, 500]
WATER_TABLE = [1, 5, 2, 2]
HARVEST_TABLE = [8000, 5000, 2500, 2000]
LIGE_TABLE = [3, 4, 4, 5]
WATER_COST_TABLE = []
RETURN_TABLE = []
for i in range(4):
    WATER_COST_TABLE.append(COST_TABLE[i]+200*WATER_TABLE[i])
    RETURN_TABLE.append(HARVEST_TABLE[i] - WATER_COST_TABLE[i])


def plant_id_to_index(id):
    return id + 3


def index_to_plant_id(id):
    return 6 - id

# TODO: Max tiles flood fill count


def optimize_buy(tiles, gold, max_tiles):
    return intopt.intlinprog(np.array([4200, 3000, 1600, 900, 0]),
                             A_ub=np.matrix([
                                 [1, 1, 1, 1, -1],
                                 [3800, 2000, 900, 900, 5000],
                                 [0, 0, 0, 0, 1]]),
                             b_ub=np.array([tiles, gold, max_tiles]),
                             options={'branch_rule': 'max fun'})


def optimize_buy_fert(tiles, gold, max_tiles):
    return intopt.intlinprog(np.array([12200, 8000, 4100, 2900, 0]),
                             A_ub=np.matrix([
                                 [1, 1, 1, 1, -1],
                                 [3800, 2000, 900, 900, 5000],
                                 [0, 0, 0, 0, 1]]),
                             b_ub=np.array([tiles, gold, max_tiles]),
                             options={'branch_rule': 'max fun'})


def card_list_to_dict(cards):
    d = {}
    for i in range(7):
        d[i] = 0
    for c in cards:
        d[c.cardId] = c.owned
    return d


class Agent:
    def __init__(self, map, source, enemy, debug=False) -> None:
        self.debug = debug
        # init map
        self.map_state = SquareMap(map, source.tiles, enemy.tiles)
        # init players
        self.me = source
        self.opponent = enemy
        # rest data
        self.turn = 0
        self.loop = 0
        self.my_card_dict = {}
        self.my_tiles = set()
        self.opponent_tiles = set()
        for t in source.tiles:
            self.my_tiles.add(Pos(t.x, t.y))
        for t in enemy.tiles:
            self.opponent_tiles.add(Pos(t.x, t.y))
        self.analyze = self.map_state.analyze()
        self.fert = False
        self.crocc_optimal = False  # Water - 2
        self.lg = False
        self.lg_q = deque()
        self.lg_fert = 0
        self.one_more = False
        #print(np.round(self.analyze, 2))
        # Create logic
        self.DL = self.init_decision_logic()
        # Set debug data if debugging

    def next_action(self):
        self.turn += 1
        return self.DL.handle()[1]

    def update_state(self, map, source, enemy):
        self.map_state.update(map, source.tiles, enemy.tiles)
        self.me = source
        self.opponent = enemy
        self.opponent_tiles.clear()
        self.my_tiles.clear()
        for t in source.tiles:
            self.my_tiles.add(Pos(t.x, t.y))
        for t in enemy.tiles:
            self.opponent_tiles.add(Pos(t.x, t.y))
        self.my_card_dict = card_list_to_dict(self.me.cards)

    def init_decision_logic(self):
        DL = DecisionLogic()
        DL.root = DL._SEQ([
            DL._IF(self.is_late_game,
                   DL._SEQ([
                       DL._IF(self.is_buying, DL._ACT(
                           self.buy_lg), DL._ACT(self.null)),
                       DL._IF(self.is_planting, DL._ACT(
                           self.plant_lg), DL._ACT(self.null)),
                       DL._IF(self.is_water, DL._ACT(
                           self.water_lg), DL._ACT(self.null)),
                       DL._IF(self.is_harvest, DL._ACT(
                           self.harvest_lg), DL._ACT(self.null)),
                   ]),
                   DL._SEQ([
                       DL._IF(self.is_buying, DL._ACT(
                           self.buy), DL._ACT(self.null)),
                       DL._IF(self.is_planting, DL._ACT(
                           self.plant), DL._ACT(self.null)),
                       DL._IF(self.is_water, DL._ACT(
                           self.water), DL._ACT(self.null)),
                       DL._IF(self.is_harvest, DL._ACT(
                           self.harvest), DL._ACT(self.null)),
                   ])
                   ),

            DL._ACT(self.default)
        ])
        return DL

    # LOGIC
    def is_late_game(self):
        return len(self.map_state.get_tiles_that_are_acc(
            self.my_tiles, self.opponent_tiles)) == 0 and ((GAME_LOOP[self.loop % 4] == "BUY" and self.one_more) or self.lg)

    def is_buying(self):
        return GAME_LOOP[self.loop % 4] == "BUY"

    def is_planting(self):
        return GAME_LOOP[self.loop % 4] == "PLANT"

    def is_water(self):
        return GAME_LOOP[self.loop % 4] == "WATER"

    def is_harvest(self):
        return GAME_LOOP[self.loop % 4] == "HARVEST"
    # ACTIONS

    def null(self):
        return None

    def default(self):
        return {}

    def buy(self):
        opt, ciklus_l = self.get_optimized_buy()
        self.crocc_optimal = False
        if self.one_more or len(self.map_state.get_tiles_that_are_acc(
                self.my_tiles, self.opponent_tiles)) == 0:
            self.one_more = True
        # USLOVI za kisu
        if (ciklus_l == 4 and (self.turn % 10 == 7 or self.turn % 10 == 8)) or (ciklus_l == 6 and (self.turn % 10 == 5 or self.turn % 10 == 6)):
            action = InputAction("C", [])
            buy_list = []
            g = self.me.gold
            if self.fert:
                buy_list.append(Action(cardid=2, amount=2))
                g -= 6000
            n = g // 1600
            n = min(len(self.my_tiles), n)
            buy_list.append(Action(cardid=0, amount=n*3))
            buy_list.append(Action(cardid=5, amount=n))
            self.crocc_optimal = True
            action.Properties = buy_list
            self.loop += 1
            return action
        # ENDUSLOVI
        if opt.success:
            bought = self.buy_tiles(int(opt.x[4]))
            if opt.x[4] > 0 and len(bought) > 0:  # buy tiles
                action = InputAction("L", [])
                action_i = []
                # print(bought)
                for b in bought:
                    action_i.append(Action(x=b.x, y=b.y))
                action.Properties = action_i
                return action
            else:
                action = InputAction("C", [])
                buy_list = []
                if self.fert:
                    buy_list.append(Action(cardid=2, amount=2))
                for plant_idx in range(4):
                    if opt.x[plant_idx] > 0:
                        buy_list.append(
                            Action(cardid=0, amount=opt.x[plant_idx]*WATER_TABLE[plant_idx]))
                        buy_list.append(Action(cardid=index_to_plant_id(
                            plant_idx), amount=opt.x[plant_idx]))
                action.Properties = buy_list
                self.loop += 1
                return action
        else:
            self.loop += 1
            return None

    def plant(self):
        action = InputAction("P", [])
        plant_list = []
        filled = 0
        me_plant_tiles = self.me.tiles[::-1]
        # print(self.my_card_dict)
        if self.my_card_dict[2] > 0:
            self.my_card_dict[2] -= 1
            return InputAction("F", [])
        for i in range(4):
            plant_id = index_to_plant_id(i)
            fill_count = 0
            if self.my_card_dict[plant_id] > 0:
                for t in me_plant_tiles[filled:]:
                    if self.my_card_dict[plant_id] == 0:
                        break
                    plant_list.append(
                        Action(x=t.x, y=t.y, cardid=index_to_plant_id(i)))
                    self.my_card_dict[plant_id] -= 1
                    fill_count += 1
            filled += fill_count
        self.loop += 1
        action.Properties = plant_list
        return action

    def water(self):
        action = InputAction("W", [])
        water_list = []
        for t in self.me.tiles:
            if t.bIsPlanted:
                if self.crocc_optimal:
                    water_list.append(
                        Action(x=t.x, y=t.y, amount=3))
                else:
                    water_list.append(
                        Action(x=t.x, y=t.y, amount=t.plantDTO.waterNeeded))
        self.loop += 1
        action.Properties = water_list
        return action

    def harvest(self):
        action = InputAction("H", [])
        harvest_list = []
        for t in self.me.tiles:
            if t.bIsPlanted and t.plantDTO.waterNeeded == 0:
                harvest_list.append(Action(x=t.x, y=t.y))
        self.loop += 1
        action.Properties = harvest_list
        return action

    def buy_tiles(self, numb):
        cant_buy = self.my_tiles.union(self.opponent_tiles)
        my_tiles = set(self.my_tiles)
        bought = []
        # Get all nei that can be bought
        # find best and buy it
        # repeat
        for i in range(numb):
            opts = self.map_state.get_to_buy_tile(my_tiles, cant_buy)
            if len(opts) > 0:
                tb = max(opts, key=lambda k: self.analyze[k.x, k.y])
                bought.append(tb)
                my_tiles.add(tb)
                cant_buy.add(tb)
            else:
                break
        return bought

    def get_optimized_buy(self):
        tiles_len = len(self.map_state.get_tiles_that_are_acc(
            self.my_tiles, self.opponent_tiles))
        opt = optimize_buy(
            len(self.me.tiles),
            self.me.gold,
            tiles_len
        )
        g = self.me.gold - 6000
        self.fert = False
        ciklus_l = (4+min(1, opt.x[4]))
        if g > 0 and self.turn > 35:
            opt_fert = optimize_buy_fert(
                len(self.me.tiles),
                g,
                tiles_len
            )
            if opt_fert.fun/(6+min(1, opt_fert.x[4])) > opt.fun/(4+min(1, opt.x[4])):
                opt = opt_fert
                self.fert = True
            #print(opt_fert.fun/(6+min(1, opt_fert.x[4])))
            ciklus_l = 6 + min(1, opt_fert.x[4])
        #print(opt.fun/(4 + min(1, opt.x[4])))
        return opt, ciklus_l

    # LATE GAME
    def buy_lg(self):
        self.lg = True
        if len(self.lg_q) > 0:
            self.loop += 1
            return None
        gold = self.me.gold
        _turn = self.turn + 1
        my_tiles_len = len(self.my_tiles)
        buy_list = []
        # SYNC
        off = -1
        for i in range(3):
            _turn = self.turn + 1 + i
            for j in range(3):
                if _turn % 10 == 6 or _turn % 10 == 7:
                    off = i
                _turn += 5
            if off != i:
                m_c = self.get_enemy_number_of_mole()
                if m_c >= i+5 and self.turn <= 70:
                    buy_list.append(Action(cardid=1, amount=i+5))

                    gold -= (10000*(i+5))
                    off = i+5
                else:

                    gold -= (10000*i)
                    buy_list.append(Action(cardid=1, amount=i))
                    off = i
                break
        # print("OFF")
        # print(self.turn)
        # print(off)
        _turn = self.turn + 1 + off
        my_tiles_len += off
        # END SYNC
        while True:
            if _turn % 10 == 6 or _turn % 10 == 7:  # C
                req = 6000+my_tiles_len*1600
                if req > gold:
                    break
                buy_list.append(Action(cardid=2, amount=2))
                buy_list.append(Action(cardid=0, amount=my_tiles_len*3))
                buy_list.append(Action(cardid=5, amount=my_tiles_len))
                self.lg_q.append("C")
                gold -= req

            else:  # T
                req = 6000+my_tiles_len*3800
                if req > gold:
                    break
                buy_list.append(Action(cardid=2, amount=2))
                buy_list.append(Action(cardid=0, amount=my_tiles_len))
                buy_list.append(Action(cardid=6, amount=my_tiles_len))
                self.lg_q.append("T")
                gold -= req
            _turn += 5
            if _turn > 150:
                break
        action = InputAction("C", [])
        action.Properties = buy_list
        self.loop += 1
        # print("DEBUGGGGGGG")
        # print(self.turn)
        # print(self.lg_q)
        return action

    def plant_lg(self):
        action = InputAction("P", [])
        plant_list = []
        what = self.lg_q.popleft()
        self.lg_q.appendleft(what)
        if self.my_card_dict[1] > 0:
            for t in self.opponent.tiles:
                if t.bIsSpecial:
                    return InputAction("M", [Action(x=t.x, y=t.y)])
            return InputAction("M", [Action(x=self.opponent.tiles[0].x, y=self.opponent.tiles[0].y)])
        if self.lg_fert < 2:
            self.lg_fert += 1
            return InputAction("F", [])
        if what == "C":
            for t in self.my_tiles:
                plant_list.append(Action(x=t.x, y=t.y, cardid=5))
        else:

            for t in self.my_tiles:
                plant_list.append(Action(x=t.x, y=t.y, cardid=6))
        self.loop += 1
        action.Properties = plant_list
        return action

    def water_lg(self):
        action = InputAction("W", [])
        water_list = []
        what = self.lg_q.popleft()
        self.lg_q.appendleft(what)
        if what == "C":
            for t in self.my_tiles:
                water_list.append(Action(x=t.x, y=t.y, amount=3))
        else:
            for t in self.my_tiles:
                water_list.append(Action(x=t.x, y=t.y, amount=1))
        self.loop += 1
        action.Properties = water_list
        return action

    def harvest_lg(self):
        action = InputAction("H", [])
        harvest_list = []
        what = self.lg_q.popleft()
        if what == "C":
            for t in self.my_tiles:
                harvest_list.append(Action(x=t.x, y=t.y))
        else:
            for t in self.my_tiles:
                harvest_list.append(Action(x=t.x, y=t.y))
        self.loop += 1
        self.lg_fert = 0
        action.Properties = harvest_list
        return action

    def get_enemy_number_of_mole(self):
        count = 0
        for t in self.opponent.tiles:
            if t.bIsSpecial:
                count += 1
        return count
