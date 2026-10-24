import random

import pyxel

from common import SE_CLEAR, SE_POINT, Game, se

CELL = 8
GW, GH = 20, 14
TOP = 8
DIRS = {
    pyxel.KEY_UP: (0, -1),
    pyxel.KEY_DOWN: (0, 1),
    pyxel.KEY_LEFT: (-1, 0),
    pyxel.KEY_RIGHT: (1, 0),
}


class Snake(Game):
    title = "SNAKE"
    controls = "ARROWS: turn"

    def reset(self):
        super().reset()
        self.body = [(10, 7), (9, 7), (8, 7)]
        self.dir = (1, 0)
        self.queue = []
        self.timer = 0
        self.place_food()

    def place_food(self):
        free = [(x, y) for x in range(GW) for y in range(GH) if (x, y) not in self.body]
        self.food = random.choice(free)

    def update(self):
        for key, d in DIRS.items():
            if pyxel.btnp(key) and len(self.queue) < 2:
                last = self.queue[-1] if self.queue else self.dir
                if d != last and d != (-last[0], -last[1]):
                    self.queue.append(d)

        self.timer += 1
        if self.timer < max(4, 10 - self.score // 4):
            return
        self.timer = 0
        if self.queue:
            self.dir = self.queue.pop(0)

        hx, hy = self.body[0]
        head = (hx + self.dir[0], hy + self.dir[1])
        if not (0 <= head[0] < GW and 0 <= head[1] < GH) or head in self.body[:-1]:
            self.finish()
            return

        self.body.insert(0, head)
        if head == self.food:
            self.score += 1
            se(SE_POINT)
            if len(self.body) == GW * GH:
                self.finish("PERFECT!", SE_CLEAR)
            else:
                self.place_food()
        else:
            self.body.pop()

    def draw(self):
        pyxel.cls(1)
        pyxel.rect(0, TOP, GW * CELL, GH * CELL, 3)
        fx, fy = self.food
        pyxel.circ(fx * CELL + 3, TOP + fy * CELL + 3, 3, 8)
        pyxel.pset(fx * CELL + 4, TOP + fy * CELL + 1, 7)
        for i, (x, y) in enumerate(self.body):
            col = 10 if i == 0 else 11
            pyxel.rect(x * CELL, TOP + y * CELL, CELL - 1, CELL - 1, col)
        hx, hy = self.body[0]
        pyxel.pset(hx * CELL + 2, TOP + hy * CELL + 2, 0)
        pyxel.pset(hx * CELL + 4, TOP + hy * CELL + 2, 0)
        pyxel.text(2, 1, f"SCORE {self.score}", 7)
