import math
import random

import pyxel

from common import H, SE_BLIP, SE_CLEAR, SE_CRASH, SE_POINT, W, Game, overlap, se, text_center

BW, BH = 14, 5
ROW_COLORS = [8, 9, 10, 11, 12]
PAD_W, PAD_Y = 24, 110
BALL = 3


class Breakout(Game):
    title = "BREAKOUT"
    controls = "LEFT/RIGHT: move  SPACE: launch"

    def reset(self):
        super().reset()
        self.lives = 3
        self.level = 1
        self.pad_x = (W - PAD_W) / 2
        self.build()

    def build(self):
        self.bricks = [
            [1 + c * 16, 14 + r * 7, ROW_COLORS[r]] for r in range(5) for c in range(10)
        ]
        self.speed = 1.4 + 0.2 * self.level
        self.hold_ball()

    def hold_ball(self):
        self.held = True
        self.vx = self.vy = 0.0
        self.bx = self.pad_x + PAD_W / 2 - 1
        self.by = PAD_Y - BALL - 1

    def launch(self):
        self.held = False
        angle = math.radians(random.uniform(-60, -120))
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

    def hit_brick(self):
        for b in self.bricks:
            if overlap(self.bx, self.by, BALL, BALL, b[0], b[1], BW, BH):
                self.bricks.remove(b)
                self.score += 10 * self.level
                self.speed = min(self.speed + 0.03, 3.5)
                se(SE_POINT)
                return True
        return False

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.pad_x -= 2.5
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.pad_x += 2.5
        self.pad_x = max(0, min(W - PAD_W, self.pad_x))

        if self.held:
            self.bx = self.pad_x + PAD_W / 2 - 1
            self.by = PAD_Y - BALL - 1
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_UP):
                self.launch()
            return

        # 軸ごとに移動と衝突判定を行うと、どちらの向きに跳ね返すかが決めやすい
        self.bx += self.vx
        if self.bx < 0 or self.bx > W - BALL:
            self.bx = max(0, min(W - BALL, self.bx))
            self.vx = -self.vx
            se(SE_BLIP)
        elif self.hit_brick():
            self.bx -= self.vx
            self.vx = -self.vx

        self.by += self.vy
        if self.by < 9:
            self.by = 9
            self.vy = -self.vy
            se(SE_BLIP)
        elif self.hit_brick():
            self.by -= self.vy
            self.vy = -self.vy

        if self.vy > 0 and overlap(self.bx, self.by, BALL, BALL, self.pad_x, PAD_Y, PAD_W, 3):
            # パドルのどこに当たったかで反射角を変える
            offset = (self.bx + BALL / 2 - (self.pad_x + PAD_W / 2)) / (PAD_W / 2)
            angle = math.radians(-90 + max(-1, min(1, offset)) * 60)
            self.vx = math.cos(angle) * self.speed
            self.vy = math.sin(angle) * self.speed
            self.by = PAD_Y - BALL
            se(SE_BLIP)

        if self.by > H:
            self.lives -= 1
            if self.lives == 0:
                self.finish()
            else:
                se(SE_CRASH)
                self.hold_ball()
        elif not self.bricks:
            se(SE_CLEAR)
            self.level += 1
            self.build()

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(0, 0, W, 8, 1)
        for x, y, col in self.bricks:
            pyxel.rect(x, y, BW, BH, col)
            pyxel.line(x, y + BH - 1, x + BW - 1, y + BH - 1, 5)
        pyxel.rect(self.pad_x, PAD_Y, PAD_W, 3, 6)
        pyxel.rect(self.pad_x + 2, PAD_Y, PAD_W - 4, 1, 7)
        pyxel.rect(self.bx, self.by, BALL, BALL, 7)
        pyxel.text(2, 1, f"SCORE {self.score}", 7)
        pyxel.text(70, 1, f"LV {self.level}", 10)
        for i in range(self.lives):
            pyxel.rect(W - 8 - i * 7, 2, 5, 3, 8)
        if self.held and not self.over:
            text_center(80, "PRESS SPACE", 13)
