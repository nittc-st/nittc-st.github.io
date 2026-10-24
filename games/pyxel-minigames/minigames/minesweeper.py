import random

import pyxel

from common import SE_BLIP, SE_CLEAR, SE_POINT, W, Game, se

CELL = 8
GW, GH = 20, 13
TOP = 16
MINES = 30
NUM_COLORS = [0, 12, 11, 8, 2, 4, 14, 0, 13]


class Minesweeper(Game):
    title = "MINESWEEPER"
    controls = "L-CLICK/Z: open  R-CLICK/X: flag"

    def reset(self):
        super().reset()
        self.mines = None  # 最初に開いたマスが地雷にならないよう、初手で配置する
        self.opened = set()
        self.flags = set()
        self.cursor = (GW // 2, GH // 2)
        self.frames = 0
        self.exploded = None

    def neighbors(self, x, y):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (dx or dy) and 0 <= nx < GW and 0 <= ny < GH:
                    yield nx, ny

    def count(self, x, y):
        return sum((n in self.mines) for n in self.neighbors(x, y))

    def place_mines(self, safe):
        keep_out = {safe, *self.neighbors(*safe)}
        cells = [(x, y) for y in range(GH) for x in range(GW) if (x, y) not in keep_out]
        self.mines = set(random.sample(cells, MINES))

    def open_cell(self, pos):
        if self.mines is None:
            self.place_mines(pos)
        if pos in self.flags or pos in self.opened:
            return
        if pos in self.mines:
            self.exploded = pos
            self.finish("BOOM!")
            return
        # 周りに地雷がないマスは連鎖的に開く
        stack = [pos]
        while stack:
            p = stack.pop()
            if p in self.opened or p in self.flags:
                continue
            self.opened.add(p)
            if self.count(*p) == 0:
                stack.extend(n for n in self.neighbors(*p) if n not in self.opened)
        se(SE_POINT)
        if len(self.opened) == GW * GH - MINES:
            self.score = max(1, 999 - self.frames // 60)
            self.flags = set(self.mines)
            self.finish("CLEAR!", SE_CLEAR)

    def toggle_flag(self, pos):
        if pos in self.opened:
            return
        self.flags ^= {pos}
        se(SE_BLIP)

    def update(self):
        if self.mines is not None:
            self.frames += 1
        x, y = self.cursor
        if pyxel.btnp(pyxel.KEY_LEFT, hold=12, repeat=3):
            x = max(0, x - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT, hold=12, repeat=3):
            x = min(GW - 1, x + 1)
        if pyxel.btnp(pyxel.KEY_UP, hold=12, repeat=3):
            y = max(0, y - 1)
        if pyxel.btnp(pyxel.KEY_DOWN, hold=12, repeat=3):
            y = min(GH - 1, y + 1)
        self.cursor = (x, y)

        mx, my = pyxel.mouse_x // CELL, (pyxel.mouse_y - TOP) // CELL
        on_board = 0 <= mx < GW and 0 <= my < GH and pyxel.mouse_y >= TOP
        if on_board and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.cursor = (mx, my)
            self.open_cell(self.cursor)
        elif on_board and pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self.cursor = (mx, my)
            self.toggle_flag(self.cursor)
        elif pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE):
            self.open_cell(self.cursor)
        elif pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.KEY_F):
            self.toggle_flag(self.cursor)

    def draw(self):
        pyxel.cls(1)
        pyxel.text(2, 5, f"MINES {MINES - len(self.flags):2}", 8)
        pyxel.text(W - 44, 5, f"TIME {self.frames // 60:3}", 7)
        for y in range(GH):
            for x in range(GW):
                px, py = x * CELL, TOP + y * CELL
                pos = (x, y)
                if pos in self.opened:
                    pyxel.rect(px, py, CELL, CELL, 13)
                    n = self.count(x, y)
                    if n:
                        pyxel.text(px + 2, py + 1, str(n), NUM_COLORS[n])
                elif self.over and self.mines and pos in self.mines and pos not in self.flags:
                    pyxel.rect(px, py, CELL, CELL, 8 if pos == self.exploded else 13)
                    pyxel.circ(px + 3, py + 4, 2, 0)
                else:
                    pyxel.rect(px, py, CELL, CELL, 6)
                    pyxel.line(px, py, px + CELL - 1, py, 7)
                    pyxel.line(px, py, px, py + CELL - 1, 7)
                    if pos in self.flags:
                        pyxel.line(px + 2, py + 1, px + 2, py + 6, 0)
                        pyxel.tri(px + 3, py + 1, px + 6, py + 2, px + 3, py + 4, 8)
                pyxel.rectb(px, py, CELL, CELL, 5)
        cx, cy = self.cursor
        pyxel.rectb(cx * CELL, TOP + cy * CELL, CELL, CELL, 10)
