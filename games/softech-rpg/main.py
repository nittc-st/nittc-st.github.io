import pyxel

import sprites
import ui
from battle import Battle
from player import Player
from world import World

ENDING = [
    "ソフテクRPG",
    "",
    "サーバー室の バグは きえさり",
    "ソフテク部は ぶじに プロコン本番を むかえた。",
    "",
    "きみの ぼうけんは ここで おわりだが",
    "ほんものの かいはつは これからだ！",
    "",
    "つくった：苫小牧高専 ソフトウェアテクノロジー部",
    "つかった：Pyxel",
    "フォント：美咲フォント",
    "",
    "プレイしてくれて ありがとう！",
]


class Game:
    def __init__(self):
        pyxel.init(ui.W, ui.H, title="Softech RPG", fps=60, quit_key=pyxel.KEY_NONE)
        ui.init()
        self.scene = "title"
        self.frames = 0
        pyxel.run(self.update, self.draw)

    def new_game(self):
        self.player = Player()
        self.world = World(self)
        self.battle = None
        self.scene = "world"
        ui.bgm(ui.BGM_MAP)
        self.world.script.say("ここは 苫小牧高専", "ソフトウェアテクノロジー部の 部室。", "きょうから きみも ソフテク部員だ！")
        self.world.script.say("まずは 部長に あいさつ しよう。", "(矢印キーで いどう、Zキーで はなす)")

    # ---- シーンの切りかえ ----------------------------------------------

    def start_battle(self, enemy_key):
        self.battle = Battle(self, enemy_key)
        self.scene = "transition"
        self.frames = 0
        pyxel.stop()
        ui.se(ui.SE_ENCOUNTER)

    def end_battle(self, won_boss=False):
        self.scene = "world"
        self.battle = None
        ui.bgm(ui.BGM_MAP)
        if won_boss:
            self.world.boss_defeated()

    def game_over(self):
        self.scene = "gameover"
        self.frames = 0

    def start_ending(self):
        self.scene = "ending"
        self.frames = 0
        ui.bgm(ui.BGM_MAP)

    # ---- 更新 ----------------------------------------------------------

    def update(self):
        self.frames += 1
        if self.scene == "title":
            if self.frames > 20 and ui.confirm_pressed():
                ui.se(ui.SE_OK)
                self.new_game()
        elif self.scene == "world":
            self.world.update()
        elif self.scene == "transition":
            if self.frames >= 40:
                self.scene = "battle"
                ui.bgm(ui.BGM_BOSS if self.battle.boss else ui.BGM_BATTLE)
        elif self.scene == "battle":
            self.battle.update()
        elif self.scene == "gameover":
            if self.frames > 60 and ui.confirm_pressed():
                self.revive()
        elif self.scene == "ending":
            if self.frames > 120 and ui.confirm_pressed():
                ui.bgm(None)
                self.scene = "title"
                self.frames = 0

    def revive(self):
        self.battle = None
        self.player.recover()
        self.world.respawn()
        self.scene = "world"
        ui.bgm(ui.BGM_MAP)
        self.world.script.say("部長「だいじょうぶか？", "ここまで はこんで きたぞ。むりは するなよ。")

    # ---- 描画 ----------------------------------------------------------

    def draw(self):
        if self.scene == "title":
            self.draw_title()
        elif self.scene == "world":
            self.world.draw()
        elif self.scene == "transition":
            self.world.draw()
            # 画面を横じまで黒くしていく
            n = self.frames
            for y in range(0, ui.H, 8):
                pyxel.rect(0, y, ui.W, min(8, n // 4 + (y // 8) % 3 - 1), 0)
            if n < 12 and n % 4 < 2:
                pyxel.rect(0, 0, ui.W, ui.H, 7)
        elif self.scene == "battle":
            self.battle.draw()
        elif self.scene == "gameover":
            pyxel.cls(0)
            ui.text_center(80, "めのまえが まっくらに なった……", 8)
            if self.frames > 60:
                ui.text_center(110, "Zキーで 部室から やりなおす", 13)
        else:
            self.draw_ending()

    def draw_title(self):
        pyxel.cls(1)
        f = pyxel.frame_count
        for i in range(40):
            x = (i * 37 + f // 2) % ui.W
            y = (i * 53) % ui.H
            pyxel.text(x, y, "01"[(i + f // 30) % 2], 5)
        for i, (shape, col) in enumerate((("bug", 11), ("ghost", 6), ("loop", 12), ("glitch", 8))):
            if (f // 120) % 4 == i:
                sprites.monster(shape, col, ui.W // 2, 132)
        pyxel.rect(36, 30, ui.W - 72, 44, 0)
        pyxel.rectb(36, 30, ui.W - 72, 44, 10)
        pyxel.rectb(38, 32, ui.W - 76, 40, 9)
        ui.text_big(36, "ソフテクRPG", 10, 8)
        ui.text_center(61, "～ バグを たおして プロコンへ ～", 7)
        if f // 30 % 2:
            ui.text_center(166, "Zキー / スペースで はじめる", 7, 0)
        ui.text_center(180, "矢印:いどう  Z:けってい  X:ステータス・もどる", 13)
        sprites.person(30, 120, sprites.RIGHT, 0, 7, f // 10 % 2)

    def draw_ending(self):
        pyxel.cls(0)
        # 下からせり上がってきて、上端に着いたら止まる
        offset = max(0, ui.H - self.frames // 2)
        for i, line in enumerate(ENDING):
            ui.text_center(8 + i * 11 + offset, line, 10 if i == 0 else 7)
        if self.frames > 120:
            p = self.player
            ui.text(4, ui.H - 12, f"LV{p.level}  たたかった かいすう {p.battles}", 13)
            ui.text(ui.W - 92, ui.H - 12, "Zで タイトルへ", 13)


if __name__ == "__main__":
    Game()
