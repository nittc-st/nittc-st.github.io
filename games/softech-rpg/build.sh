#!/bin/sh
# ソフテクRPGをHTMLに書き出し、src/games/softech-rpg.html に配置する
set -eu

here=$(cd "$(dirname "$0")" && pwd)
out="$here/../../src/games"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# セリフに使う文字だけのフォントを作り直す
python "$here/subset_font.py"

mkdir -p "$work/softech-rpg"
(cd "$here" && cp -r battle.py data.py main.py player.py sprites.py ui.py world.py assets "$work/softech-rpg/")
find "$work" -name __pycache__ -exec rm -rf {} +

cd "$work"
pyxel package softech-rpg softech-rpg/main.py
pyxel app2html softech-rpg.pyxapp

mkdir -p "$out"
cp softech-rpg.html "$out/softech-rpg.html"
echo "wrote $out/softech-rpg.html"
