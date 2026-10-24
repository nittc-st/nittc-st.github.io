---

title: 通信1 演習2
draft: false
date: 2026-03-01
tags: [通信, 演習資料]

---

## 演習2 Requestsを用いたHTTPリクエスト

HTTPクライアント説明資料に示す注意事項をよく確認しながら、演習を行うこと。

### 2.1

以下のコマンドを用いて、sample.pyを実行する。

```sh
python3 演習/2-python3/sample.py
```

得られた結果から、どんな命令がどんな出力を行うのかを説明せよ。

以下、sample.pyのソースである。

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

### 2.2

Python3のRequestsライブラリを用いて、郵便番号から住所を得る。

このWEBサイトは、郵便番号検索APIのトップページである。

https://zipcloud.ibsnet.co.jp/doc/api

以下のURLにアクセスし、0591275の住所を特定せよ。

```
http://zipcloud.ibsnet.co.jp/api/search?zipcode=0591275
```

得られた結果を記録し、考察せよ。

### 2.3

Python3のRequestsライブラリを用いて、郵便番号から住所を得る。

以下の要件を満たすPython3プログラムを作成せよ。

**概要**

ユーザーから入力された郵便番号の住所を特定するプログラムを作成する。

**入力**

ユーザーから、7桁の数字を受け取る。

**出力**

対応する郵便番号の住所を出力する。
ただし、対応する住所が複数存在する場合は、複数出力すること。

#### サンプル

**(1) 正常系**

入力

```
0591275
```

出力

```
北海道苫小牧市錦岡 (ﾎｯｶｲﾄﾞｳﾄﾏｺﾏｲｼﾆｼｷｵｶ)
```

**(2) 正常系 (複数)**

入力

```
4980000
```

出力

```
愛知県弥富市 (ｱｲﾁｹﾝﾔﾄﾐｼ)
三重県桑名郡木曽岬町 (ﾐｴｹﾝｸﾜﾅｸﾞﾝｷｿｻｷﾁｮｳ)
```

**(2) 異常系 (一致なし)**

入力

```
9999999
```

出力

```
郵便番号が見つかりませんでした。
```

**(3) 異常系 (不正入力)**

入力

```
aaaaaaa
```

出力

```
入力が不正です。
```

**(4) 異常系 (通信失敗)**

入力

```
0591275
```

出力

```
接続できませんでした。
```
