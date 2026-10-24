import random

import pyxel

from common import SE_BLIP, SE_CLEAR, SE_POINT, Game, se

N = 4
TILE, GAP = 24, 3
OX, OY = 46, 5
COLORS = {2: 7, 4: 15, 8: 9, 16: 8, 32: 14, 64: 2, 128: 10, 256: 11, 512: 3, 1024: 12, 2048: 6}
DIRS = {pyxel.KEY_LEFT: "L", pyxel.KEY_RIGHT: "R", pyxel.KEY_UP: "U", pyxel.KEY_DOWN: "D"}


def lines(d):
    """移動方向の先頭から並べたマス目の座標を列ごとに返す。"""
    for i in range(N):
        if d == "L":
            yield [(x, i) for x in range(N)]
        elif d == "R":
            yield [(x, i) for x in reversed(range(N))]
        elif d == "U":
            yield [(i, y) for y in range(N)]
        else:
            yield [(i, y) for y in reversed(range(N))]


def slide(values):
    tiles = [v for v in values if v]
    out, gained, i = [], 0, 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            out.append(tiles[i] * 2)
            gained += tiles[i] * 2
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    return out + [0] * (N - len(out)), gained


class G2048(Game):
    title = "2048"
    controls = "ARROWS: slide"

    def reset(self):
        super().reset()
        self.grid = [[0] * N for _ in range(N)]
        self.reached = False
        self.pop = None
        self.add_tile()
        self.add_tile()

    def add_tile(self):
        empty = [(x, y) for y in range(N) for x in range(N) if not self.grid[y][x]]
        x, y = random.choice(empty)
        self.grid[y][x] = 4 if random.random() < 0.1 else 2
        self.pop = (x, y, 6)

    def move(self, d):
        moved, gained = False, 0
        for cells in lines(d):
            values = [self.grid[y][x] for x, y in cells]
            new, g = slide(values)
            gained += g
            if new != values:
                moved = True
                for (x, y), v in zip(cells, new):
                    self.grid[y][x] = v
        return moved, gained

    def can_move(self):
        for y in range(N):
            for x in range(N):
                v = self.grid[y][x]
                if v == 0 or (x + 1 < N and self.grid[y][x + 1] == v) or (
                    y + 1 < N and self.grid[y + 1][x] == v
                ):
                    return True
        return False

    def update(self):
        if self.pop and self.pop[2] > 0:
            self.pop = (self.pop[0], self.pop[1], self.pop[2] - 1)
        for key, d in DIRS.items():
            if pyxel.btnp(key):
                moved, gained = self.move(d)
                if not moved:
                    continue
                self.score += gained
                se(SE_POINT if gained else SE_BLIP)
                self.add_tile()
                if not self.reached and any(2048 in row for row in self.grid):
                    self.reached = True
                    se(SE_CLEAR)
                if not self.can_move():
                    self.finish()
                break

    def draw(self):
        pyxel.cls(4)
        pyxel.text(4, 8, "SCORE", 15)
        pyxel.text(4, 16, str(self.score), 7)
        if self.reached:
            pyxel.text(4, 40, "2048!", 10 if pyxel.frame_count % 30 < 20 else 7)
        size = N * TILE + (N + 1) * GAP
        pyxel.rect(OX, OY, size, size, 13)
        for y in range(N):
            for x in range(N):
                v = self.grid[y][x]
                tx, ty = OX + GAP + x * (TILE + GAP), OY + GAP + y * (TILE + GAP)
                if not v:
                    pyxel.rect(tx, ty, TILE, TILE, 5)
                    continue
                shrink = self.pop[2] if self.pop and self.pop[:2] == (x, y) else 0
                pyxel.rect(tx + shrink, ty + shrink, TILE - shrink * 2, TILE - shrink * 2, COLORS.get(v, 1))
                s = str(v)
                col = 0 if COLORS.get(v) in (7, 15, 10, 11, 6) else 7
                pyxel.text(tx + (TILE - len(s) * 4) // 2 + 1, ty + 9, s, col)
