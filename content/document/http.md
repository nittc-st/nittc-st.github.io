---

title: 通信1 HTTPクライアント説明資料
draft: false
date: 2026-02-28
tags: [通信, 説明資料]
---

## HTTPクライアント

この資料では、それぞれの使い方や仕様を示します。
これを見ながら、[演習1](1-cmd.md)、[演習2](2-python3.md)に取り組んでください。

ここからは、実際にプログラムでHTTP通信を行う方法について学習します。

HTTPクライアントとは、HTTP通信を行うクライアントアプリケーションのことを指します。
（厳密な定義があるわけではありませんが、ここでは上のように定義します。）

通信1では、以下の2つの方法について学習します。

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
インターネット接続を行うコマンドである。

**文法**

```sh
telnet <ホスト> 80
```

**コマンド例**

```sh
telnet example.com 80
```

このコマンドを実行すると、ホストに接続を試みる。
接続が成功すると、HTTP通信(コネクション)を開始する。

コネクションが開始されると、以下のようなメッセージが表示される。

```
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
通信説明資料 ステータスコード の条を参考にせよ。

なお、HTTPリクエストの入力については、数秒でコネクションが遮断されるため、
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

**コマンド例**

```sh
curl -L -v http://example.com
```

このコマンドを使用すると、
自動でGETリクエストを送信し、受信を待機する。

標準出力には、
接続情報、送信されたGETリクエスト、返信されたヘッダ、
レスポンスボディ(ペイロード)が表示される。

**出力例**

```
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

## Python3のライブラリを用いる方法

### JSONについて

HTTP通信において、データを送信するときによく用いる形式として、JSONがある。

**文法**

キー・値の組を定義するとき(map)は、波括弧を使用する。

```
{
    <キー>: <値>
}
```

配列を定義するとき(array)は、角括弧を使用する。

```
[
    <アイテム>
]
```

キーに設定できるのは、以下の2つのリテラルである。

- string
- number

値に設定できるのは、以下の5つのリテラルである。

- string
- number
- boolean
- null
- map
- array

**例**

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

なお、Python3においては、jsonはディクショナリ型によって代用される。

ディクショナリ型の変数dictがあるとき、
あるキーに値を代入するときは、以下のように記述する。

```py
dict[<キー/インデックス>] = <値>
```

あるキーの値を取得するときは、以下のように記述する。

```py
<変数> = dict[<キー/インデックス>]
```

**例**

```py
definition = res["entries"]["senses"][0]["definition"]
```

### Requestsの使い方

Python3では、Requestsモジュール(ライブラリ)を用いてHTTP通信を行う。
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

レスポンス: ヘッダをもつクラス

URL       : URL (文字列)

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

レスポンス: ヘッダやレスポンスボディをもつクラス

URL       : パラメータを含まないURL (文字列)

パラメータ: `?`以降のURLパラメータ  (ディクショナリ)

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

レスポンス: ヘッダやレスポンスボディをもつクラス

URL       : パラメータを含まないURL (文字列)

パラメータ: `?`以降のURLパラメータ  (ディクショナリ)

**例**

```py
response = requests.post(
    "http://example.com/register",
    params={"quiet": true},
    json={"user": "you", "age": 255}
)
```

### requestsの関数の返り値について

requestsでHTTPリクエストを送信すると、すべてResponse型で返却される。
以下のように記述することで、データを取得することができる。
ただし、取得したレスポンスをresponseとする。

**ステータスコード**

```
response.status_code
```

ステータスコードを整数型で取得する。

**ステータスコード(正常)**

```
response.ok
```

ステータスコードが正常範囲(<200)かどうかを確認する。
正常範囲である場合true, 異常範囲である場合false

**レスポンスボディ**

```
response.text
```

レスポンスボディを文字列型で取得する。

**レスポンスボディ(ディクショナリ)**

```
response.json()
```

レスポンスボディをディクショナリ型に変換し取得する。
ただし、レスポンスボディがJSONとして解釈出来ない場合はエラーを投げる。
