# 404 Runner（Pyxel Web対応）

Python / Pyxelのゲーム本体です。サイトルートの`404.html`から、`game.html`をiframeで読み込みます。
`my_resource.pyxres`は変更していません。

## 起動（Windows推奨）

検証バージョンはPyxel **2.9.9**です。WindowsのPython環境でインストールして実行してください。

```powershell
python -m pip install pyxel==2.9.9
cd games/404-runner
pyxel run main.py
```

- Space：開始、ジャンプ／ゲームオーバー・リザルト画面では離したときに次へ
- ← / A、→ / D：左右移動
- ↑ / W：ジャンプ
- Enter：タイトルにリセット
- M：消音／音声オンの切り替え（初期状態は消音。リスタート時も選択を維持）

内部解像度は128×128、30fpsです。カウントダウンは3・2・1・STARTを各1秒表示します。
落下時は残機を1減らし、残機があれば1秒待機して点滅しながら復活します。
ランキングの読み書き・ハイスコア判定はありません。スコアは従来の`get_score()`で計算します。

## Web用HTMLの生成（PowerShell）

リポジトリのルートから実行します。

```powershell
python games/404-runner/build_web.py
npm run build
python -m http.server 8011 --bind 127.0.0.1 --directory dist
```

`http://localhost:8011/404.html`をブラウザで開き、ゲームの起動用画面をクリックします。
サーバーはCtrl+Cで停止します。Pythonの簡易サーバーでは、不明なURLから自動でこの404ページへは切り替わりません。

`build_web.py`は一時ディレクトリに`main.py`と`my_resource.pyxres`だけをコピーし、公式の`pyxel package`と`pyxel app2html`を実行します。
生成した`games/404-runner/game.html`も変更と一緒にコミットしてください。サイトのビルドはこのHTMLを`dist/`へコピーするため、ActionsにPyxelをインストールする必要はありません。
ゲーム本体やリソースを変更したら、必ずHTMLを再生成してください。

HTMLにはコードとリソースが内包されますが、Pyxel WebランタイムはCDNから取得するため、ネット接続が必要です。
`app2html`が標準で含めるタッチ端末用ゲームパッドは、今回独自に追加・調整していません。

公式手順：https://kitao.dev/pyxel/web-usage/

## 回帰テスト（画面を開かない）

リポジトリのルートから実行します。標準ライブラリのみで動作します。

```sh
python -B -m unittest discover -s games/404-runner -p "test_*.py" -v
```

カウントダウン・BGM呼び出し、復活待機・点滅・着地、残機0からリザルト・リスタート、待機中リセット、移動・ジャンプ・スクロール・衝突を検証します。
Pyxel APIをモックするため、実際の描画・キーボードイベント・音の聞こえ方はこのテストだけでは確認できません。
