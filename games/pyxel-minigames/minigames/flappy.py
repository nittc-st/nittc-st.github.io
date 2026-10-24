import random

import pyxel

from common import H, SE_BLIP, SE_POINT, W, Game, overlap, se, text_center

GROUND = 108
PIPE_W = 14
GAP = 38
BIRD_X = 40


class Flappy(Game):
    title = "FLAPPY"
    controls = "SPACE/UP: flap"

    def reset(self):
        super().reset()
        self.y = 50.0
        self.vy = 0.0
        self.started = False
        self.pipes = []
        self.timer = 0
        self.scroll = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_UP):
            self.started = True
            self.vy = -2.4
            se(SE_BLIP)
        if not self.started:
            self.y = 50 + pyxel.sin(pyxel.frame_count * 6) * 3
            return

        self.vy = min(self.vy + 0.15, 3.5)
        self.y += self.vy
        self.scroll += 1

        self.timer -= 1
        if self.timer <= 0:
            self.timer = 80
            self.pipes.append([W, random.randint(16, GROUND - GAP - 10), False])

        for p in self.pipes:
            p[0] -= 1
            if not p[2] and p[0] + PIPE_W < BIRD_X:
                p[2] = True
                self.score += 1
                se(SE_POINT)
            if overlap(BIRD_X, self.y, 8, 6, p[0], 0, PIPE_W, p[1]) or overlap(
                BIRD_X, self.y, 8, 6, p[0], p[1] + GAP, PIPE_W, H
            ):
                self.finish()
        self.pipes = [p for p in self.pipes if p[0] > -PIPE_W]

        if self.y > GROUND - 6 or self.y < -10:
            self.finish()

    def draw(self):
        pyxel.cls(12)
        for i in range(4):
            cx = (i * 50 - self.scroll // 3) % (W + 40) - 20
            pyxel.circ(cx, 30 + i % 2 * 12, 8, 7)
            pyxel.circ(cx + 9, 32 + i % 2 * 12, 6, 7)
        for x, top, _ in self.pipes:
            pyxel.rect(x, 0, PIPE_W, top, 11)
            pyxel.rect(x - 1, top - 5, PIPE_W + 2, 5, 3)
            pyxel.rect(x, top + GAP, PIPE_W, GROUND - top - GAP, 11)
            pyxel.rect(x - 1, top + GAP, PIPE_W + 2, 5, 3)
        pyxel.rect(0, GROUND, W, H - GROUND, 15)
        for x in range(-(self.scroll % 8), W, 8):
            pyxel.line(x, GROUND, x + 4, GROUND + 4, 9)
        pyxel.rect(0, GROUND, W, 2, 11)

        y = int(self.y)
        pyxel.rect(BIRD_X, y, 8, 6, 10)
        pyxel.rect(BIRD_X + 1, y + 3 - (pyxel.frame_count // 4 % 2), 4, 2, 9)
        pyxel.pset(BIRD_X + 6, y + 1, 0)
        pyxel.rect(BIRD_X + 8, y + 3, 2, 2, 9)

        pyxel.text(W // 2 - 4, 6, str(self.score), 7)
        if not self.started:
            text_center(80, "PRESS SPACE", 1)
