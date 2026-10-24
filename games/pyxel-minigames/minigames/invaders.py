import random

import pyxel

from common import H, SE_CLEAR, SE_CRASH, SE_POINT, SE_SHOT, W, Game, overlap, se

COLS, ROWS = 8, 4
ALIEN_W, ALIEN_H = 8, 6
ROW_COLORS = [8, 14, 9, 11]
PLAYER_Y = 108


class Invaders(Game):
    title = "INVADERS"
    controls = "LEFT/RIGHT: move  SPACE: shoot"

    def reset(self):
        super().reset()
        self.lives = 3
        self.wave = 0
        self.px = W / 2 - 4
        self.next_wave()

    def next_wave(self):
        self.wave += 1
        self.aliens = [
            [12 + c * 14, 14 + r * 10 + min(self.wave - 1, 4) * 4, r]
            for r in range(ROWS)
            for c in range(COLS)
        ]
        self.dx = 2
        self.step_timer = 0
        self.shots = []
        self.bombs = []
        self.invincible = 60

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.px -= 1.5
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.px += 1.5
        self.px = max(0, min(W - 9, self.px))
        if pyxel.btnp(pyxel.KEY_SPACE) and len(self.shots) < 2:
            self.shots.append([self.px + 4, PLAYER_Y - 3])
            se(SE_SHOT)
        self.invincible = max(0, self.invincible - 1)

        # 残りが少ないほど速く動く
        self.step_timer += 1
        interval = max(3, len(self.aliens) * 2 // 3 + 6 - self.wave * 2)
        if self.step_timer >= interval:
            self.step_timer = 0
            xs = [a[0] for a in self.aliens]
            if (self.dx > 0 and max(xs) + ALIEN_W + self.dx > W - 2) or (
                self.dx < 0 and min(xs) + self.dx < 2
            ):
                self.dx = -self.dx
                for a in self.aliens:
                    a[1] += 4
            else:
                for a in self.aliens:
                    a[0] += self.dx

        if random.random() < 0.015 + self.wave * 0.005:
            shooter = random.choice(self.aliens)
            self.bombs.append([shooter[0] + 4, shooter[1] + ALIEN_H])

        for s in self.shots:
            s[1] -= 4
            for a in self.aliens:
                if overlap(s[0], s[1], 1, 4, a[0], a[1], ALIEN_W, ALIEN_H):
                    self.aliens.remove(a)
                    s[1] = -10
                    self.score += (ROWS - a[2]) * 10
                    se(SE_POINT)
                    break
        self.shots = [s for s in self.shots if s[1] > 0]

        for b in self.bombs:
            b[1] += 1.5
            if self.invincible == 0 and overlap(b[0], b[1], 1, 3, self.px, PLAYER_Y, 9, 5):
                b[1] = H
                self.hit()
        self.bombs = [b for b in self.bombs if b[1] < H]

        if self.over:
            return
        if not self.aliens:
            se(SE_CLEAR)
            self.next_wave()
        elif max(a[1] for a in self.aliens) + ALIEN_H >= PLAYER_Y:
            self.finish()

    def hit(self):
        self.lives -= 1
        if self.lives <= 0:
            self.finish()
        else:
            se(SE_CRASH)
            self.invincible = 90

    def draw(self):
        pyxel.cls(0)
        for i in range(20):
            pyxel.pset((i * 37) % W, (i * 23 + pyxel.frame_count // 8) % H, 5)
        frame = pyxel.frame_count // 20 % 2
        for x, y, r in self.aliens:
            col = ROW_COLORS[r]
            pyxel.rect(x + 1, y, 6, 4, col)
            pyxel.pset(x + 2, y + 1, 0)
            pyxel.pset(x + 5, y + 1, 0)
            if frame:
                pyxel.line(x, y + 4, x, y + 5, col)
                pyxel.line(x + 7, y + 4, x + 7, y + 5, col)
            else:
                pyxel.line(x + 2, y + 4, x + 1, y + 5, col)
                pyxel.line(x + 5, y + 4, x + 6, y + 5, col)
        for x, y in self.shots:
            pyxel.rect(x, y, 1, 4, 10)
        for x, y in self.bombs:
            pyxel.rect(x, y, 1, 3, 8 if pyxel.frame_count % 4 < 2 else 7)
        if self.invincible % 6 < 3:
            px = int(self.px)
            pyxel.rect(px, PLAYER_Y + 2, 9, 3, 11)
            pyxel.rect(px + 3, PLAYER_Y, 3, 2, 11)
            pyxel.pset(px + 4, PLAYER_Y - 1, 7)
        pyxel.line(0, PLAYER_Y + 6, W, PLAYER_Y + 6, 3)
        pyxel.text(2, 1, f"SCORE {self.score}", 7)
        pyxel.text(70, 1, f"WAVE {self.wave}", 12)
        for i in range(self.lives):
            pyxel.rect(W - 8 - i * 7, 2, 5, 3, 11)
