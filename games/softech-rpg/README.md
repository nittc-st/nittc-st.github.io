# ソフテクRPG

[Pyxel](https://github.com/kitao/pyxel) で作った、ソフテク部が舞台の小さなRPGです。
サーバー室にわいたバグを倒してレベルを上げ、奥にいる親玉「デッドロック」を倒すとクリアです。
サイトでは `src/games.html` から、書き出したHTML（`src/games/softech-rpg.html`）を iframe で埋め込んでいます。

## 操作

| キー | 内容 |
| --- | --- |
| 矢印キー | 移動・カーソル移動 |
| Z / Space / Enter | 話す・調べる・決定 |
| X | ステータス・戻る |

## 手元で遊ぶ

```sh
pip install pyxel
python main.py
```

## サイト用のHTMLを書き出す

ゲームを変更したら、次のコマンドで `assets/font.bdf` と `src/games/softech-rpg.html` を作り直してコミットしてください。

```sh
./build.sh
```

## 構成

| ファイル | 内容 |
| --- | --- |
| `main.py` | タイトル・マップ・バトル・エンディングの切りかえ |
| `world.py` | マップの移動、会話、調べる、エンカウント |
| `battle.py` | ターン制バトル |
| `data.py` | マップ、敵、スキル、どうぐ、必要けいけんち |
| `player.py` | プレイヤーのステータスとレベルアップ |
| `sprites.py` | 人物・マップ・バグの描画（画像ファイルは使わず図形で描いている） |
| `ui.py` | フォント、効果音・BGM、メッセージウィンドウ |
| `subset_font.py` | `fonts/` のフォントから、ゲームで使う文字だけを `assets/font.bdf` に抜き出す |

セリフは `ui.Script` に `say()` で積みます。新しい文字を使ったら `build.sh`（または `python subset_font.py`）でフォントを作り直してください。
足りない文字があると、`subset_font.py` がその文字を表示して失敗します。

## フォント

`fonts/misaki_gothic_2nd.bdf` は、門真 なむ さんの [美咲フォント](https://littlelimit.net/misaki.htm)（8×8ドット、美咲ゴシック第2、2021-05-05版）です。
ライセンスは同じフォルダの `fonts/misaki.txt` のとおりで、改変・再配布を含めて自由に使えます。
`assets/font.bdf` は、そこからゲームで使う文字だけを抜き出したものです。
