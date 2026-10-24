import random

import pyxel

import sprites
import ui
from data import ENEMIES, ITEMS

COMMANDS = ["たたかう", "スキル", "どうぐ", "にげる"]


def damage(atk, df, power=1.0):
    base = atk * power - df / 2
    return max(1, int(base + random.uniform(-base * 0.15, base * 0.15)))


class Battle:
    def __init__(self, game, enemy_key):
        self.game = game
        self.player = game.player
        self.key = enemy_key
        self.name, self.max_hp, self.atk, self.df, self.exp, self.col, self.shape = ENEMIES[enemy_key]
        self.hp = self.max_hp
        self.boss = enemy_key == "boss"
        self.script = ui.Script()
        self.mode = "script"
        self.cursor = 0
        self.sub_cursor = 0
        self.flash = 0
        self.shake = 0
        self.dying = 0
        self.turn = 0
        self.charging = False
        self.script.say(f"{self.name}が あらわれた！")
        self.script.do(self.to_command)

    # ---- 入力 ----------------------------------------------------------

    def update(self):
        self.flash = max(0, self.flash - 1)
        self.shake = max(0, self.shake - 1)
        if self.dying:
            self.dying -= 1
        if self.mode == "script":
            self.script.update()
        elif self.mode == "command":
            self.update_command()
        else:
            self.update_submenu()

    def move_cursor(self, value, n):
        if pyxel.btnp(pyxel.KEY_UP):
            ui.se(ui.SE_CURSOR)
            return (value - 1) % n
        if pyxel.btnp(pyxel.KEY_DOWN):
            ui.se(ui.SE_CURSOR)
            return (value + 1) % n
        return value

    def update_command(self):
        self.cursor = self.move_cursor(self.cursor, len(COMMANDS))
        if not ui.confirm_pressed():
            return
        ui.se(ui.SE_OK)
        if self.cursor == 0:
            self.run(self.player_attack)
        elif self.cursor == 1:
            self.mode, self.sub_cursor = "skill", 0
        elif self.cursor == 2:
            if self.player.item_list():
                self.mode, self.sub_cursor = "item", 0
            else:
                self.run(lambda: self.script.say("どうぐを なにも もっていない！"), enemy_turn=False)
        else:
            self.run(self.escape)

    def update_submenu(self):
        options = self.player.skills() if self.mode == "skill" else self.player.item_list()
        self.sub_cursor = self.move_cursor(self.sub_cursor, len(options))
        if ui.cancel_pressed():
            self.mode = "command"
            return
        if not ui.confirm_pressed():
            return
        if self.mode == "skill":
            skill = options[self.sub_cursor]
            if self.player.mp < skill[1]:
                ui.se(ui.SE_DAMAGE)
                return
            ui.se(ui.SE_OK)
            self.run(lambda: self.use_skill(skill))
        else:
            key = options[self.sub_cursor][0]
            ui.se(ui.SE_OK)
            self.run(lambda: self.use_item(key))

    def run(self, action, enemy_turn=True):
        """プレイヤーの行動のあと、敵の番を回してコマンド選択に戻る。"""
        self.mode = "script"
        self.script.do(action)
        if enemy_turn:
            self.script.do(self.enemy_turn)
        self.script.do(self.to_command)

    def to_command(self):
        self.mode = "command"

    # ---- プレイヤーの行動 ----------------------------------------------

    def player_attack(self):
        self.script.say("きみの こうげき！")
        self.script.do(lambda: self.hit_enemy(damage(self.player.atk, self.df)))

    def use_skill(self, skill):
        name, mp, _, kind, _ = skill
        self.player.mp -= mp
        if kind == "attack":
            self.script.say(f"きみは {name}を つかった！", "バグの いばしょを つきとめた！")
            self.script.do(lambda: self.hit_enemy(damage(self.player.atk, 0, 1.6)))
        elif kind == "big":
            self.script.say(f"きみは {name}を つかった！", "へんこうを なかったことに した！")
            self.script.do(lambda: self.hit_enemy(damage(self.player.atk, 0, 2.6)))
        else:
            amount = 18 + self.player.level * 5
            self.script.say(f"きみは {name}を つかった！", "コードが すっきり した！")
            self.script.do(lambda: self.heal("hp", amount))

    def use_item(self, key):
        name, kind, amount = ITEMS[key]
        self.player.items[key] -= 1
        self.script.say(f"きみは {name}を つかった！")
        self.script.do(lambda: self.heal(kind, amount))

    def heal(self, kind, amount):
        p = self.player
        if kind == "hp":
            before, p.hp = p.hp, min(p.max_hp, p.hp + amount)
            self.script.say(f"HPが {p.hp - before} かいふく した！")
        else:
            before, p.mp = p.mp, min(p.max_mp, p.mp + amount)
            self.script.say(f"MPが {p.mp - before} かいふく した！")
        ui.se(ui.SE_HEAL)

    def escape(self):
        if self.boss:
            self.script.say("きみは にげだした！", "しかし デッドロックに まわりこまれた！")
        elif random.random() < 0.7:
            self.script.clear()
            self.script.say("きみは うまく にげきった！")
            self.script.do(self.game.end_battle)
        else:
            self.script.say("きみは にげだした！", "しかし まわりこまれてしまった！")

    def hit_enemy(self, dmg):
        self.hp = max(0, self.hp - dmg)
        self.flash = 16
        ui.se(ui.SE_HIT)
        self.script.say(f"{self.name}に {dmg}の ダメージ！")
        if self.hp == 0:
            self.script.do(self.win)

    # ---- 敵の行動 ------------------------------------------------------

    def enemy_turn(self):
        self.turn += 1
        s = self.script
        if self.boss:
            if self.charging:
                self.charging = False
                s.say("デッドロックの ぜんスレッドていし！")
                s.do(lambda: self.hit_player(damage(self.atk, self.player.df, 1.8)))
                return
            if self.turn % 3 == 0:
                self.charging = True
                s.say("デッドロックは リソースを", "かかえこんでいる……！")
                return
        if self.key == "loop" and random.random() < 0.25:
            s.say("むげんループは ぐるぐる まわっている。")
            return
        if self.key == "leak" and random.random() < 0.3 and self.player.mp > 0:
            lost = min(self.player.mp, 3)
            s.say("メモリリークは メモリを くいつぶした！")
            s.do(lambda: self.drain_mp(lost))
            return
        s.say(f"{self.name}の こうげき！")
        s.do(lambda: self.hit_player(damage(self.atk, self.player.df)))

    def drain_mp(self, lost):
        self.player.mp -= lost
        ui.se(ui.SE_DAMAGE)
        self.script.say(f"きみの MPが {lost} へった！")

    def hit_player(self, dmg):
        self.player.hp = max(0, self.player.hp - dmg)
        self.shake = 12
        ui.se(ui.SE_DAMAGE)
        self.script.say(f"きみは {dmg}の ダメージを うけた！")
        if self.player.hp == 0:
            self.script.do(self.lose)

    # ---- 決着 ----------------------------------------------------------

    def win(self):
        s = self.script
        # 勝ったら、このあとに積まれている敵の番やコマンド選択は捨てる
        s.items = []
        self.dying = 30
        ui.bgm(None)
        ui.se(ui.SE_WIN)
        self.player.battles += 1
        s.say(f"{self.name}を たおした！", f"{self.exp}の けいけんちを かくとく！")
        for level, learned in self.player.gain_exp(self.exp):
            s.do(lambda: ui.se(ui.SE_LEVELUP))
            s.say(f"レベルが あがった！ LV{level}に なった！")
            for name in learned:
                s.say(f"{name}を おぼえた！")
        if not self.boss and random.random() < 0.2:
            key = random.choice(["drink", "drink", "ramune"])
            self.player.items[key] += 1
            s.say(f"{self.name}は {ITEMS[key][0]}を おとしていった！")
        s.do(lambda: self.game.end_battle(won_boss=self.boss))

    def lose(self):
        s = self.script
        s.items = []
        ui.bgm(None)
        s.say("きみは たおれてしまった……")
        s.do(self.game.game_over)

    # ---- 描画 ----------------------------------------------------------

    def draw(self):
        dx = (random.randint(-3, 3) if self.shake else 0)
        pyxel.camera(dx, 0)
        pyxel.cls(0)
        for i in range(12):
            pyxel.line(0, 96 + i * i, ui.W, 96 + i * i, 1)
        for i in range(9):
            x = i * 32 + 16
            pyxel.line(x, 96, ui.W / 2 + (x - ui.W / 2) * 4, ui.H + 200, 1)

        visible = not (self.flash and self.flash % 4 < 2)
        if self.dying:
            visible = self.dying % 4 < 2 and self.dying > 6
        elif self.hp == 0:
            visible = False
        if visible:
            sprites.monster(self.shape, self.col, ui.W // 2, 76)
        pyxel.camera()

        p = self.player
        ui.window(4, 4, 132, 36)
        ui.text(12, 9, f"きみ  LV{p.level}", 7)
        hp_col = 8 if p.hp <= p.max_hp // 4 else 7
        ui.text(12, 23, f"HP {p.hp:3}/{p.max_hp}  MP {p.mp:2}/{p.max_mp}", hp_col)
        ui.window(156, 4, 96, 22)
        ui.text(164, 9, self.name, 10 if self.boss else 7)
        pyxel.rect(164, 20, 80, 2, 5)
        pyxel.rect(164, 20, 80 * self.hp // self.max_hp, 2, 11 if self.hp > self.max_hp // 4 else 8)

        if self.mode == "script":
            self.script.draw()
            return

        ui.window(4, 134, 76, 54)
        for i, c in enumerate(COMMANDS):
            ui.text(18, 139 + i * 12, c, 7)
        if self.mode == "command":
            ui.cursor(9, 139 + self.cursor * 12, 10)
            ui.window(84, 134, 168, 54)
            ui.text(92, 141, "どうする？", 7)
            ui.text(92, 167, "Z:けってい", 13)
        else:
            ui.cursor(9, 139 + self.cursor * 12, 13)
            self.draw_submenu()

    def draw_submenu(self):
        ui.window(84, 134, 168, 54)
        if self.mode == "skill":
            options = self.player.skills()
            for i, (name, mp, _, _, _) in enumerate(options):
                col = 7 if self.player.mp >= mp else 13
                ui.text(98, 139 + i * 12, name, col)
                ui.text(214, 139 + i * 12, f"MP{mp}", col)
        else:
            options = self.player.item_list()
            for i, (_, (name, _, _), n) in enumerate(options):
                ui.text(98, 139 + i * 12, f"{name}", 7)
                ui.text(214, 139 + i * 12, f"x{n}", 7)
        ui.cursor(89, 139 + self.sub_cursor * 12, 10)
