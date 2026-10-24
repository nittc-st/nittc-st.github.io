import random

import pyxel

from common import H, SE_POINT, W, Game, overlap, se

PLAYER_Y = 106


class Dodge(Game):
    title = "DODGE"
    controls = "LEFT/RIGHT: move  grab the coins"

    def reset(self):
        super().reset()
        self.px = W / 2 - 4
        self.blocks = []
        self.coins = []
        self.frames = 0

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.px -= 2
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.px += 2
        self.px = max(0, min(W - 8, self.px))

        self.frames += 1
        if self.frames % 60 == 0:
            self.score += 1
        level = self.frames / 600
        if random.random() < 0.05 + level * 0.03:
            size = random.randint(5, 12)
            self.blocks.append([random.uniform(0, W - size), -size, size, 0.8 + level * 0.4 + random.random()])
        if random.random() < 0.006:
            self.coins.append([random.uniform(4, W - 8), -6])

        for b in self.blocks:
            b[1] += b[3]
            if overlap(self.px + 1, PLAYER_Y + 1, 6, 7, b[0], b[1], b[2], b[2]):
                self.finish()
        for c in self.coins:
            c[1] += 1
            if overlap(self.px, PLAYER_Y, 8, 8, c[0], c[1], 5, 5):
                c[1] = H
                self.score += 5
                se(SE_POINT)
        self.blocks = [b for b in self.blocks if b[1] < H]
        self.coins = [c for c in self.coins if c[1] < H]

    def draw(self):
        pyxel.cls(1)
        pyxel.rect(0, PLAYER_Y + 8, W, H - PLAYER_Y - 8, 5)
        for x, y, s, _ in self.blocks:
            pyxel.rect(x, y, s, s, 8)
            pyxel.rectb(x, y, s, s, 2)
        for x, y in self.coins:
            pyxel.circ(x + 2, y + 2, 2, 10)
            pyxel.pset(x + 2, y + 1, 7)
        px = int(self.px)
        pyxel.rect(px + 1, PLAYER_Y, 6, 8, 12)
        pyxel.rect(px + 2, PLAYER_Y + 2, 4, 2, 7)
        pyxel.pset(px + 3, PLAYER_Y + 2, 0)
        pyxel.text(2, 2, f"SCORE {self.score}", 7)
