import os

import pyxel

W, H = 256, 192
LINE_H = 12

# assets/font.bdf は subset_font.py で、ゲーム中で使う文字だけを抜き出した日本語フォント
FONT = None

SE_CURSOR, SE_OK, SE_HIT, SE_DAMAGE, SE_HEAL, SE_LEVELUP, SE_ENCOUNTER, SE_WIN = range(8)
BGM_MAP, BGM_BATTLE, BGM_BOSS = range(3)


def init():
    global FONT
    FONT = pyxel.Font(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "font.bdf"))

    pyxel.sounds[SE_CURSOR].set("c3", "p", "4", "n", 4)
    pyxel.sounds[SE_OK].set("g3c4", "p", "5", "n", 4)
    pyxel.sounds[SE_HIT].set("c3g2c2", "n", "765", "f", 4)
    pyxel.sounds[SE_DAMAGE].set("f2c2f1c1", "n", "7765", "f", 5)
    pyxel.sounds[SE_HEAL].set("c3e3g3c4e4g4", "s", "5", "n", 4)
    pyxel.sounds[SE_LEVELUP].set("c3e3g3c4 r g3c4e4g4", "s", "6", "n", 7)
    pyxel.sounds[SE_ENCOUNTER].set("c4b3a#3a3g#3g3f#3f3", "p", "6", "n", 3)
    pyxel.sounds[SE_WIN].set("g3g3g3 e3 g3 r c4", "s", "6", "n", 9)

    # BGM はチャンネル 0, 1 を使い、効果音はチャンネル 3 で鳴らす
    pyxel.sounds[10].set("e3g3c4g3 a3g3e3r f3a3c4a3 g3e3d3r e3g3c4e4 d4c4a3g3 f3a3g3f3 e3r c3r",
                         "t", "4", "n", 22)
    pyxel.sounds[11].set("c2r g1r a1r e1r f1r c2r d2r g1r c2r e2r f1r d2r f1r g1r c2r c2r",
                         "t", "5", "n", 22)
    pyxel.sounds[12].set("a2c3e3a3 g3e3c3e3 f3a3c4a3 e3g#3b3e4 a3e3c3a2 g3d3b2g2 f3c3a2f2 e3b2g#2e2",
                         "s", "4", "n", 11)
    pyxel.sounds[13].set("a1a1a1a1 a1a1a1a1 f1f1f1f1 e1e1e1e1 a1a1a1a1 g1g1g1g1 f1f1f1f1 e1e1e1e1",
                         "t", "6", "n", 11)
    pyxel.sounds[14].set("d3d3f3d3 g#3f3d3c#3 d3d3f3d3 a3g#3f3e3 d3f3a3d4 c#4a3f3e3 d3e3f3g3 g#3a3g#3e3",
                         "p", "4", "n", 9)
    pyxel.sounds[15].set("d1d1d2d1 d1d1d2d1 a#0a#0a#1a#0 a0a0a1a0 d1d1d2d1 d1d1d2d1 a#0a#0a#1a#0 a0a0a1a0",
                         "t", "6", "n", 9)
    pyxel.musics[BGM_MAP].set([10], [11])
    pyxel.musics[BGM_BATTLE].set([12], [13])
    pyxel.musics[BGM_BOSS].set([14], [15])


def se(snd):
    pyxel.play(3, snd)


def bgm(music):
    pyxel.stop()
    if music is not None:
        pyxel.playm(music, loop=True)


def text(x, y, s, col):
    pyxel.text(x, y, s, col, FONT)


def text_width(s):
    return FONT.text_width(s)


def text_border(x, y, s, col, bcol):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                pyxel.text(x + dx, y + dy, s, bcol, FONT)
    pyxel.text(x, y, s, col, FONT)


def text_center(y, s, col, bcol=None):
    x = (W - text_width(s)) // 2
    if bcol is None:
        text(x, y, s, col)
    else:
        text_border(x, y, s, col, bcol)


def text_big(y, s, col, bcol):
    """ふちどり文字をドットごと2倍に拡大して、画面中央に描く。"""
    w, h = text_width(s) + 2, 10
    img = pyxel.Image(w, h)
    img.cls(0)
    for dx in (0, 1, 2):
        for dy in (0, 1, 2):
            if dx != 1 or dy != 1:
                img.text(dx, dy, s, bcol, FONT)
    img.text(1, 1, s, col, FONT)
    # scale は元の大きさで置いたときの中心を基準に拡大されるので、中心が (W / 2, y + h) に来るよう置く
    pyxel.blt(W / 2 - w / 2, y + h / 2, img, 0, 0, w, h, 0, scale=2)


def cursor(x, y, col):
    pyxel.tri(x, y + 1, x, y + 7, x + 4, y + 4, col)


def window(x, y, w, h):
    pyxel.rect(x, y, w, h, 0)
    pyxel.rectb(x + 1, y + 1, w - 2, h - 2, 7)


def confirm_pressed():
    return pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN)


def cancel_pressed():
    return pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.KEY_BACKSPACE)


class Script:
    """メッセージと処理を順番に実行する待ち行列。

    say() でメッセージを、do() で関数を積む。関数の中で say() / do() を呼ぶと、
    その関数の直後に割り込んで実行されるので、バトルの流れをそのまま書き下せる。
    """

    def __init__(self):
        self.items = []
        self.insert_at = None
        self.lines = None
        self.shown = 0

    @property
    def busy(self):
        return self.lines is not None or bool(self.items)

    def _push(self, item):
        if self.insert_at is None:
            self.items.append(item)
        else:
            self.items.insert(self.insert_at, item)
            self.insert_at += 1

    def say(self, *lines):
        self._push(("say", lines))

    def do(self, fn):
        self._push(("do", fn))

    def clear(self):
        self.items = []
        self.lines = None

    def advance(self):
        while self.lines is None and self.items:
            kind, value = self.items.pop(0)
            if kind == "say":
                self.lines = value
                self.shown = 0
                se(SE_CURSOR)
            else:
                self.insert_at = 0
                try:
                    value()
                finally:
                    self.insert_at = None

    def update(self):
        self.advance()
        if self.lines is None:
            return
        total = sum(len(s) for s in self.lines)
        if self.shown < total:
            self.shown += 1
            if confirm_pressed():
                self.shown = total
        elif confirm_pressed():
            self.lines = None
            self.advance()

    def draw(self, x=4, y=134, w=248, h=54):
        if self.lines is None:
            return
        window(x, y, w, h)
        left = self.shown
        for i, line in enumerate(self.lines):
            text(x + 8, y + 7 + i * LINE_H, line[:max(0, left)], 7)
            left -= len(line)
        total = sum(len(s) for s in self.lines)
        if self.shown >= total and pyxel.frame_count // 15 % 2:
            text(x + w - 16, y + h - 14, "▼", 7)
