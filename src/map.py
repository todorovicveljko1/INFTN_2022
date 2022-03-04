import queue
from typing import Any, TypeVar
import numpy as np
from collections import deque
Tile = TypeVar("Tile", bound="Tile")
Pos = TypeVar("Pos", bound="Pos")


class Pos:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def distance(self, b: Pos):
        return abs(self.x - b.x) + abs(self.y - b.y)

    def add(self, b: Pos):
        return Pos(self.x+b.x, self.y+b.y)

    def sub(self, b: Pos):
        return Pos(self.x-b.x, self.y-b.y)

    def __str__(self) -> str:
        return f"{self.x}_{self.y}"

    def __repr__(self) -> str:

        return f"{self.x}_{self.y}"

    def __hash__(self) -> int:
        return self.x + 512*self.y

    def __eq__(self, o) -> bool:
        return self.x == o.x and self.y == o.y


OWNER_TILE = ["NONE", "ME", "ENEMY"]


class Tile:
    def __init__(self, pos: Pos, tile: Any) -> None:
        self.pos = pos
        self.data = tile
        self.owner = 0  # 0 1 2

    # DEBUG

    def to_json(self):
        return {
            "pos": str(self.pos),
            "tile_type": self.get_type(),
            "data": self.data.to_json()
        }

    def get_type(self):
        return f"{OWNER_TILE[self.owner]}_{'SPC' if self.data.bIsSpecial else 'NO'}"

    def __repr__(self) -> str:
        return f"{self.pos} - {self.data}"


class SquareMap:
    def __init__(self, map: list[Any], me_tiles, enemy_tiles) -> None:
        self.height: int = 8
        self.width: int = 8
        self.tiles: list[list[Tile]] = [[Tile(Pos(i, j), None)
                                         for i in range(self.width)] for j in range(self.height)]
        for t in map:
            self.tiles[t.y][t.x].data = t
        for t in me_tiles:
            self.tiles[t.y][t.x].owner = 1
        for t in enemy_tiles:
            self.tiles[t.y][t.x].owner = 2
        self._map = map
        self._updated: set[Pos] = set()

    def update(self, map: list[Any], me_tiles, enemy_tiles) -> None:

        for t in map:
            if self.tiles[t.y][t.x].data != t:
                # Update
                temp = Pos(t.x, t.y)
                self.tiles[t.y][t.x].data = t
                self._updated.add(temp)

        for t in me_tiles:
            self.tiles[t.y][t.x].owner = 1
        for t in enemy_tiles:
            self.tiles[t.y][t.x].owner = 2

    def get_tile(self, pos: Pos) -> Tile:
        return self.tiles[pos.y][pos.x]

    def get_neighbors(self, pos: Pos) -> list[Tile]:
        neighbors: list[Tile] = []
        if pos.y > 0:
            neighbors.append(self.tiles[pos.y - 1][pos.x])
        if pos.x < self.width - 1:
            neighbors.append(self.tiles[pos.y][pos.x + 1])
            if pos.y > 0:
                neighbors.append(self.tiles[pos.y - 1][pos.x + 1])
            if pos.y < self.height - 1:
                neighbors.append(self.tiles[pos.y + 1][pos.x + 1])
        if pos.y < self.height - 1:
            neighbors.append(self.tiles[pos.y + 1][pos.x])
        if pos.x > 0:
            neighbors.append(self.tiles[pos.y][pos.x - 1])
            if pos.y > 0:
                neighbors.append(self.tiles[pos.y - 1][pos.x - 1])
            if pos.y < self.height - 1:
                neighbors.append(self.tiles[pos.y + 1][pos.x - 1])
        return neighbors

    # DEBUG
    def to_map_data(self, whole: bool = False):
        data: list[dict[Any]] = []
        if whole:
            for j in range(self.height):
                for i in range(self.width):
                    data.append(self.tiles[j][i].to_json())
        else:
            for pos in self._updated:
                data.append(self.tiles[pos.x][pos.y].to_json())
        return data

    def analyze(self):
        map = np.zeros(shape=(8, 8))
        for j in range(self.height):
            for i in range(self.width):
                if self.tiles[i][j].data.bIsSpecial:
                    map += self._sub_analyze(self.tiles[i][j].pos)
        return map

    def _sub_analyze(self, pos):
        q = deque()
        map = np.zeros(shape=(8, 8))
        q.append(pos)
        map[pos.x, pos.y] = 1
        while len(q) > 0:
            curr = q.popleft()
            for n in self.get_neighbors(curr):
                if map[n.pos.x, n.pos.y] == 0:
                    q.append(n.pos)
                    map[n.pos.x, n.pos.y] = map[curr.x, curr.y]/2
        return map

    def get_to_buy_tile(self, my_tiles_pos: set[Pos], cant_buy_pos: set[Pos]):
        a_set = set()
        for t in my_tiles_pos:
            for n in self.get_neighbors(t):
                a_set.add(n.pos)

        a_set.difference_update(cant_buy_pos)
        return a_set

    def get_tiles_that_are_acc(self, my_tile_pos: set[Pos], enemy_tile_pos: set[Pos]):
        tiles = set()
        passed = set(my_tile_pos.union(enemy_tile_pos))
        q = deque(my_tile_pos)
        while len(q) > 0:
            curr = q.popleft()
            for n in self.get_neighbors(curr):
                if n.pos not in passed:
                    q.append(n.pos)
                    passed.add(n.pos)
                    tiles.add(n.pos)
        return tiles
