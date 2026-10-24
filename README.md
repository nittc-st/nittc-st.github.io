# nittc-st.github.io

[ソフテク公式サイト](https://nittc-st.github.io)

- [このサイトの仕様はこちら(ComingSoon)]()

# 記事・資料の投稿ガイド

知恵袋及び資料への投稿は、次の流れで行います。

**ブランチを切る → Markdownを書く → PRで内容を確認する → マージして公開する**

`main`へ直接pushせず、Pull Request（PR）で誰かにレビューしてもらってから公開してください。

## 1. ブランチを切る

リポジトリを手元に用意し、作業中の変更がない状態で、最新の`main`から投稿用ブランチを作成します。

```sh
git switch main
git pull --ff-only origin main
git switch -c blog/git-basic
```

ブランチ名は、投稿先に合わせて次の形式にします。

| 投稿の種類 | ブランチ名 | 例 |
| --- | --- | --- |
| ソフテク知恵袋 | `blog/<title>` | `blog/git-basic` |
| 資料置き場 | `doc/<title>` | `doc/protocol` |

`<title>`は表示タイトルではなく、Markdownのファイル名から拡張子を除いた名前（slug）に合わせます。公開済みの記事を修正する場合も、同じ命名規則で新しいブランチを作成します。

## 2. Markdownを書く

### 投稿先とファイル名

| 投稿の種類 | 配置先 |
| --- | --- |
| ソフテク知恵袋 | `content/blog/` |
| 資料置き場 | `content/document/` |

それぞれのディレクトリ直下に`.md`ファイルを作成します。例えば、Gitの記事なら`content/blog/git-basic.md`です。

ファイル名には文字・数字・`-`・`_`を使用できます。拡張子を除いた名前が記事のURLに使われる**slug**になります。日本語の表示タイトルとは別に、内容が分かる名前を付けてください。

例：`git-basic.md` → `src/blog.html?slug=git-basic`

公開後にファイル名を変更するとURLも変わるため、注意してください。

### Front Matterと本文

ファイルの先頭に、`---`で囲んだ記事情報（Front Matter）をYAML形式で記述します。その下にMarkdownで本文を書きます。

```md
---
title: Gitの基本操作
description: Gitの基本的な操作方法を解説します。
date: 2026-10-25
tags:
  - Git
  - 初心者向け
draft: false
---

## Gitとは

Gitは分散型バージョン管理システムです。

### 変更を記録する

ここに操作方法を記述します。
```

| 項目 | 必須 | 書き方 |
| --- | --- | --- |
| `title` | 必須 | 記事のタイトル。空でない文字列を指定します。 |
| `description` | 任意 | 一覧に表示する短い概要です。 |
| `date` | 任意 | 公開日・更新日を`YYYY-MM-DD`形式で指定します。 |
| `tags` | 任意 | タグの配列です。上の例のほか、`tags: [Git, 初心者向け]`とも書けます。 |
| `draft` | 任意 | 下書きは`true`、公開対象は`false`です。省略時は`false`になります。 |

- `draft`は文字列ではなく真偽値です。`"false"`のように引用符で囲まないでください。
- `title`などに同じ項目を重複して書いたり、存在しない日付を指定したりするとビルドエラーになります。
- タイトルにコロンなどのYAML記号を含む場合は、`title: "Git: 基本操作"`のように引用符で囲んでください。
- `date`の新しい記事から一覧に並びます。日付なしの記事は末尾に表示されます。
- 記事タイトルは`title`から表示されるので、本文の見出しは`##`から始められます。見出しからアウトラインが自動生成されます。
- 本文中の生HTMLは無効です。基本的なMarkdown記法を使ってください。

### 画像・添付ファイル

記事専用の画像は、投稿先の`img/`内に、slugと同じ名前のフォルダーを作って配置します。

```text
content/
  blog/
    git-basic.md
    img/
      git-basic/
        screenshot.png
```

`git-basic.md`からは次のように参照します。画像には内容を説明する代替テキストを付けてください。

```md
![Gitの変更履歴画面](img/git-basic/screenshot.png)
```

資料側も同様に、`content/document/img/<slug>/`へ配置します。ルートの`img/`はロゴなどサイト共通画像用なので、記事専用画像は置かないでください。

PDF等は、例えば`content/blog/assets/git-basic/guide.pdf`に配置し、次のようにリンクします。

```md
[補足資料（PDF）](assets/git-basic/guide.pdf)
```

画像・添付ファイルの相対パスはMarkdownファイルを基準にします。別の記事にも`[関連記事](other-article.md)`のようにリンクできます。ファイル名は実在するものを指定してください。

> **公開してはいけない情報はコミットしないでください。**
> `draft: true`のMarkdownはサイトへの公開対象から外れますが、画像・添付ファイルは公開対象です。また、下書きでもGitHubリポジトリ自体には内容が残ります。

### コードを書く

コードブロックに言語を指定すると、シンタックスハイライトが付きます。

````md
```js
const message = 'こんにちは';
console.log(message);
```
````

`js`、`ts`、`py`、`sh`、`html`、`css`、`json`、`yaml`、`http`などが使えます。言語未指定・未対応の場合は通常のコードとして表示されます。

### 手元で表示を確認する

Node.js 22以上で、次を実行します。WindowsのPowerShellでも同じコマンドを使えます。

```sh
npm ci
npm run dev
```

記事をビルドした後、<http://localhost:8000/>で確認用サーバーを起動します。初回は`npx`で`http-server@14.1.1`を取得するため、ネット接続が必要です。停止するときはCtrl+Cを押してください。

サーバーを別のツールで起動する場合は、先に`npm run build`を実行してください。例えば、次のどちらかを使えます。

```sh
# Node.jsを使う場合（初回はサーバー用パッケージを取得します）
npx http-server@14.1.1 dist -a 127.0.0.1 -p 8000 -c-1
```

```sh
# Python 3を使う場合
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

VS CodeのLive Serverなどを使っても構いません。ソースではなく、ビルド済みの`dist/`を配信してください。

上記のコマンド例では、次のURLから確認できます。別のツールを使う場合は、そのサーバーのURL・ポート番号に合わせてください。

- 知恵袋：<http://localhost:8000/src/blog.html>
- 資料置き場：<http://localhost:8000/src/document.html>

HTMLファイルの直接起動（`file://`）ではなく、HTTP経由で開いてください。自動ビルド・自動リロードは行わないため、記事や画像を変更したら、別のターミナルで再度`npm run build`を実行してブラウザを再読み込みします。

`draft: true`の記事はプレビューにも表示されません。表示確認のために`false`へ変更した場合は、PRへ出す前に意図した値か確認してください。生成物の`dist/`はコミットしません。

## 3. PRを出し、内容を確認する

記事と必要な画像・添付ファイルをコミットし、投稿用ブランチをpushします。以下は記事だけを追加する例です。画像・添付がある場合は、そのファイルも個別に`git add`してください。

```sh
git status
git add content/blog/git-basic.md
git commit -m "Gitの基本操作の記事を追加"
git push -u origin blog/git-basic
```

GitHubで**Compare & pull request**を開き、マージ先（base）を`main`、投稿元（compare）を自分のブランチにしてPRを作成します。

PRには、記事の目的・想定読者・追加や変更した内容・確認方法を記載し、他のメンバーにレビューを依頼してください。投稿者とレビュー担当者は、次の観点で内容を確認します。

指摘があれば同じブランチで修正し、コミット・pushします。PRに変更が反映されるので、再確認を依頼してください。

## 4. マージして公開する

レビュー担当者と内容に問題がないことを確認したら、権限のあるメンバーがPRを`main`へマージします。

マージ後、GitHub Actionsが記事一覧の生成とGitHub Pagesへのデプロイを実行します。完了したら[公開サイト](https://nittc-st.github.io)で記事・画像・リンクを確認してください。

公開されない場合は、次を確認します。

- PRが`main`へマージされているか
- `draft: true`のままになっていないか
- GitHubの**Actions**でデプロイが成功しているか（反映まで少し時間がかかります）

ビルドが失敗している場合は、ログに表示されたファイルやFront Matterを確認し、修正用ブランチとPRで対応してください。
