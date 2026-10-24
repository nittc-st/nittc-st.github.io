import random

import pyxel

from common import H, SE_BLIP, SE_CLEAR, SE_CRASH, SE_POINT, W, Game, overlap, se

PAD_H = 20
WIN_SCORE = 7


class Pong(Game):
    title = "PONG"
    controls = "UP/DOWN: move  first to 7 wins"

    def reset(self):
        super().reset()
        self.py = self.cy = (H - PAD_H) / 2
        self.cpu = 0
        self.serve(1)

    def serve(self, direction):
        self.bx, self.by = W / 2, H / 2
        self.vx = 1.3 * direction
        self.vy = random.uniform(-1, 1)
        self.wait = 40

    def update(self):
        if pyxel.btn(pyxel.KEY_UP):
            self.py -= 2
        if pyxel.btn(pyxel.KEY_DOWN):
            self.py += 2
        self.py = max(0, min(H - PAD_H, self.py))

        # CPU は速度制限付きでボールを追う
        target = self.by - PAD_H / 2 if self.vx > 0 else (H - PAD_H) / 2
        self.cy += max(-1.3, min(1.3, target - self.cy))
        self.cy = max(0, min(H - PAD_H, self.cy))

        if self.wait > 0:
            self.wait -= 1
            return

        self.bx += self.vx
        self.by += self.vy
        if self.by < 0 or self.by > H - 3:
            self.by = max(0, min(H - 3, self.by))
            self.vy = -self.vy
            se(SE_BLIP)

        for px, py, side in ((4, self.py, 1), (W - 7, self.cy, -1)):
            if self.vx * side < 0 and overlap(self.bx, self.by, 3, 3, px, py, 3, PAD_H):
                offset = (self.by + 1.5 - (py + PAD_H / 2)) / (PAD_H / 2)
                self.vx = -self.vx * 1.06
                self.vx = max(-3.5, min(3.5, self.vx))
                self.vy = offset * 1.8
                se(SE_BLIP)

        if self.bx < -4:
            self.cpu += 1
            se(SE_CRASH)
            self.serve(-1)
        elif self.bx > W + 1:
            self.score += 1
            se(SE_POINT)
            self.serve(1)

        if self.score == WIN_SCORE:
            self.finish("YOU WIN!", SE_CLEAR)
        elif self.cpu == WIN_SCORE:
            self.finish("YOU LOSE")

    def draw(self):
        pyxel.cls(5)
        for y in range(0, H, 8):
            pyxel.rect(W // 2 - 1, y, 2, 4, 1)
        pyxel.text(W // 2 - 20, 4, str(self.score), 10)
        pyxel.text(W // 2 + 17, 4, str(self.cpu), 8)
        pyxel.rect(4, self.py, 3, PAD_H, 10)
        pyxel.rect(W - 7, self.cy, 3, PAD_H, 8)
        if self.wait % 10 < 6:
            pyxel.rect(self.bx, self.by, 3, 3, 7)
