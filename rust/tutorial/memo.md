# Rust Tutorial メモ

チュートリアル：https://doc.rust-jp.rs/book/second-edition/foreword.html

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
- `&` で参照を明示しているらしい...
  - つける時とつけないときがあってよくわからん...
- `match` : switch 文的な立ち位置だと理解
  - 返り値がenumのとき、それぞれの値に対して処理を記述する

## chapter3

- シャドーイング
  - 同じ変数を再定義して、上書きすること
  - 変数はimmutableだが、`let` で再定義は可能
  - `mut` との違い
    - 値の型を変えることが可能
- tuple について
  - 配列のとアクセスの仕方が違う
- 式と文の違い
  - 文：何らかの動作はするが値は返さないコード
  - 式：なにかに評価されるコード (=値を返す...?)
    - 式は文の一部になりえる
    - 式は終端にセミコロンを含まない
- 関数
  - 返り値は基本的に、関数内の最後の式となる
- if 式の使用
  - 条件文内で違う型の値を返そうとするとコンパイル時にエラーを出してくれる
