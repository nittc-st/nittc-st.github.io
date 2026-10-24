from data import ITEMS, LEVEL_EXP, MAX_LEVEL, SKILLS


class Player:
    def __init__(self):
        self.level = 1
        self.exp = 0
        self.max_hp, self.max_mp = 30, 10
        self.atk, self.df = 8, 4
        self.hp, self.mp = self.max_hp, self.max_mp
        self.items = {"drink": 2, "ramune": 0}
        self.battles = 0

    def skills(self):
        return [s for s in SKILLS if s[2] <= self.level]

    def item_list(self):
        return [(key, ITEMS[key], n) for key, n in self.items.items() if n > 0]

    def recover(self):
        self.hp, self.mp = self.max_hp, self.max_mp

    def gain_exp(self, exp):
        """けいけんちを足し、上がったレベルごとに (新しいLV, おぼえたスキル名) を返す。"""
        self.exp += exp
        ups = []
        while self.level < MAX_LEVEL and self.exp >= LEVEL_EXP[self.level + 1]:
            self.level += 1
            self.max_hp += 8
            self.max_mp += 3
            self.atk += 3
            self.df += 2
            self.hp = min(self.max_hp, self.hp + 8)
            self.mp = min(self.max_mp, self.mp + 3)
            learned = [s[0] for s in SKILLS if s[2] == self.level]
            ups.append((self.level, learned))
        return ups

    def next_exp(self):
        if self.level >= MAX_LEVEL:
            return 0
        return LEVEL_EXP[self.level + 1] - self.exp
