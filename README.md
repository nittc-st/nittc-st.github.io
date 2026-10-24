# nittc-st.github.io

```https://nittc-st.github.io```

## ディレクトリ構成
- `components/`
    - footerとheader(navbar)要素を配置しています．
- `img/`
    - 画像ファイルの配置場所です．
- `js/`
    - 各htmlファイルでfooterとheader(navbar)要素を呼び出すスクリプトです．
- `src/`
    - `index.html`以外のhtmlファイルを配置しています．

## Markdownコンテンツの投稿

記事（ソフテク知恵袋）は `content/blog/`、資料は `content/document/` の直下に `.md` ファイルを作成します。両ページは同じJavaScriptとUIを使い、`data-content-type` で種別だけを切り替えます。

```md
---
title: Gitの基本操作
description: Gitの基本的な操作方法を解説します。
date: 2026-10-24
tags:
  - Git
  - 初心者向け
draft: false
---

## Gitとは

ここから本文を記述します。
```

- `title` は必須の空でない文字列です。
- `description` は任意の文字列、`date` は任意の実在する日付（`YYYY-MM-DD`）です。
- `tags` は文字列の配列、`draft` は真偽値です。省略時はそれぞれ空配列・`false` になります。
- YAML Front Matterはファイル先頭の `---` 行で開始します。YAMLの重複キーや不正な型はビルドエラーになります。
- slugは拡張子を除いたファイル名です。例: `git-basic.md` → `git-basic`。ファイル名には文字・数字・`-`・`_` を使用してください。日本語タイトルとは独立しています。
- 一覧は日付の降順、同日・日付なしはslug順です。日付なしは末尾に表示されます。
- 本文は `src/blog.html?slug=git-basic` のようなURLで表示します。ページ側でタイトルが表示されるため、本文の見出しは `##` から始められます。

### 画像・添付ファイル

画像は、サイト共通のものと記事専用のものを分けて配置します。記事専用画像は、種別ごとの `img/` 内で記事のslugごとにまとめます。

```text
img/                              # ロゴなど、サイト共通の画像
content/
  blog/
    git-basic.md
    img/
      git-basic/
        screenshot.png
  document/
    protocol.md
    img/
      protocol/
        diagram.png
```

例えば `content/document/protocol.md` から、その記事の画像を次のように参照します。

```md
![構成図](img/protocol/diagram.png)
```

画像を使う記事だけslug名のフォルダーを作成してください。上記の画像・ファイル名は配置例です。相対パスはMarkdownファイルを基準に解決され、記事専用画像もビルド時に同じ構成で `dist/` へコピーされます。

PDF等の添付ファイルは、例えば `content/document/assets/protocol/guide.pdf` に配置し、`[資料](assets/protocol/guide.pdf)` のようにリンクできます。別の記事への `[記事](git-basic.md)` や `[資料](../document/guide.md)` も使用できます（ファイル名は実際の投稿に合わせてください）。

`draft: true` のMarkdownは一覧・公開ファイルの両方から除外します。ただし、画像・添付ファイルは共有資産として公開されるため、下書き専用の秘密情報は配置しないでください。GitHubリポジトリ自体にコミットした情報の非公開化を保証する機能ではありません。

本文中の生HTMLは無効です。Markdown変換はブラウザ内で、バージョン固定したCDNのmarkdown-itを使用します。CDNへの接続が必要です。

### コードのシンタックスハイライト

コードブロックの開始行で言語を指定すると、自動で色分けされます。

````md
```js
const message = 'こんにちは';
console.log(message);
```
````

JavaScript（`js`）、TypeScript（`ts`）、Python（`py`）、シェル（`sh`）、HTML、CSS、JSON、YAML、HTTPなどに対応します。言語未指定・未対応の場合は色分けせず表示します。コード中のHTMLは実行されず、長い行はコードブロック内で横スクロールできます。

highlight.js 11.12.0とGitHub系の明るいテーマをバージョン固定のCDNから読み込みます。npm依存やブラウザ用のビルド処理は追加していません。

### 記事のアウトライン

記事タイトルと本文の見出し（`#`〜`######`）から、階層付きアウトラインを自動生成します。PCでは左側に追従表示し、スマートフォンでは本文上部の「アウトライン」ボタンで開閉できます。スクロール中の現在位置も強調されます。本文に見出しがない記事では表示しません。

見出しには日本語対応のIDが自動で付き、同名見出しは連番で区別します。アウトラインのリンク先URLを共有することで、記事内の見出しへ直接移動できます。見出し名を変更するとリンク先IDも変わります。

レイアウトは [mkilnの同梱CSS・アウトライン](https://github.com/sankaku789/mkiln/tree/main/internal/assets) を参考にし、Bootstrapのグリッド・Collapse・Navで構成しています。現在位置の判定はVanilla JavaScriptで行います。

## ローカル検証

Node.js 22以上を使用します。npm依存関係はFront Matter解析とテスト用で、ブラウザのビルドは不要です。

```sh
npm ci
npm test
npm run build
python3 -m http.server 8000 --directory dist
```

`http://localhost:8000/src/blog.html` と `http://localhost:8000/src/document.html` を開いて確認します。`file://` ではなくHTTPサーバーを使ってください。

`scripts/build-content.js` がYAMLの解析・検証を行い、既存サイトの静的ファイル、Front Matter除去済みMarkdown、画像・添付ファイル、各種別の `index.json` を `dist/` に生成します。`index.json` の手動編集は不要です。`dist/` は毎回再生成され、Gitの追跡対象外です。

## GitHub Pagesへのデプロイ

1. リポジトリの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に設定します。
2. Markdownと画像等をコミットし、`main` にpushします。
3. `.github/workflows/deploy.yml` が依存関係のインストール、テスト、生成、`dist/` のPagesデプロイを実行します。Actions画面から手動実行も可能です。

不正なメタデータがあるとファイル名付きのエラーで処理が停止し、デプロイしません。ビルド処理はMarkdownをHTMLに変換せず、ブラウザの `js/markdown.js` が描画を担当します。既存のnavbar・footerの読み込みは `js/common.js` のままです。
