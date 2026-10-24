import json
import os
import sys

import pyxel

from common import SE_BLIP, H, W, init_sounds, se, text_center
from minigames.breakout import Breakout
from minigames.dodge import Dodge
from minigames.flappy import Flappy
from minigames.g2048 import G2048
from minigames.invaders import Invaders
from minigames.memory import Memory
from minigames.minesweeper import Minesweeper
from minigames.pong import Pong
from minigames.runner import Runner
from minigames.snake import Snake
from minigames.tetris import Tetris
from minigames.whack import Whack

GAMES = [Snake, Breakout, Pong, Flappy, Invaders, Dodge, Runner, Tetris, G2048, Memory, Minesweeper, Whack]
ROWS = 6


def item_pos(i):
    return 14 + i // ROWS * 74, 24 + i % ROWS * 12


class App:
    def __init__(self, start=None):
        pyxel.init(W, H, title="Pyxel Mini Games", fps=60, quit_key=pyxel.KEY_NONE)
        init_sounds()
        self.score_file = None
        self.best = self.load_scores()
        self.sel = 0
        self.game = None
        self.paused = False
        self.over_frames = 0
        self.last_mouse = (0, 0)
        if start is not None:
            self.start(start)
        pyxel.run(self.update, self.draw)

    def load_scores(self):
        try:
            self.score_file = os.path.join(pyxel.user_data_dir("nittc-st", "minigames"), "scores.json")
            with open(self.score_file) as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def save_score(self):
        name = self.game.title
        if self.game.score <= self.best.get(name, 0):
            return
        self.best[name] = self.game.score
        if self.score_file is None:
            return
        try:
            with open(self.score_file, "w") as f:
                json.dump(self.best, f)
        except OSError:
            pass

    def start(self, i):
        self.sel = i
        self.game = GAMES[i]()
        self.paused = False
        self.over_frames = 0
        pyxel.mouse(GAMES[i] in (Memory, Minesweeper))

    def back_to_menu(self):
        self.save_score()
        self.game = None
        pyxel.mouse(True)

    def update(self):
        if self.game is None:
            self.update_menu()
            return

        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_BACKSPACE) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.back_to_menu()
            return
        if pyxel.btnp(pyxel.KEY_R):
            self.save_score()
            self.start(self.sel)
            return

        if self.game.over:
            self.over_frames += 1
            # 死んだ瞬間のキー入力ですぐにリトライしないよう、少し待つ
            if self.over_frames > 40 and (pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE)):
                self.start(self.sel)
            return

        if pyxel.btnp(pyxel.KEY_P):
            self.paused = not self.paused
        if not self.paused:
            self.game.update()
            if self.game.over:
                self.save_score()

    def update_menu(self):
        n = len(GAMES)
        if pyxel.btnp(pyxel.KEY_DOWN, hold=12, repeat=4):
            self.sel = (self.sel + 1) % n
        if pyxel.btnp(pyxel.KEY_UP, hold=12, repeat=4):
            self.sel = (self.sel - 1) % n
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_LEFT):
            self.sel = (self.sel + ROWS) % n
        if any(pyxel.btnp(k) for k in (pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT)):
            se(SE_BLIP)

        mouse = (pyxel.mouse_x, pyxel.mouse_y)
        hovered = None
        for i in range(n):
            x, y = item_pos(i)
            if x - 4 <= mouse[0] < x + 70 and y - 2 <= mouse[1] < y + 9:
                hovered = i
        # マウスが動いたときだけ選択を追従させ、キー操作と競合しないようにする
        if hovered is not None and mouse != self.last_mouse:
            self.sel = hovered
        self.last_mouse = mouse

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            self.start(self.sel)
        elif hovered is not None and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.start(hovered)

    def draw(self):
        if self.game is None:
            self.draw_menu()
            return
        self.game.draw()
        if self.game.over:
            self.draw_panel(
                self.game.message,
                f"SCORE {self.game.score}   BEST {self.best.get(self.game.title, 0)}",
                "ENTER: retry  Q: menu",
            )
        elif self.paused:
            self.draw_panel("PAUSE", self.game.controls, "P: resume  R: retry  Q: menu")

    def draw_panel(self, title, line1, line2):
        width = max(len(title), len(line1), len(line2)) * 4 + 12
        x, y = (W - width) // 2, 38
        pyxel.rect(x, y, width, 40, 0)
        pyxel.rectb(x, y, width, 40, 7)
        text_center(y + 6, title, 10)
        text_center(y + 18, line1, 7)
        text_center(y + 29, line2, 13)

    def draw_menu(self):
        pyxel.cls(1)
        for i in range(24):
            x = (i * 53 + pyxel.frame_count // 3) % (W + 10) - 5
            pyxel.pset(x, (i * 29) % H, 5)
        title = "PYXEL MINI GAMES"
        for i, ch in enumerate(title):
            dy = pyxel.sin(pyxel.frame_count * 4 + i * 25) * 1.5
            pyxel.text((W - len(title) * 4) // 2 + i * 4, 8 + dy, ch, 8 + i % 8)
        for i, game in enumerate(GAMES):
            x, y = item_pos(i)
            if i == self.sel:
                pyxel.rect(x - 4, y - 2, 70, 10, 5)
                pyxel.text(x - 2, y, ">", 10)
            pyxel.text(x + 4, y, game.title, 7 if i == self.sel else 6)
        game = GAMES[self.sel]
        pyxel.line(0, 98, W, 98, 5)
        pyxel.text(4, 102, game.controls, 7)
        pyxel.text(4, 111, f"BEST {self.best.get(game.title, 0)}", 10)
        pyxel.text(W - 64, 111, "ENTER: start", 13)


if __name__ == "__main__":
    names = [g.__name__.lower() for g in GAMES]
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
    App(names.index(arg) if arg in names else None)
