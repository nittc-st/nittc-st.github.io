import pyxel

W, H = 160, 120

SE_BLIP, SE_POINT, SE_CRASH, SE_CLEAR, SE_SHOT = range(5)


def init_sounds():
    pyxel.sounds[SE_BLIP].set("c3", "p", "5", "f", 5)
    pyxel.sounds[SE_POINT].set("g3c4", "s", "5", "n", 6)
    pyxel.sounds[SE_CRASH].set("c2a1f1d1", "n", "7654", "f", 8)
    pyxel.sounds[SE_CLEAR].set("c3e3g3c4", "s", "5", "n", 8)
    pyxel.sounds[SE_SHOT].set("a3e3", "t", "43", "f", 4)


def se(snd):
    pyxel.play(3, snd)


def text_center(y, s, col):
    pyxel.text((W - len(s) * 4) // 2, y, s, col)


def overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


class Game:
    """ミニゲームの基底クラス。ランチャーが update / draw を呼び出す。"""

    title = "?"
    controls = ""

    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.over = False
        self.message = "GAME OVER"

    def finish(self, message="GAME OVER", sound=SE_CRASH):
        self.over = True
        self.message = message
        se(sound)

    def update(self):
        pass

    def draw(self):
        pass
