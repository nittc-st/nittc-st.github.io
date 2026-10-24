import random

import pyxel

from common import SE_BLIP, SE_CLEAR, SE_CRASH, SE_POINT, W, Game, se

TIME = 30 * 60
# テンキーの並びに合わせて 7 8 9 / 4 5 6 / 1 2 3 を対応させる
KEYS = [pyxel.KEY_7, pyxel.KEY_8, pyxel.KEY_9, pyxel.KEY_4, pyxel.KEY_5, pyxel.KEY_6,
        pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3]


def hole_pos(i):
    return 40 + i % 3 * 40, 42 + i // 3 * 28


class Whack(Game):
    title = "WHACK-A-MOLE"
    controls = "CLICK or 1-9: hit  avoid bombs!"

    def reset(self):
        super().reset()
        self.time = TIME
        self.holes = [None] * 9  # [残り時間, 種類, 叩かれた後の表示時間]
        self.hammer = 0

    def update(self):
        self.time -= 1
        if self.time <= 0:
            self.finish("TIME UP!", SE_CLEAR)
            return

        elapsed = 1 - self.time / TIME
        if random.random() < 0.03 + elapsed * 0.05:
            empty = [i for i, h in enumerate(self.holes) if h is None]
            if empty:
                kind = "bomb" if random.random() < 0.18 else "mole"
                self.holes[random.choice(empty)] = [int(70 - elapsed * 35), kind, 0]

        for i, h in enumerate(self.holes):
            if h is None:
                continue
            if h[2]:
                h[2] -= 1
                if h[2] == 0:
                    self.holes[i] = None
            else:
                h[0] -= 1
                if h[0] <= 0:
                    self.holes[i] = None

        hit = None
        for i, key in enumerate(KEYS):
            if pyxel.btnp(key):
                hit = i
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.hammer = 6
            for i in range(9):
                x, y = hole_pos(i)
                if abs(pyxel.mouse_x - x) < 16 and abs(pyxel.mouse_y - y + 4) < 12:
                    hit = i
        self.hammer = max(0, self.hammer - 1)

        if hit is not None:
            h = self.holes[hit]
            if h is None or h[2]:
                se(SE_BLIP)
            elif h[1] == "mole":
                self.score += 1
                h[2] = 12
                se(SE_POINT)
            else:
                self.score = max(0, self.score - 3)
                h[2] = 20
                se(SE_CRASH)

    def draw(self):
        pyxel.cls(11)
        pyxel.rect(0, 0, W, 10, 3)
        for i in range(9):
            x, y = hole_pos(i)
            pyxel.elli(x - 14, y - 2, 28, 10, 4)
            h = self.holes[i]
            if h is not None:
                if h[1] == "mole":
                    col = 8 if h[2] else 4
                    pyxel.rect(x - 8, y - 12, 16, 14, col)
                    pyxel.circ(x, y - 12, 8, col)
                    pyxel.pset(x - 3, y - 13, 0)
                    pyxel.pset(x + 3, y - 13, 0)
                    pyxel.rect(x - 2, y - 10, 4, 3, 15)
                    pyxel.pset(x, y - 10, 0)
                else:
                    pyxel.circ(x, y - 8, 7, 9 if h[2] and h[2] % 4 < 2 else 0)
                    pyxel.line(x + 4, y - 15, x + 7, y - 18, 13)
                    pyxel.pset(x + 7, y - 19, 10)
            pyxel.elli(x - 14, y + 2, 28, 6, 3)
            pyxel.text(x + 12, y + 5, "789456123"[i], 3)
        pyxel.text(2, 2, f"SCORE {self.score}", 7)
        sec = (self.time + 59) // 60
        pyxel.text(W - 30, 2, f"TIME {sec:2}", 10 if sec > 5 else 8)
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        tilt = 4 if self.hammer else 0
        pyxel.line(mx, my, mx + 8, my + 8 - tilt, 4)
        pyxel.rect(mx - 3 + tilt, my - 3, 7, 5, 13)
