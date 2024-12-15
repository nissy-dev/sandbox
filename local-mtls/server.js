const https = require("https");
const fs = require("fs");
const express = require("express");

// Express アプリの作成
const app = express();

// サーバー証明書と秘密鍵の読み込み
const options = {
  key: fs.readFileSync("./server.key"),
  cert: fs.readFileSync("./server.crt"),
};

// ルートのエンドポイント
app.get("/", (req, res) => {
  res.send("Hello, TLS World!");
});

// HTTPS サーバーの起動
https.createServer(options, app).listen(3000, () => {
  console.log("HTTPS Server running at https://localhost:3000");
});
