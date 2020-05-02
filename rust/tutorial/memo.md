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

