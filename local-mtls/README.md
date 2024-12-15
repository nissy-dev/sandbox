# ローカルで mTLS をやる

TLS を理解したいので自分で証明書と発行してみて、その作業のログを残しておく。

https://qiita.com/kentarok/items/15c08350274fa5578aaf

実際には、mkcert とかを使うと多分楽できるはず。

## mTLS

## サーバー側

自分で認証するので、認証局の準備をします。
CN に今回のサーバーの hostname を適切に設定しないと、curl でのアクセス時にエラーが出てしまいます。

```shell
openssl req -new -x509 -nodes -days 365 -subj '/CN=localhost' -keyout server-ca.key -out server-ca.crt
```

サーバーの秘密鍵を作成します。

```shell
openssl genrsa -out server.key
```

認証局に提出するサーバーの CSR (証明書要求) を作成します。

```shell
openssl req -new -key server.key -out server.csr
```

サーバーの TLS 証明書を発行します。ここでも CN に今回のサーバーの hostname を適切に設定します。

```shell
openssl x509 -req -in server.csr -CA server-ca.crt -CAkey server-ca.key -CAcreateserial -subj '/CN=localhost' -days 365 -out server.crt
```

サーバーを起動して、認証局の TLS 証明書と一緒にリクエストすると結果が返ってきます。

```shell
node server.js
curl --cacert server-ca.crt https://localhost:3000
```

一般的なTLS では、PC にあらかじめインストールされている認証局の公開鍵を使って、サーバーから送られてくる TLS 証明書を復号します。

## クライアント側

基本的にはサーバー側と同様の手順を行なって、クライアント側の TLS 証明書を作成します。

```shell
openssl req -new -x509 -nodes -days 365 -subj '/CN=localhost' -keyout client-ca.key -out client-ca.crt
openssl genrsa -out client.key
openssl req -new -key client.key -subj '/CN=localhost' -out client.csr
openssl x509 -req -in client.csr -CA client-ca.crt -CAkey client-ca.key -CAcreateserial -subj '/CN=localhost' -days 365 -out client.crt
```

サーバーを起動して、サーバーの認証局の TLS 証明書だけでなく、クライアントの TLS 証明書と秘密鍵を渡すと結果が返ってきます。

```shell
node server-mtls.js
curl --cacert server-ca.crt --key ./client.key --cert ./client.crt https://localhost:3000
```
