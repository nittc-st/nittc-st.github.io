import random

import pyxel

import sprites
import ui
from data import ENCOUNTERS, MAP_H, MAP_W, START, WALKABLE, area, tile
from sprites import DIR_VEC, DOWN, LEFT, RIGHT, UP

KEY_DIRS = ((pyxel.KEY_UP, UP), (pyxel.KEY_DOWN, DOWN), (pyxel.KEY_LEFT, LEFT), (pyxel.KEY_RIGHT, RIGHT))
STEP_FRAMES = 8


class Npc:
    def __init__(self, key, x, y, hair, shirt, d=DOWN):
        self.key = key
        self.x, self.y = x, y
        self.hair, self.shirt = hair, shirt
        self.d = d


class World:
    def __init__(self, game):
        self.game = game
        self.player = game.player
        self.script = ui.Script()
        self.flags = set()
        self.npcs = [
            Npc("bucho", 6, 2, 0, 12),
            Npc("senpai_a", 4, 4, 4, 3, RIGHT),
            Npc("senpai_b", 10, 6, 9, 14, LEFT),
            Npc("classmate", 22, 9, 0, 6),
            Npc("teacher", 21, 2, 13, 5),
            Npc("lab", 17, 6, 1, 11, UP),
            Npc("boss", 2, 18, 0, 0),
        ]
        self.respawn()
        self.show_status = False

    def respawn(self):
        self.x, self.y = START
        self.d = UP
        self.moving = 0
        self.steps = 0

    # ---- 移動 ----------------------------------------------------------

    def npc_at(self, x, y):
        for n in self.npcs:
            if (n.x, n.y) == (x, y):
                return n
        return None

    def walkable(self, x, y):
        ch = tile(x, y)
        if ch == "L":
            return "started" in self.flags
        return ch in WALKABLE and self.npc_at(x, y) is None

    def update(self):
        if self.script.busy:
            self.script.update()
            return
        if self.show_status:
            if ui.cancel_pressed() or ui.confirm_pressed():
                self.show_status = False
            return

        if self.moving:
            self.moving -= 1
            if self.moving == 0:
                self.on_step()
            return

        for key, d in KEY_DIRS:
            # 一瞬だけ押されたキーも拾えるよう btnp も見る
            if pyxel.btn(key) or pyxel.btnp(key):
                self.d = d
                dx, dy = DIR_VEC[d]
                if self.walkable(self.x + dx, self.y + dy):
                    self.x += dx
                    self.y += dy
                    self.moving = STEP_FRAMES
                return

        if ui.confirm_pressed():
            self.interact()
        elif ui.cancel_pressed():
            self.show_status = True
            ui.se(ui.SE_OK)

    def on_step(self):
        if tile(self.x, self.y) != ",":
            self.steps = 0
            return
        self.steps += 1
        if self.steps >= 5 and random.random() < 1 / 10:
            self.steps = 0
            pool = next(p for limit, p in ENCOUNTERS if self.y <= limit)
            self.game.start_battle(random.choice(pool))

    # ---- 会話としらべる ------------------------------------------------

    def interact(self):
        dx, dy = DIR_VEC[self.d]
        tx, ty = self.x + dx, self.y + dy
        npc = self.npc_at(tx, ty)
        if npc:
            npc.d = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}[self.d]
            getattr(self, "talk_" + npc.key)()
            return
        ch = tile(tx, ty)
        s = self.script
        if ch == "P":
            if area(tx, ty) == "club":
                s.say("プロコンの ソースコードが ひらかれている。", "……コメントが ひとつも ない。")
            else:
                s.say("ゲームエンジンの ビルドが まわっている。", "あと 3ぷん と ひょうじされている。")
        elif ch == "B":
            s.say("プログラミングの 本が ずらりと ならんでいる。", "『よみやすい コードの かきかた』……", "あとで よんでみよう。")
        elif ch == "T":
            s.say("つくえの うえに かいはつ用の ボードが おいてある。")
        elif ch == "V":
            s.say("自販機で エナドリを かって のんだ！")
            s.do(self.heal)
        elif ch == "S":
            s.say("サーバーラックが ブーンと うなっている。")
        elif ch == "L" and "started" not in self.flags:
            s.say("とびらには かぎが かかっている。", "まずは 部室の 部長に はなしかけよう。")

    def heal(self):
        self.player.recover()
        ui.se(ui.SE_HEAL)
        self.script.say("HPと MPが ぜんかいふく した！")

    def talk_bucho(self):
        s = self.script
        if "boss" in self.flags:
            s.say("部長「やったな！ サーバーが ぶじに", "うごきだしたぞ！")
            s.say("部長「これで プロコン本番にも まにあう。", "きみは もう りっぱな ソフテク部員だ！")
            s.do(self.game.start_ending)
        elif "started" in self.flags:
            s.say("部長「デッドロックは サーバー室の いちばん", "おくに いる。とても つよいぞ。")
            s.say("部長「LV5くらいまで あげてから", "いどむと いいだろう。")
        else:
            s.say("部長「おっ、きみが しんにゅうぶいんだな！", "ようこそ ソフテクへ！")
            s.say("部長「じつは いま たいへんなんだ。", "プロコン本番を まえに サーバー室に", "バグが 大量に わいてしまった！")
            s.say("部長「おくにいる 親玉『デッドロック』を", "たおせば バグも きえるはずだ。")
            s.say("部長「サーバー室は ろうかの 南の とびらだ。", "つかれたら 自販機で ひとやすみ してくれ。", "たのんだぞ！")
            s.do(lambda: self.flags.add("started"))
            s.say("サーバー室の とびらの かぎが あいた！")

    def talk_senpai_a(self):
        self.script.say("先輩「Zキーで はなす・しらべる、", "Xキーで ステータスが みられるよ。")
        self.script.say("先輩「バトルでは MPを つかって", "スキルが つかえる。LVが あがると", "あたらしい スキルを おぼえるよ。")

    def talk_senpai_b(self):
        s = self.script
        if "gift" in self.flags:
            s.say("先輩「サーバー室の おくの バグほど", "つよいから きをつけてね。")
            return
        s.say("先輩「これ、さしいれ！ がんばってね！")
        s.do(self.give_gift)

    def give_gift(self):
        self.flags.add("gift")
        self.player.items["drink"] += 3
        self.player.items["ramune"] += 2
        ui.se(ui.SE_HEAL)
        self.script.say("エナドリを 3こ、ラムネを 2こ もらった！")

    def talk_classmate(self):
        if "boss" in self.flags:
            self.script.say("同級生「すごい！ きみが デッドロックを", "たおしたんだって！？")
        else:
            self.script.say("同級生「ぼくも ソフテクに はいったんだ。", "いっしょに がんばろうね！")

    def talk_teacher(self):
        self.script.say("先生「やあ。ここは 研究室。4・5年生が", "それぞれの テーマで かいはつを しているよ。")
        self.script.say("先生「こまめに git commit しておくことだ。", "……すこし やすんで いきなさい。")
        self.script.do(self.heal)

    def talk_lab(self):
        self.script.say("4年生「いまは ゲームエンジンを さわってるんだ。")
        self.script.say("4年生「Pyxelって しってる？", "このゲームも Pyxelで うごいてるんだよ。")

    def talk_boss(self):
        s = self.script
        s.say("？？？「ワタシハ デッドロック……", "スベテノ スレッドヲ トメテヤル……")
        s.do(lambda: self.game.start_battle("boss"))

    def boss_defeated(self):
        self.flags.add("boss")
        self.npcs = [n for n in self.npcs if n.key != "boss"]
        self.script.say("サーバー室の バグが きえていく……")
        self.script.say("部長に ほうこく しにいこう！")

    # ---- 描画 ----------------------------------------------------------

    def camera(self):
        px = self.x * 16 - DIR_VEC[self.d][0] * self.moving * 2
        py = self.y * 16 - DIR_VEC[self.d][1] * self.moving * 2
        cx = max(0, min(MAP_W * 16 - ui.W, px - ui.W // 2 + 8))
        cy = max(0, min(MAP_H * 16 - ui.H, py - ui.H // 2 + 8))
        return px, py, cx, cy

    def draw(self):
        px, py, cx, cy = self.camera()
        pyxel.cls(0)
        pyxel.camera(cx, cy)
        for ty in range(cy // 16, min(MAP_H, cy // 16 + 13)):
            for tx in range(cx // 16, min(MAP_W, cx // 16 + 17)):
                ch = tile(tx, ty)
                if ch == "L" and "started" in self.flags:
                    ch = "."
                sprites.tile(ch, tx * 16, ty * 16, tx, ty)
        for n in self.npcs:
            if n.key == "boss":
                sprites.boss_mini(n.x * 16, n.y * 16)
            else:
                sprites.person(n.x * 16, n.y * 16, n.d, n.hair, n.shirt)
        step = (self.moving > STEP_FRAMES // 2) if self.moving else 0
        sprites.person(px, py, self.d, 0, 7, step)
        pyxel.camera()

        if self.show_status:
            self.draw_status()
        self.script.draw()

    def draw_status(self):
        p = self.player
        ui.window(8, 8, 124, 96)
        rows = [
            f"LV   {p.level}",
            f"HP   {p.hp}/{p.max_hp}",
            f"MP   {p.mp}/{p.max_mp}",
            f"こうげき {p.atk}",
            f"ぼうぎょ {p.df}",
            f"つぎのLVまで {p.next_exp()}",
        ]
        for i, r in enumerate(rows):
            ui.text(16, 15 + i * 13, r, 7)
        ui.window(136, 8, 112, 60)
        ui.text(144, 15, "どうぐ", 10)
        items = p.item_list()
        if not items:
            ui.text(144, 30, "なし", 13)
        for i, (_, (name, _, _), n) in enumerate(items):
            ui.text(144, 30 + i * 13, f"{name} x{n}", 7)
