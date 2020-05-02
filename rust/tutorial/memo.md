# Rust Tutorial メモ

## chapter 1

- `!` をつけると関数呼び出しではなく、マクロの呼び出しになる
  - マクロと関数の違いについては19章で確認する
- Cargo : Rust’s build system and package manager
  - Cargo.tomlに外部パッケージの情報を書くようにする
  - ソースコードは、`src`以下に置く
  - コマンドの使いかた
   - `cargo run` : build + binary run
   - `cargo check` ; build check
   - `cargo build --release` : release build (compile it with optimizations)

## chapter 2

- `mut` : 変数がmutableであることを定義している
  - Rustでは原則immutable
- crate : https://crates.io/
  - rust のパッケージを探したい時はここで探す
- rust の標準入出力のエラーハンドリングは厳格
  - 基本的に`io::Result`に対応する処理を必要がある
- `match` : switch 文的な立ち位置だと理解
  - 返り値がenumのとき、それぞれの値に対して処理を記述する