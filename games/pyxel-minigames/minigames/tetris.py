import random

import pyxel

from common import SE_BLIP, SE_CLEAR, SE_POINT, Game, se

BW, BH = 10, 20
CELL = 5
OX, OY = 55, 10
SHAPES = {
    "I": (["....", "####", "....", "...."], 12),
    "O": (["##", "##"], 10),
    "T": ([".#.", "###", "..."], 2),
    "S": ([".##", "##.", "..."], 11),
    "Z": (["##.", ".##", "..."], 8),
    "J": (["#..", "###", "..."], 5),
    "L": (["..#", "###", "..."], 9),
}
LINE_SCORES = [0, 100, 300, 500, 800]


def rotate(mat):
    n = len(mat)
    return ["".join(mat[n - 1 - j][i] for j in range(n)) for i in range(n)]


def cells(mat):
    return [(x, y) for y, row in enumerate(mat) for x, c in enumerate(row) if c == "#"]


class Tetris(Game):
    title = "TETRIS"
    controls = "ARROWS: move/rotate  SPACE: drop"

    def reset(self):
        super().reset()
        self.board = [[0] * BW for _ in range(BH)]
        self.bag = []
        self.lines = 0
        self.fall = 0
        self.next = self.draw_bag()
        self.spawn()

    @property
    def level(self):
        return self.lines // 10 + 1

    def draw_bag(self):
        # 7種類を1セットずつ配る方式にすると、同じミノが偏って続かない
        if not self.bag:
            self.bag = list(SHAPES)
            random.shuffle(self.bag)
        return self.bag.pop()

    def spawn(self):
        self.kind = self.next
        self.next = self.draw_bag()
        self.mat, self.color = SHAPES[self.kind]
        self.px = (BW - len(self.mat)) // 2
        self.py = -1 if self.kind == "I" else 0
        if not self.fits(self.mat, self.px, self.py):
            self.finish()

    def fits(self, mat, px, py):
        for x, y in cells(mat):
            bx, by = px + x, py + y
            if not (0 <= bx < BW and by < BH) or (by >= 0 and self.board[by][bx]):
                return False
        return True

    def try_move(self, dx, dy):
        if self.fits(self.mat, self.px + dx, self.py + dy):
            self.px += dx
            self.py += dy
            return True
        return False

    def try_rotate(self):
        mat = rotate(self.mat)
        for kick in (0, -1, 1, -2, 2):
            if self.fits(mat, self.px + kick, self.py):
                self.mat = mat
                self.px += kick
                se(SE_BLIP)
                return

    def lock(self):
        for x, y in cells(self.mat):
            if self.py + y >= 0:
                self.board[self.py + y][self.px + x] = self.color
        full = [y for y in range(BH) if all(self.board[y])]
        if full:
            self.score += LINE_SCORES[len(full)] * self.level
            self.lines += len(full)
            self.board = [[0] * BW for _ in full] + [r for y, r in enumerate(self.board) if y not in full]
            se(SE_CLEAR if len(full) == 4 else SE_POINT)
        self.spawn()

    def ghost_y(self):
        y = self.py
        while self.fits(self.mat, self.px, y + 1):
            y += 1
        return y

    def update(self):
        if pyxel.btnp(pyxel.KEY_LEFT, hold=10, repeat=3):
            self.try_move(-1, 0)
        if pyxel.btnp(pyxel.KEY_RIGHT, hold=10, repeat=3):
            self.try_move(1, 0)
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.KEY_Z):
            self.try_rotate()
        if pyxel.btnp(pyxel.KEY_SPACE):
            drop = self.ghost_y() - self.py
            self.py += drop
            self.score += drop * 2
            self.lock()
            return

        speed = max(4, 48 - (self.level - 1) * 5)
        if pyxel.btn(pyxel.KEY_DOWN):
            speed = 3
        self.fall += 1
        if self.fall >= speed:
            self.fall = 0
            if not self.try_move(0, 1):
                self.lock()
            elif pyxel.btn(pyxel.KEY_DOWN):
                self.score += 1

    def cell(self, x, y, col):
        if y < 0:
            return
        px, py = OX + x * CELL, OY + y * CELL
        pyxel.rect(px, py, CELL - 1, CELL - 1, col)
        pyxel.pset(px, py, 7)

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(OX - 1, OY - 1, BW * CELL + 1, BH * CELL + 1, 1)
        pyxel.rectb(OX - 2, OY - 2, BW * CELL + 3, BH * CELL + 3, 13)
        for y, row in enumerate(self.board):
            for x, col in enumerate(row):
                if col:
                    self.cell(x, y, col)
        if not self.over:
            gy = self.ghost_y()
            for x, y in cells(self.mat):
                if gy + y >= 0:
                    pyxel.rectb(OX + (self.px + x) * CELL, OY + (gy + y) * CELL, CELL - 1, CELL - 1, 5)
            for x, y in cells(self.mat):
                self.cell(self.px + x, self.py + y, self.color)

        pyxel.text(4, 10, "SCORE", 13)
        pyxel.text(4, 18, str(self.score), 7)
        pyxel.text(4, 34, "LINES", 13)
        pyxel.text(4, 42, str(self.lines), 7)
        pyxel.text(4, 58, "LEVEL", 13)
        pyxel.text(4, 66, str(self.level), 7)
        pyxel.text(116, 10, "NEXT", 13)
        mat, col = SHAPES[self.next]
        for x, y in cells(mat):
            pyxel.rect(118 + x * CELL, 22 + y * CELL, CELL - 1, CELL - 1, col)
