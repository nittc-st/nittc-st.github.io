"""Pyxel に付属する日本語フォントから、ゲームで使う文字だけを抜き出して assets/font.bdf を作る。

元のフォントは 1MB ほどあり、そのままでは HTML に書き出したときに重くなるため。
セリフを変えたら build.sh(またはこのスクリプト)を実行し直すこと。
"""

import sys
from pathlib import Path

import pyxel

HERE = Path(__file__).resolve().parent
SOURCE = Path(pyxel.__file__).parent / "examples" / "assets" / "umplus_j10r.bdf"
OUTPUT = HERE / "assets" / "font.bdf"


def used_chars():
    chars = {chr(c) for c in range(0x20, 0x7F)} | {"　"}
    for path in HERE.glob("*.py"):
        if path.name != Path(__file__).name:
            chars |= set(path.read_text(encoding="utf-8"))
    return {c for c in chars if c >= " "}


def char_of(glyph):
    code = int(next(l for l in glyph if l.startswith("ENCODING")).split()[1])
    return chr(code) if code >= 0 else None


def main():
    chars = used_chars()
    lines = SOURCE.read_text(encoding="latin-1").splitlines()
    header, glyphs, current = [], [], None
    for line in lines:
        if line.startswith("STARTCHAR"):
            current = [line]
        elif current is not None:
            current.append(line)
            if line == "ENDCHAR":
                glyphs.append(current)
                current = None
        elif not line.startswith("ENDFONT"):
            header.append(line)

    kept = [g for g in glyphs if char_of(g) in chars]
    found = {char_of(g) for g in kept}
    missing = sorted(chars - found)

    header = [f"CHARS {len(kept)}" if l.startswith("CHARS ") else l for l in header]
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text("\n".join(header + [l for g in kept for l in g] + ["ENDFONT", ""]), encoding="latin-1")
    print(f"wrote {OUTPUT.name}: {len(kept)} glyphs")
    if missing:
        print("missing:", " ".join(f"{c}(U+{ord(c):04X})" for c in missing))
        sys.exit(1)


if __name__ == "__main__":
    main()
