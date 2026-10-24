import random

import pyxel

from common import SE_BLIP, SE_CLEAR, SE_CRASH, SE_POINT, W, Game, se

COLS, ROWS = 4, 4
CW, CH = 28, 22
OX, OY = 18, 14


def card_pos(i):
    return OX + i % COLS * 32, OY + i // COLS * 26


def draw_symbol(kind, cx, cy):
    if kind == 0:
        pyxel.circ(cx, cy, 6, 8)
    elif kind == 1:
        pyxel.rect(cx - 5, cy - 5, 11, 11, 12)
    elif kind == 2:
        pyxel.tri(cx, cy - 6, cx - 6, cy + 5, cx + 6, cy + 5, 10)
    elif kind == 3:
        pyxel.tri(cx, cy - 7, cx - 6, cy, cx + 6, cy, 11)
        pyxel.tri(cx, cy + 7, cx - 6, cy, cx + 6, cy, 11)
    elif kind == 4:
        pyxel.circb(cx, cy, 6, 14)
        pyxel.circb(cx, cy, 3, 14)
    elif kind == 5:
        pyxel.rect(cx - 6, cy - 2, 13, 5, 9)
        pyxel.rect(cx - 2, cy - 6, 5, 13, 9)
    elif kind == 6:
        for d in range(-1, 2):
            pyxel.line(cx - 6, cy - 6 + d, cx + 6, cy + 6 + d, 2)
            pyxel.line(cx - 6, cy + 6 + d, cx + 6, cy - 6 + d, 2)
    else:
        pyxel.circ(cx - 3, cy - 2, 3, 6)
        pyxel.circ(cx + 3, cy - 2, 3, 6)
        pyxel.tri(cx - 6, cy - 1, cx + 6, cy - 1, cx, cy + 6, 6)


class Memory(Game):
    title = "MEMORY"
    controls = "CLICK or ARROWS+SPACE: flip"

    def reset(self):
        super().reset()
        self.cards = list(range(8)) * 2
        random.shuffle(self.cards)
        self.matched = [False] * 16
        self.open = []
        self.wait = 0
        self.moves = 0
        self.cursor = 0
        self.frames = 0

    def flip(self, i):
        if self.matched[i] or i in self.open or len(self.open) == 2:
            return
        self.open.append(i)
        se(SE_BLIP)
        if len(self.open) == 2:
            self.moves += 1
            a, b = self.open
            if self.cards[a] == self.cards[b]:
                self.matched[a] = self.matched[b] = True
                self.open = []
                se(SE_POINT)
                if all(self.matched):
                    self.score = max(10, 100 - (self.moves - 8) * 4)
                    self.finish(f"CLEAR! {self.moves} MOVES", SE_CLEAR)
            else:
                self.wait = 40

    def update(self):
        self.frames += 1
        if self.wait:
            self.wait -= 1
            if self.wait == 0:
                self.open = []
                se(SE_CRASH)
            return

        x, y = self.cursor % COLS, self.cursor // COLS
        if pyxel.btnp(pyxel.KEY_LEFT):
            x = (x - 1) % COLS
        if pyxel.btnp(pyxel.KEY_RIGHT):
            x = (x + 1) % COLS
        if pyxel.btnp(pyxel.KEY_UP):
            y = (y - 1) % ROWS
        if pyxel.btnp(pyxel.KEY_DOWN):
            y = (y + 1) % ROWS
        self.cursor = y * COLS + x
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            self.flip(self.cursor)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for i in range(16):
                cx, cy = card_pos(i)
                if cx <= pyxel.mouse_x < cx + CW and cy <= pyxel.mouse_y < cy + CH:
                    self.cursor = i
                    self.flip(i)

    def draw(self):
        pyxel.cls(5)
        pyxel.text(2, 3, f"MOVES {self.moves}", 7)
        pyxel.text(W - 44, 3, f"TIME {self.frames // 60:3}", 7)
        for i in range(16):
            x, y = card_pos(i)
            if self.matched[i] or i in self.open:
                pyxel.rect(x, y, CW, CH, 6 if self.matched[i] else 7)
                draw_symbol(self.cards[i], x + CW // 2, y + CH // 2)
            else:
                pyxel.rect(x, y, CW, CH, 1)
                pyxel.rectb(x + 2, y + 2, CW - 4, CH - 4, 12)
                pyxel.text(x + 12, y + 8, "?", 12)
            if i == self.cursor:
                pyxel.rectb(x - 2, y - 2, CW + 4, CH + 4, 10)
