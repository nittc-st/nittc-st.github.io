# Pyxel ミニゲーム集

[Pyxel](https://github.com/kitao/pyxel) で作ったミニゲーム12本と、それらを選ぶランチャーです。
サイトでは `src/games.html` から、書き出したHTML（`src/games/minigames.html`）を iframe で埋め込んでいます。

## 手元で遊ぶ

```sh
pip install pyxel
python main.py          # ランチャーから選ぶ
python main.py tetris   # ゲームを直接起動する
```

## サイト用のHTMLを書き出す

ゲームを変更したら、次のコマンドで `src/games/minigames.html` を作り直してコミットしてください。

```sh
./build.sh
```

## 構成

| ファイル | 内容 |
| --- | --- |
| `main.py` | ランチャー（メニュー・一時停止・リトライ・ベストスコア） |
| `common.py` | 画面サイズ・効果音・`Game` 基底クラス |
| `minigames/*.py` | 各ゲーム。`Game` を継承して `reset` / `update` / `draw` を実装する |

新しいゲームを追加するときは、`minigames/` にクラスを作り、`main.py` の `GAMES` に加えます。
