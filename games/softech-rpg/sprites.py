import pyxel

DOWN, UP, LEFT, RIGHT = range(4)
DIR_VEC = {DOWN: (0, 1), UP: (0, -1), LEFT: (-1, 0), RIGHT: (1, 0)}


def person(x, y, d, hair, shirt, step=0, skin=15):
    """16x16 の人物を描く。step は歩きの足の位置(0/1)。"""
    pyxel.elli(x + 3, y + 13, 10, 4, 13)
    pyxel.rect(x + 4, y + 1, 8, 7, skin)
    pyxel.rect(x + 4, y, 8, 2, hair)
    if d == UP:
        pyxel.rect(x + 4, y + 1, 8, 6, hair)
    elif d == DOWN:
        pyxel.pset(x + 4, y + 2, hair)
        pyxel.pset(x + 11, y + 2, hair)
        pyxel.pset(x + 6, y + 4, 0)
        pyxel.pset(x + 9, y + 4, 0)
    elif d == LEFT:
        pyxel.rect(x + 9, y + 1, 3, 5, hair)
        pyxel.pset(x + 5, y + 4, 0)
    else:
        pyxel.rect(x + 4, y + 1, 3, 5, hair)
        pyxel.pset(x + 10, y + 4, 0)
    pyxel.rect(x + 3, y + 8, 10, 5, shirt)
    pyxel.rect(x + 3, y + 12, 10, 1, 1)
    if step:
        pyxel.rect(x + 5, y + 13, 2, 2, 1)
        pyxel.rect(x + 9, y + 13, 2, 3, 1)
    else:
        pyxel.rect(x + 5, y + 13, 2, 3, 1)
        pyxel.rect(x + 9, y + 13, 2, 2, 1)


def tile(ch, x, y, tx, ty):
    f = pyxel.frame_count
    if ch == "#":
        pyxel.rect(x, y, 16, 16, 1)
        pyxel.rect(x, y + 12, 16, 4, 5)
        pyxel.line(x, y + 12, x + 15, y + 12, 13)
    elif ch == ",":
        pyxel.rect(x, y, 16, 16, 1)
        pyxel.rectb(x, y, 16, 16, 5)
        if (tx * 7 + ty * 3) % 5 == 0:
            pyxel.line(x + 2, y + 8, x + 13, y + 8, 3)
    elif ch == "S":
        pyxel.rect(x, y, 16, 16, 1)
        pyxel.rect(x + 1, y, 14, 15, 0)
        for i in range(3):
            pyxel.rect(x + 3, y + 2 + i * 4, 10, 2, 5)
            on = (f // 10 + tx * 3 + ty * 5 + i) % 7
            pyxel.pset(x + 11, y + 2 + i * 4, 11 if on < 4 else (8 if on == 6 else 3))
    else:
        pyxel.rect(x, y, 16, 16, 15)
        pyxel.line(x, y + 15, x + 15, y + 15, 14)
        pyxel.line(x + 15, y, x + 15, y + 15, 14)
        if ch == "P":
            pyxel.rect(x, y + 6, 16, 10, 4)
            pyxel.rect(x + 3, y + 1, 10, 8, 13)
            pyxel.rect(x + 4, y + 2, 8, 6, 0)
            for i in range(3):
                if (f // 20 + tx + i) % 4:
                    pyxel.line(x + 5, y + 3 + i * 2, x + 6 + (tx * 3 + i * 5) % 5, y + 3 + i * 2, 11)
            pyxel.rect(x + 7, y + 9, 2, 2, 13)
        elif ch == "T":
            pyxel.rect(x, y + 3, 16, 12, 4)
            pyxel.line(x, y + 3, x + 15, y + 3, 9)
            if (tx + ty) % 2:
                pyxel.rect(x + 4, y + 6, 8, 5, 13)
                pyxel.rect(x + 5, y + 7, 6, 3, 6)
        elif ch == "B":
            pyxel.rect(x, y, 16, 16, 4)
            for row in range(2):
                for i in range(6):
                    col = (8, 12, 11, 10, 14, 6)[(i + tx + row * 2) % 6]
                    pyxel.rect(x + 1 + i * 2 + (i > 2), y + 1 + row * 7, 2, 6, col)
        elif ch == "V":
            pyxel.rect(x + 1, y, 14, 16, 8)
            pyxel.rect(x + 3, y + 2, 10, 6, 7)
            for i in range(3):
                pyxel.rect(x + 4 + i * 3, y + 3, 2, 4, (12, 10, 11)[i])
            pyxel.rect(x + 4, y + 11, 8, 3, 0)
            pyxel.pset(x + 12, y + 9, 10 if f // 20 % 2 else 9)
        elif ch == "L":
            pyxel.rect(x + 1, y, 14, 16, 4)
            pyxel.rect(x + 3, y + 2, 10, 12, 9)
            pyxel.pset(x + 11, y + 8, 10)


def boss_mini(x, y):
    bob = pyxel.sin(pyxel.frame_count * 4) * 1.5
    pyxel.circb(x + 8, y + 5 + bob, 5, 13)
    pyxel.circb(x + 8, y + 5 + bob, 4, 13)
    pyxel.rect(x + 2, y + 6 + bob, 12, 9, 2)
    pyxel.pset(x + 5, y + 9 + bob, 8)
    pyxel.pset(x + 10, y + 9 + bob, 8)
    pyxel.rect(x + 7, y + 11 + bob, 2, 3, 0)


def monster(shape, col, cx, cy):
    """バトル画面のバグを (cx, cy) を中心に描く。"""
    f = pyxel.frame_count
    cy += pyxel.sin(f * 3) * 2
    if shape == "bug":
        for i in range(3):
            ly = cy - 4 + i * 8
            kick = 3 if (f // 8 + i) % 2 else 0
            pyxel.line(cx - 12, ly, cx - 24, ly + 4 - kick, 0 if col != 0 else 5)
            pyxel.line(cx + 12, ly, cx + 24, ly + 4 - kick, 0 if col != 0 else 5)
        pyxel.elli(cx - 14, cy - 12, 28, 30, col)
        pyxel.line(cx, cy - 10, cx, cy + 16, 1)
        pyxel.circ(cx, cy - 16, 8, 1)
        pyxel.line(cx - 4, cy - 22, cx - 10, cy - 32, 1)
        pyxel.line(cx + 4, cy - 22, cx + 10, cy - 32, 1)
        pyxel.circ(cx - 3, cy - 17, 2, 7)
        pyxel.circ(cx + 3, cy - 17, 2, 7)
        pyxel.pset(cx - 3, cy - 17, 8)
        pyxel.pset(cx + 3, cy - 17, 8)
    elif shape == "ghost":
        pyxel.circ(cx, cy - 6, 16, col)
        pyxel.rect(cx - 16, cy - 6, 33, 18, col)
        for i in range(4):
            off = (f // 6 + i) % 2 * 3
            pyxel.tri(cx - 16 + i * 8, cy + 12, cx - 8 + i * 8, cy + 12, cx - 12 + i * 8, cy + 17 + off, col)
        pyxel.circ(cx - 6, cy - 6, 4, 7)
        pyxel.circ(cx + 6, cy - 6, 4, 7)
        pyxel.circ(cx - 5, cy - 5, 2, 0)
        pyxel.circ(cx + 7, cy - 5, 2, 0)
        pyxel.text(cx - 8, cy + 3, "null", 1)
    elif shape == "loop":
        angle = f * 6
        for r in range(17, 21):
            pyxel.circb(cx, cy, r, col)
        ax = cx + pyxel.cos(angle) * 19
        ay = cy + pyxel.sin(angle) * 19
        pyxel.circ(ax, ay, 5, 7)
        pyxel.circ(cx, cy, 10, 5)
        pyxel.circ(cx - 4, cy - 2, 3, 7)
        pyxel.circ(cx + 4, cy - 2, 3, 7)
        pyxel.pset(cx - 4 + pyxel.cos(angle) * 1.5, cy - 2 + pyxel.sin(angle) * 1.5, 0)
        pyxel.pset(cx + 4 + pyxel.cos(angle) * 1.5, cy - 2 + pyxel.sin(angle) * 1.5, 0)
    elif shape == "blob":
        drip = f // 4 % 20
        pyxel.circ(cx, cy + 4, 18, col)
        pyxel.tri(cx - 14, cy - 6, cx + 14, cy - 6, cx, cy - 28, col)
        pyxel.circ(cx - 8, cy - 4, 4, 7)
        pyxel.circ(cx + 8, cy - 4, 4, 7)
        pyxel.circ(cx - 8, cy - 3, 2, 0)
        pyxel.circ(cx + 8, cy - 3, 2, 0)
        pyxel.circ(cx + 12, cy + 20 + drip, 2, col)
        pyxel.circ(cx - 12, cy + 22 + (drip + 9) % 20, 2, col)
        pyxel.text(cx - 10, cy + 8, "0xFF", 2)
    elif shape == "glitch":
        for i in range(8):
            shift = ((f // 3 + i * 5) % 7 - 3) * 2
            c = col if i % 3 else (7 if f // 5 % 2 else 12)
            pyxel.rect(cx - 18 + shift, cy - 22 + i * 5, 36, 5, c)
        pyxel.rect(cx - 10, cy - 10, 6, 6, 0)
        pyxel.rect(cx + 4, cy - 10, 6, 6, 0)
        pyxel.pset(cx - 8, cy - 8, 7)
        pyxel.pset(cx + 6, cy - 8, 7)
        pyxel.text(cx - 14, cy + 4, "SIGSEGV", 7)
    elif shape == "lock":
        for r in range(16, 22):
            pyxel.circb(cx, cy - 18, r, 13)
        pyxel.rect(cx - 30, cy - 18, 61, 44, col)
        pyxel.rectb(cx - 30, cy - 18, 61, 44, 14)
        for i in range(4):
            pyxel.line(cx - 28, cy - 10 + i * 10, cx + 28, cy - 10 + i * 10, 14 if i % 2 else 2)
        pyxel.tri(cx - 20, cy - 10, cx - 6, cy - 4, cx - 20, cy - 2, 8)
        pyxel.tri(cx + 20, cy - 10, cx + 6, cy - 4, cx + 20, cy - 2, 8)
        pyxel.circ(cx, cy + 10, 5, 0)
        pyxel.rect(cx - 2, cy + 12, 5, 9, 0)
