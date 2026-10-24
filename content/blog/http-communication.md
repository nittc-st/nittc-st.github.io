---
title: 通信入門 ― プロトコル・HTTP・HTTPクライアント
description: 通信とプロトコルの基本、HTTP通信の仕組み、telnet・curl・Python3のRequestsを使ったHTTP通信の方法を解説し、演習課題をまとめます。
date: 2026-10-25
author: nagnagi
tags:
  - 通信
  - HTTP
  - Python
  - プロコン講習
draft: false
---

プロコン講習「通信1」の通信説明資料・HTTPクライアント説明資料・演習1・演習2を1つにまとめた記事です。

この記事の学習目標は次のとおりです。

- 身の回りに存在する通信について知る。
- コンピュータネットワークでよく利用されるHTTP通信について学習する。
- UNIXコマンドやPython3のライブラリを用いて、HTTP通信を行うことができる。

## 環境構築

この講習は、WSL上で行う。

この講習では、以下のパッケージが必要である。

- curl
- telnet
- python3
- python3-pip
- python3-requests

以下のコマンドでインストールせよ。

```sh
sudo apt update && sudo apt install curl telnet python3 python3-pip python3-requests
```

## 通信とは

そもそも通信（communication）とは、直接やりとりのできない人々や機器同士が、
何らかの道具を使って意思や情報を交換することをいう。

その中でも、電気信号を用いて、文字や数値、音声などのデータをやりとりする通信を、
電気通信（telecommunication）という。

### インターネットと通信

皆さんが当たり前に使っているDiscordやTeams、Googleなどの検索エンジンなど、
インターネットは、この電気通信を用いて情報のやりとりを行う。

また、テレビの放送や信号機の制御なども、もちろん通信が使われている。

ただし、通信が用いられるのは、インターネットや放送のような広い世界だけではない。

### コンピュータ内部の通信

実は、コンピュータ内部でも、たくさんの通信が行われている。
例えば、PowerPointのスライドを読み込むときを考えると、
そのスライドのデータをストレージ（記憶装置）から処理装置（CPU）に持っていき、
処理が完了したら、また処理装置（CPU）からストレージ（記憶装置）に返す。

また、PCで同時にたくさんのアプリケーションを起動したときに、
その間ではデータのやりとりが行われている。

さらに小さい世界を考えてみよう。
実は、処理装置（CPU）も、たくさんの部品からできている。
これらは相互にデータのやりとりが必要なので、通信が行われている。

このように、通信は広い世界だけでなく、非常に小さな世界でも行われているのである。

## プロトコル

ここまでの説明で、様々なところで通信が行われているということは理解できたと思う。

ここで、通信は様々な人種や言語、様々な種類の電気信号で行われる可能性がある。
もし、機器Aではモールス信号を送信し、機器Bでは地デジ信号を受信しようとすると、どうなるだろうか。

また、日本語でメールを送りたいが、メールのシステムが英語にしか対応していない場合、
どう通信したら良いだろうか。

これらを取り決めるのが、プロトコルである。

### 主要なプロトコルとその役割

プロトコルは、通信を行う上で、手順や決まり事、ルールを定めたものを指す。

例えば、高専の出願（略）だと、

- 学生は、個人調査票（中学校の校長が作成した、成績を証明するもの）を中学校に提出する。
- 学校は、上を封筒に入れ、教務係に簡易書留で郵送する。
- 志願者が複数名いる場合は、個人毎の出願書類をクリップでまとめる。

これが、高専出願の「プロトコル」である。

これと同様に、インターネットにもたくさんのプロトコルが存在する。
その中でも、特によく用いるものを下に示す。

| プロトコル | 役割 |
| --- | --- |
| HTTP/HTTPS | WEBページや文字データを送受信する |
| SSH | PCに遠隔でログインする |
| FTP | ファイルの送受信を行う |
| SMTP | メールを送信する |
| POP3/IMAP | メールを受信する |
| DHCP | 通信に必要な情報を自動で設定する |

普段使っているアプリケーションも、
通信したいデータに応じ、これらのプロトコルを適切に選択することで、
インターネットを利用できている。

## クライアントサーバシステム

インターネットの通信において、多くの通信はクライアントサーバ型により提供される。

クライアントサーバシステムは、私たちが使っているPCやスマートフォンなどの端末であるクライアントと、
（HTTPであれば）WEBサイトやログイン情報などを送受信・管理するサーバーにより構成される。

このシステムにおいては、まずクライアントがリクエスト（要求）を送信し、
サーバーがそれに応じた処理を実行して、レスポンス（応答）を返信する。

このように、クライアントサーバシステムでは必ずクライアント側から通信を開始するため、
サーバーから一方的にデータが送られてくることはない。

## HTTP通信

インターネットのプロトコルの中でも、特に多く用いるのが、HTTP（HyperText Transfer Protocol）である。
HTTPは、もともとWEBページ（ハイパーテキスト）を送受信するためのプロトコルであるが、
画像やJSONなど様々なデータを送受信できる、汎用的なプロトコルである。

### HTTP通信の形式

HTTP/1.1の通信は、テキスト形式のメッセージで行われる。
クライアントが送信するメッセージをHTTPリクエスト、
サーバーが返信するメッセージをHTTPレスポンスという。

以下に、そのサンプルを示す。

**HTTPリクエスト（送信）**

```http
GET / HTTP/1.1
Host: example.com
User-Agent: curl/8.18.0
Accept: */*
```

**HTTPレスポンス（受信）**

```http
HTTP/1.1 200 OK
Date: Fri, 27 Feb 2026 15:43:13 GMT
Content-Type: text/html
Transfer-Encoding: chunked
Connection: keep-alive
CF-RAY: 9d48cbec5e257b69-NRT
Last-Modified: Wed, 25 Feb 2026 07:22:28 GMT
Allow: GET, HEAD
Accept-Ranges: bytes
Age: 12952
cf-cache-status: HIT
Server: cloudflare

<!doctype html><html lang="en"><head><title>Example Domain</title>
(省略)
```

これらが何を表すのかについて、説明する。

### HTTPメッセージの構成

HTTPリクエスト・HTTPレスポンスは、以下の構成をもつ。

**HTTPリクエスト（送信）**

```text
<メソッド> <場所(Path)> <バージョン>
<キー>: <値>

<リクエストボディ(ペイロード)>
```

**HTTPレスポンス（受信）**

```text
<バージョン> <ステータスコード> <メッセージ>
<キー>: <値>

<レスポンスボディ(ペイロード)>
```

#### ヘッダ

送信、受信のどちらにおいても、空行より上にある、ペイロードを含まない部分をヘッダという。
ヘッダは、どんなクライアント、サーバーがどんな通信を行おうとしているのか、という情報を示す。

また、ヘッダのキー、値は、情報の種類とその内容を示す。
例えば、キーが`Date`、値が`Fri, 27 Feb 2026 15:43:13 GMT`だとすると、
通信が行われた日付が`2026年2月27日(金) 世界時15:43:13`であることを示す。

ペイロードは、実際に送信・受信する本体のことを示す。

通常、WEBサイトにアクセスすると、
リクエストボディはなし、レスポンスボディはWEBページになる。

#### ステータスコード

返却された値について、正常であるか、異常であるか、
またその中でもどんな状態かを示す3桁の値を、ステータスコードという。

ステータスコードは、百の位で大まかな状態、下2桁でその詳細を表す。
以下に、それぞれの値に対する、その状態（意味）を示す。

| ステータスコード | 状態 | 例 |
| --- | --- | --- |
| 2xx | 正常 | 200 OK |
| 3xx | リダイレクト（別の場所への転送） | 301 Moved Permanently |
| 4xx | ユーザーのリクエストが不正 | 404 Not Found |
| 5xx | サーバーのエラー | 500 Internal Server Error |

### HTTPリクエストのメソッド

続いて、メソッドについて説明する。

HTTPリクエストにおいては、主に以下のメソッドが存在する。

- HEAD
- GET
- POST

それぞれのメソッドについて、役割と形式を説明する。

#### HEADメソッド

HEADメソッドでは、サーバーにヘッダのみを要求する。
このメソッドは、ある場所（Path）にアクセスしたときに、どのようなデータが得られるのかを確認するために使う。
このリクエストでは、リクエストボディを付加しない。
アクセス先によっては、リクエストボディを付加するとエラーが返ってくることもある。

**例**

```http
HEAD / HTTP/1.1
Host: example.com
```

例えば、AというPathにHEADメソッドを実行したとき、ヘッダに

- `Allow: GET, HEAD`

という記述があったとしよう。
この場合は、AにGETメソッドを送信することができるということを表す。
このように、パスに応じたデータの内容が不明確である場合に用いる。

#### GETメソッド

GETメソッドでは、サーバーにヘッダ及びレスポンスボディ（ペイロード）を要求する。
普通、サーバーにWEBサイトを要求するときは、このメソッドを用いる。
このリクエストでは、リクエストボディを付加しない。
アクセス先によっては、リクエストボディを付加するとエラーが返ってくることもある。

**例**

```http
GET / HTTP/1.1
Host: example.com
```

上で示したサンプルより、要求したパスのHTMLファイルが返却されていることが分かるだろう。
なお、画像などのファイルを要求した場合も、ヘッダはテキストで返却され、
レスポンスボディにはそのファイルのデータが入る。
レスポンスボディが何のデータであるかは、ヘッダの`Content-Type`で示される。

GETメソッドは、原則としてサーバーが持っている情報の書き換えを行わない。

#### POSTメソッド

POSTメソッドは、サーバーに対してリクエストボディを送るときに用いる。
例えば、サーバーに何らかのデータを登録するときは、
GETではなくPOSTを用いる必要がある。

**例**

```http
POST /register HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 29

{ "user": "you", "age": 255 }
```

リクエストボディを送るときは、ヘッダの`Content-Type`でボディの形式を、
`Content-Length`でボディの長さ（バイト数）を示す。

POSTメソッドでは、サーバーが持っている情報の書き換えを行う場合がある。
つまり、クライアントが送信したデータがサーバーに反映されることがある。

### URLとパラメータ

ブラウザなどでWEBサイトにアクセスするときは、URLを用いてホストと場所を指示する。
以下に、URLの例を示す。

```text
https://www.example.com/example/search?q=aaa&page=2
```

URLは、以下の構造をもつ文字列である。

```text
<プロトコル>://<ドメイン>/<場所(Path)>?<キー>=<値>&<キー>=<値>
```

それぞれの要素について説明する。

**プロトコル（スキーム）**

以下のような文字列を用いて、通信の種類を示す。

- http
- https
- ftp
- file
- ssh

**ドメイン（ホスト）**

どのサーバーと通信するかを示す文字列である。
例えば、上のURLでは`www.example.com`がドメインである。
ドメイン（厳密にはFQDN）は、ドット区切りで要素を表す。

今回においてはその仕組みは重要でないので、省略する。

**場所（Path）**

サーバー内部のファイルの位置を示す。

基本的にはローカルのパスと同様であるが、
ディレクトリを指定すると、自動でファイルが提供される場合がある。
例えば、

```text
https://www.example.com/
```

にアクセスすると、実際には、

```text
https://www.example.com/index.html
```

を取得している、というような場合がある。この設定はサーバーによって異なるが、
慣習的に`index.html`が適用されることが多い。

**URLパラメータ**

`?`記号以降に記述されるキー、値の組をURLパラメータ（または単にパラメータ）という。

これらは引数のようなものであり、例えば検索文字列や結果の数などを設定する。
上のURLでは、`q`が`aaa`、`page`が`2`である。

### 暗号化通信

インターネットには、様々な脅威が無数に存在している。
暗号化されていないデータは容易に盗聴され、不正に利用される。

これを防ぐ仕組みとして、暗号化が存在する。
暗号化は、以下のような仕組みを指す。

1. クライアントは鍵を作成し、安全な方法でサーバーに渡す。
2. クライアントは鍵を使ってデータを暗号（一見無意味な文字列）に変換し送信する。
3. サーバーは鍵を使って暗号を解読し、クライアントが求めているデータを用意する。
4. サーバーはそのデータを鍵を使って暗号に変換し送信する。
5. クライアントは鍵を使って暗号を解読し、データを得る。

HTTPSというプロトコルでは、通信に暗号化が行われる。（暗号化通信）
一方、HTTPでは暗号化が行われないため、通信内容がそのまま第三者に見えてしまう。

HTTPSでは、URLのパスやパラメータも暗号化される。
ただし、どのドメインと通信しているかは、第三者から分かる場合がある。
また、URLはブラウザの履歴やサーバーのアクセスログに記録され、画面にも表示される。

そのため、URLパラメータでパスワードや個人情報を渡してはいけない。
（これは、開発者側が注意することである。）

## HTTPクライアント

ここからは、実際にプログラムでHTTP通信を行う方法について学習する。
これを見ながら、後述の[演習](#演習)に取り組むこと。

HTTPクライアントとは、HTTP通信を行うクライアントアプリケーションのことを指す。
（厳密な定義があるわけではないが、ここでは上のように定義する。）

この講習では、以下の2つの方法について学習する。

- UNIXコマンドを用いる方法
- Python3のライブラリを用いる方法

## UNIXコマンドを用いる方法

### man

UNIXコマンドにおいては、
manコマンドを用いることでそのコマンドのマニュアルを閲覧することができる。

**文法**

```sh
man <コマンド>
```

**コマンド例**

```sh
man ls
```

コマンドの使用方法が分からない場合は、適宜manコマンドを用いて調べよ。

### telnet

telnetは、Linuxのターミナルで使用可能な、
指定したホストに接続するコマンドである。

**文法**

```sh
telnet <ホスト> 80
```

`80`は、HTTPで用いるポート番号である。

**コマンド例**

```sh
telnet example.com 80
```

このコマンドを実行すると、ホストに接続を試みる。
接続が成功すると、コネクションを確立し、HTTP通信ができる状態になる。

コネクションが確立されると、以下のようなメッセージが表示される。

```text
Trying 2606:4700::6812:1a78...
Connected to www.example.com.
Escape character is '^]'.
```

この状態で、HTTPリクエストを入力することで、サーバーとHTTP通信を行うことができる。

**入力例**

```http
GET / HTTP/1.1
Host: example.com
(改行)
```

**出力例**

```http
HTTP/1.1 200 OK
Date: Fri, 27 Feb 2026 15:43:13 GMT
Content-Type: text/html
Transfer-Encoding: chunked
Connection: keep-alive
CF-RAY: 9d48cbec5e257b69-NRT
Last-Modified: Wed, 25 Feb 2026 07:22:28 GMT
Allow: GET, HEAD
... (略)
```

ステータスコードが200番台でない場合は、何らかのエラーがあることを意味する。
[ステータスコード](#ステータスコード)の節を参考にせよ。

なお、HTTPリクエストを手で入力していると、数秒でコネクションが遮断されるため、
コピー&ペーストにより入力すること。

telnetコマンドは標準入力を読み取るため、それをパイプさせてもよい。
ただし、パイプの使用方法については各自で調査せよ。

### curl

curlは、Linuxのターミナルで使用可能な、
HTTPリクエストを送信するためのコマンドである。

**文法**

```sh
curl -L -v <URL>
```

`-L`はリダイレクトされた場合に転送先を追いかけるオプション、
`-v`は通信の詳細を表示するオプションである。

**コマンド例**

```sh
curl -L -v http://example.com
```

このコマンドを使用すると、
自動でGETリクエストを送信し、受信を待機する。

標準出力には、
接続情報、送信されたGETリクエスト、返信されたヘッダ、
レスポンスボディ（ペイロード）が表示される。

**出力例**

```text
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed

  0      0   0      0   0      0      0      0                              0* Host example.com:80 was resolved.
* IPv6: 2606:4700::6812:1a78, 2606:4700::6812:1b78
* IPv4: 104.18.26.120, 104.18.27.120
*   Trying [2606:4700::6812:1a78]:80...
* Established connection to example.com (2606:4700::6812:1a78 port 80) from 240a:61:129c:cbde:9758:61c5:d048:44ae port 45664
* using HTTP/1.x
> GET / HTTP/1.1
> Host: example.com
> User-Agent: curl/8.18.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200 OK
< Date: Sat, 28 Feb 2026 10:10:56 GMT
< Content-Type: text/html
< Transfer-Encoding: chunked
< Connection: keep-alive
< CF-RAY: 9d4f228ede8ed76c-NRT
< Last-Modified: Wed, 25 Feb 2026 07:22:28 GMT
< Allow: GET, HEAD
... (略)
```

`>`で始まる行が送信したHTTPリクエスト、`<`で始まる行が受信したHTTPレスポンスのヘッダである。

## Python3のライブラリを用いる方法

### JSONについて

HTTP通信において、データを送信するときによく用いる形式として、JSONがある。

**文法**

キー・値の組（オブジェクト、map）を定義するときは、波括弧を使用する。

```text
{
    <キー>: <値>,
    <キー>: <値>
}
```

配列（array）を定義するときは、角括弧を使用する。

```text
[
    <アイテム>,
    <アイテム>
]
```

キーに設定できるのは、文字列（string）のみである。
文字列は、`"`（ダブルクォート）で囲む。

値に設定できるのは、以下の6種類である。

- string（文字列）
- number（数値）
- boolean（`true`または`false`）
- null
- オブジェクト（map）
- 配列（array）

**例**

以下は、Free Dictionary APIで`HTTP`を検索したときのレスポンスボディである。

```json
{
  "word": "HTTP",
  "entries": [
    {
      "language": {
        "code": "en",
        "name": "English"
      },
      "partOfSpeech": "name",
      "pronunciations": [],
      "forms": [],
      "senses": [
        {
          "definition": "(Internet, networking) Initialism of Hypertext Transfer Protocol, the protocol used most commonly to transfer Web pages and accompanying data over the Internet.",
          "tags": [
            "Internet",
            "abbreviation",
            "alt of",
            "initialism"
          ],
          "examples": [],
          "quotes": [
            {
              "text": "The Hypertext Transfer Protocol (HTTP) is an application-level protocol with the lightness and speed necessary for distributed, collaborative, hypermedia information systems.",
              "reference": "1996 May, T. Berners-Lee, R. Fielding, H. Frystyk, “Hypertext Transfer Protocol – HTTP/1.0”, in RFC Editor, →ISSN, RFC 1945:"
            }
          ],
          "synonyms": [],
          "antonyms": [],
          "subsenses": []
        }
      ],
      "synonyms": [],
      "antonyms": []
    }
  ],
  "source": {
    "url": "https://en.wiktionary.org/wiki/HTTP",
    "license": {
      "name": "CC BY-SA 4.0",
      "url": "https://creativecommons.org/licenses/by-sa/4.0/"
    }
  }
}
```

Python3においては、JSONのオブジェクトはディクショナリ型、配列はリスト型として扱われる。

ディクショナリ型の変数`data`があるとき、
あるキーに値を代入するときは、以下のように記述する。

```py
data[<キー>] = <値>
```

あるキーの値を取得するときは、以下のように記述する。

```py
<変数> = data[<キー>]
```

リスト型の場合は、キーの代わりにインデックス（0から始まる番号）を指定する。

**例**

上のJSONを変数`res`に読み込んだとき、`HTTP`の意味は以下のように取得できる。

```py
definition = res["entries"][0]["senses"][0]["definition"]
```

### Requestsの使い方

Python3では、Requestsモジュール（ライブラリ）を用いてHTTP通信を行う。
ライブラリを使用するときは、ファイルの先頭に以下の記述を行う。

```py
import requests
```

続いて、HTTPリクエストの送信を行う関数を示す。

#### HEADリクエストの送信

HEADリクエストは、以下の関数によって送信する。

**文法**

```py
<レスポンス> = requests.head(<URL>)
```

- レスポンス：ヘッダをもつオブジェクト
- URL：URL（文字列）

**例**

```py
response = requests.head("http://example.com")
```

#### GETリクエストの送信

GETリクエストは、以下の関数によって送信する。

**文法**

```py
<レスポンス> = requests.get(<URL>, params=<パラメータ>)
```

- レスポンス：ヘッダやレスポンスボディをもつオブジェクト
- URL：パラメータを含まないURL（文字列）
- パラメータ：`?`以降のURLパラメータ（ディクショナリ）

**例**

```py
response = requests.get("http://example.com")
```

#### POSTリクエストの送信

POSTリクエストは、以下の関数によって送信する。

**文法**

```py
<レスポンス> = requests.post(<URL>, params=<パラメータ>, json=<リクエストボディ>)
```

- レスポンス：ヘッダやレスポンスボディをもつオブジェクト
- URL：パラメータを含まないURL（文字列）
- パラメータ：`?`以降のURLパラメータ（ディクショナリ）
- リクエストボディ：JSONとして送信するデータ（ディクショナリ）

**例**

```py
response = requests.post(
    "http://example.com/register",
    params={"quiet": "true"},
    json={"user": "you", "age": 255}
)
```

### Requestsの関数の返り値について

RequestsでHTTPリクエストを送信すると、すべてResponse型で返却される。
以下のように記述することで、データを取得することができる。
ただし、取得したレスポンスを`response`とする。

**ステータスコード**

```py
response.status_code
```

ステータスコードを整数型で取得する。

**ステータスコード（正常）**

```py
response.ok
```

ステータスコードが正常範囲（400未満）かどうかを確認する。
正常範囲である場合`True`、異常範囲である場合`False`となる。

**レスポンスボディ**

```py
response.text
```

レスポンスボディを文字列型で取得する。

**レスポンスボディ（ディクショナリ）**

```py
response.json()
```

レスポンスボディをディクショナリ型に変換し取得する。
ただし、レスポンスボディがJSONとして解釈できない場合はエラーを投げる。

## 演習

演習を行う際は、[HTTPクライアント](#httpクライアント)以降に示す注意事項をよく確認すること。

演習では、以下のサイトを用いる。

- [Example Domain](http://example.com/)
- [郵便番号検索API - zipcloud](https://zipcloud.ibsnet.co.jp/doc/api)
- [Free Dictionary API](https://freedictionaryapi.com/)

### 演習1 UNIXコマンドを用いたHTTPリクエスト

#### 1.1

以下のコマンドを用いて、telnetでのWEBアクセスを試みよ。

```sh
telnet example.com 80
```

なお、ここで送信するHTTPリクエストは以下のものとする。

```http
GET / HTTP/1.1
Host: example.com

```

得られた出力を記録し、考察せよ。

#### 1.2

telnetコマンドを用いて、'unix'を検索する。

以下のURLにtelnetでアクセスし、'unix'を検索せよ。

```text
http://lite.duckduckgo.com/lite/?q=unix
```

適切なコマンド及びHTTPリクエストを考え、それを送信することで結果を得ること。

得られた出力を記録し、考察せよ。
ただし、非常に長い文字列が出力されるため、考察に必要な結果のみを記録すること。

#### 1.3

curlコマンドを用いて、'unix'を検索する。

適切なコマンドを考え、それを実行することで結果を得ること。

得られた出力を記録し、考察せよ。

#### 1.4

curlコマンドを用いて、辞書で'HTML'を検索する。

以下のURLにcurlコマンドでアクセスし、'HTML'を検索せよ。

```text
https://freedictionaryapi.com/api/v1/entries/en/HTML
```

適切なコマンドを考え、それを実行することで結果を得ること。

得られた結果を記録し、考察せよ。
また、レスポンスボディからHTMLの言葉の意味を表す値を探し、
それを示せ。

### 演習2 Requestsを用いたHTTPリクエスト

#### 2.1

以下のソースを`sample.py`として保存し、次のコマンドで実行する。

```sh
python3 sample.py
```

得られた結果から、どんな命令がどんな出力を行うのかを説明せよ。

以下、`sample.py`のソースである。

```py
# date  : 2026-02-28

## 英単語の検索

import requests

# URLの設定
URL = "https://freedictionaryapi.com/api/v1/entries/en"

# ユーザーの入力を得る
user_input = input("?: ")
print("*> OK")

# URLとユーザー入力を結合する
target = URL + "/" + user_input
print("<< GET {}".format(target))
print("*> Please Wait...")

# GETリクエスト
response = requests.get(target)

# 正常系か、異常系かの判断
if response.ok:  # 正常系
    print(">> {} {}".format(response.status_code, response.reason))

    response_body = response.json()

    # entriesが空だったら
    if len(response_body["entries"]) <= 0:
        print("*> no entries.")
    else:  # 空じゃなかったら
        # 言葉の定義を取り出す
        defs: list = response_body["entries"][0]["senses"]
        # 定義が複数存在するなら
        if len(defs) > 1:
            # すべての定義を順に出力する
            for i, definition in enumerate(defs):
                print(">> [{}]: {}".format(i, definition["definition"]))
        else:  # 定義が一つしかないなら
            # 単に定義を出力する。
            print(">> {}".format(defs[0]["definition"]))

else:  # 異常系
    print(">> Error! {} {}".format(response.status_code, response.reason))
```

#### 2.2

Python3のRequestsライブラリを用いて、郵便番号から住所を得る。

以下のWEBサイトは、郵便番号検索APIのトップページである。

<https://zipcloud.ibsnet.co.jp/doc/api>

以下のURLにアクセスし、0591275の住所を特定せよ。

```text
http://zipcloud.ibsnet.co.jp/api/search?zipcode=0591275
```

得られた結果を記録し、考察せよ。

#### 2.3

Python3のRequestsライブラリを用いて、郵便番号から住所を得る。

以下の要件を満たすPython3プログラムを作成せよ。

**概要**

ユーザーから入力された郵便番号の住所を特定するプログラムを作成する。

**入力**

ユーザーから、7桁の数字を受け取る。

**出力**

対応する郵便番号の住所を出力する。
ただし、対応する住所が複数存在する場合は、複数出力すること。

**サンプル**

(1) 正常系

入力

```text
0591275
```

出力

```text
北海道苫小牧市錦岡 (ﾎｯｶｲﾄﾞｳﾄﾏｺﾏｲｼﾆｼｷｵｶ)
```

(2) 正常系（複数）

入力

```text
4980000
```

出力

```text
愛知県弥富市 (ｱｲﾁｹﾝﾔﾄﾐｼ)
三重県桑名郡木曽岬町 (ﾐｴｹﾝｸﾜﾅｸﾞﾝｷｿｻｷﾁｮｳ)
```

(3) 異常系（一致なし）

入力

```text
9999999
```

出力

```text
郵便番号が見つかりませんでした。
```

(4) 異常系（不正入力）

入力

```text
aaaaaaa
```

出力

```text
入力が不正です。
```

(5) 異常系（通信失敗）

入力

```text
0591275
```

出力

```text
接続できませんでした。
```

## 参考文献

- [とほほのHTTP入門 - とほほのWWW入門](https://www.tohoho-web.com/ex/http.html)
- [通信の役割・しくみ | NTT東日本 新卒採用情報](https://www.ntt-east.co.jp/recruit/new-grad/about/index.html)
- [通信(ツウシン)とは？ 意味や使い方 - コトバンク](https://kotobank.jp/word/%E9%80%9A%E4%BF%A1-570543)
- [第3回　電気通信のはじまり｜JRC 日本無線株式会社](https://www.jrc.co.jp/casestudy/column/03)
- [プロトコルとは？意味・用語説明｜IT用語集｜KDDI株式会社](https://biz.kddi.com/content/glossary/p/protocol/)
- [【NTT西日本】プロトコル｜ICT用語集｜法人・企業向けICTサービス・ソリューション](https://business.ntt-west.co.jp/glossary/words-00107.html)
- [URL（ユーアールエル）とは？意味やドメインとの違いを初心者に解説](https://ds-b.jp/dsmagazine/what-is-url/)
- [URLの構造 #Network - Qiita](https://qiita.com/mrshouuge/items/8eb61dfaddff744f69eb)
- [telnetでHTTP GETリクエストを送ってみる #Apache - Qiita](https://qiita.com/honeycom/items/d44590dd27d5dccb4b5a)
- [【超初心者】curl コマンドとはなんぞや？！ #API - Qiita](https://qiita.com/studio_k_one/items/8580dfc8bbbfa8360a73)
