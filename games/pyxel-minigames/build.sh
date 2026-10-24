#!/bin/sh
# Pyxelのミニゲーム集をHTMLに書き出し、src/games/minigames.html に配置する
set -eu

here=$(cd "$(dirname "$0")" && pwd)
out="$here/../../src/games"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

mkdir -p "$work/minigames"
(cd "$here" && cp -r common.py main.py minigames "$work/minigames/")
find "$work" -name __pycache__ -exec rm -rf {} +

cd "$work"
pyxel package minigames minigames/main.py
pyxel app2html minigames.pyxapp

mkdir -p "$out"
cp minigames.html "$out/minigames.html"
echo "wrote $out/minigames.html"
