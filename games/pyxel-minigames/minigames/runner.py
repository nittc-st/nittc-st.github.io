import random

import pyxel

from common import SE_BLIP, SE_POINT, W, Game, overlap, se

GROUND = 96
PX = 20


class Runner(Game):
    title = "RUNNER"
    controls = "SPACE/UP: jump  DOWN: duck"

    def reset(self):
        super().reset()
        self.y = 0.0  # 地面からの高さ
        self.vy = 0.0
        self.speed = 2.0
        self.dist = 0
        self.obstacles = []
        self.next_spawn = 60
        self.ducking = False

    def update(self):
        on_ground = self.y == 0
        self.ducking = on_ground and pyxel.btn(pyxel.KEY_DOWN)
        if on_ground and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_UP)):
            self.vy = 3.6
            se(SE_BLIP)
        # ボタンを離すと早く落ちるので、ジャンプの高さを調整できる
        held = pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP)
        self.vy -= 0.18 if held and self.vy > 0 else 0.35
        self.y = max(0.0, self.y + self.vy)
        if self.y == 0:
            self.vy = 0

        self.speed = min(5.0, self.speed + 0.0012)
        self.dist += self.speed
        new_score = int(self.dist / 10)
        if new_score // 100 > self.score // 100:
            se(SE_POINT)
        self.score = new_score

        self.next_spawn -= self.speed
        if self.next_spawn <= 0:
            self.next_spawn = random.randint(70, 150) + self.speed * 10
            if self.score > 150 and random.random() < 0.3:
                self.obstacles.append([W, GROUND - random.choice((13, 24)), 10, 5, "bird"])
            else:
                h = random.choice((10, 14, 18))
                self.obstacles.append([W, GROUND - h, random.choice((6, 6, 12)), h, "cactus"])

        for o in self.obstacles:
            o[0] -= self.speed
        self.obstacles = [o for o in self.obstacles if o[0] > -20]

        h = 7 if self.ducking else 12
        top = GROUND - self.y - h
        for x, y, w, oh, _ in self.obstacles:
            if overlap(PX + 1, top, 8, h, x, y, w, oh):
                self.finish()

    def draw(self):
        pyxel.cls(7)
        offset = int(self.dist) % 40
        for i in range(6):
            x = i * 40 - offset
            pyxel.pset(x, GROUND + 6, 13)
            pyxel.pset(x + 17, GROUND + 10, 13)
        pyxel.line(0, GROUND, W, GROUND, 0)

        for x, y, w, h, kind in self.obstacles:
            if kind == "cactus":
                pyxel.rect(x, y, w, h, 3)
                pyxel.rect(x - 2, y + 4, 2, 4, 3)
            else:
                wing = 3 if pyxel.frame_count // 8 % 2 else -2
                pyxel.rect(x, y, w, 4, 4)
                pyxel.line(x + 3, y + 1, x + 6, y + wing, 4)
                pyxel.pset(x + 1, y + 1, 7)

        ducking = self.ducking
        h = 7 if ducking else 12
        top = int(GROUND - self.y - h)
        w = 12 if ducking else 9
        pyxel.rect(PX, top, w, h - 3, 13)
        pyxel.rect(PX + w - 4, top, 4, 4, 13)
        pyxel.pset(PX + w - 2, top + 1, 7)
        leg = pyxel.frame_count // 4 % 2 if self.y == 0 else 0
        pyxel.rect(PX + 1 + leg * 3, top + h - 3, 2, 3, 13)
        pyxel.rect(PX + 5 - leg * 3, top + h - 3, 2, 3, 13)

        pyxel.text(W - 40, 4, f"{self.score:05}", 0)
