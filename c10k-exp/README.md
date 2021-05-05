# C10k 問題の実験

[Apache と Nginx について比較](https://qiita.com/kamihork/items/49e2a363da7d840a4149)

以上の記事にもあるように、

- Apache : マルチプロセスのプロセス駆動アーキテクチャ
- Nginx : シングルスレッドモデルのイベント駆動アーキテクチャ

とのことなので実際に Apache Bench を使って負荷試験をやってみた

## 実験手順

### レスポンスで返す HTML の準備

5MB 程度の大きめの HTML を準備した (`large_html`に配置)

### Apache

```sh
$ docker run --name apache_server -d -v $PWD/large_html:/usr/local/apache2/htdocs httpd
$ docker exec -it apache_server /bin/bash

// 以下コンテナ内での操作
$ ab -c 1000 -n 10000 -r http://localhost/ > /tmp/apache_c1000_n10000.log
$ ab -c 10000 -n 10000 -r http://localhost/ > /tmp/apache_c10000_n10000.log
```

### Nginx

```sh
$ docker run --name ngnix_server -d -v $PWD/large_html:/usr/share/nginx/html nginx
$ docker exec -it ngnix_server /bin/bash

// 以下コンテナ内での操作
$ apt-get update && apt-get install -y apache2-utils
$ ab -c 1000 -n 10000 -r http://localhost/ > /tmp/nginx_c1000_n10000.log
$ ab -c 10000 -n 10000 -r http://localhost/ > /tmp/nginx_c10000_n10000.log
```

### 結果

- レスポンスの速さ
  - Apache の方が全体的にかなり遅い
  - Nignx は、`-c 10000 -n 10000`で一瞬だった
    - プロセスを立ち上げるオーバーヘッドがないから...?
- レスポンスの正確さ (失敗の少なさ)
  - Apache の方が正確
    - 特に同時接続数が少ないときに顕著
  - Nginx はデフォルトで同時接続数を`2000`に制限していた
    - `/etc/nginx/nginx.conf`に設定は書かれている
