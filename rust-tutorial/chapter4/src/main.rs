fn main() {
    // stack 
    let mut s = "hello";
    // invalid
    // s.push_str(", world!");

    // heap
    let mut s = String::from("hello");
    s.push_str(", world!");
    println!("{}", s);

    // 以下の例だとs1とs2は、同じヒープのメモリ領域をさしている
    let s1 = String::from("hello");
    // s1の実態はs2に移っており、s1にはアクセスできない (メモリ安全のため)
    // shallow copy
    let s2 = s1;
    // println!("{}, world!", s1);
    println!("{}, world!", s2);

    // clone すればアクセスできるようになる
    let s1 = String::from("hello");
    // ヒープメモリもコピーされるため、s1の実態もスタックメモリに残っている
    // deep copy
    let s2 = s1.clone();
    println!("s1 = {}, s2 = {}", s1, s2);

    let s = String::from("hello");
    takes_ownership(s);
    // sの値は、some_stringに移っており、もうアクセスできない
    // println!("{}", s);
    let x = 5;
    makes_copy(x);
    // こっちは使える
    println!("{}", x);

    let s1 = gives_ownership();
    println!("{}", s1);
    let s2 = String::from("hello");
    let s3 = takes_and_gives_back(s2);
    println!("{}", s3);

    let s1 = String::from("hello");
    let (s2, len) = calculate_length(s1);
    println!("The length of '{}' is {}.", s2, len);

    let s1 = String::from("hello");
    let len = smart_calculate_length(&s1);
    println!("The length of '{}' is {}.", s1, len);

    let s = String::from("hello");
    change(&s);

    let mut s = String::from("hello");
    valid_change(&mut s);

    let mut s = String::from("hello");
    let r1 = &mut s;
    // エラーが出るはずだけどでない。。。
    let r2 = &mut s;
    let r1 = &s;
    let r2 = &s;
    // エラーが出るはずだけどでない。。。
    let r3 = &mut s;

    // NG
    // let reference_to_nothing = dangle();
    // OK
    let value = nodangle();

    let mut s = String::from("hello world");
    let first_word_len = first_word_length(&s); // wordの中身は、値5になる
    println!("first_word_len is {}", first_word_len);
    s.clear();

    // スライスでアクセスできる
    let s = String::from("hello world");
    let hello = &s[0..5];
    let world = &s[6..11];
    println!("{} {}.", hello, world);

    // 0は省略可能
    let slice = &s[0..2];
    let slice = &s[..2];
    // 最後も省略可能
    let len = s.len();
    let slice = &s[3..len];
    let slice = &s[3..];

    let mut s = String::from("hello world");
    let first_word_str = first_word(&s); // wordの中身は、値5になる
    println!("first_word is {}", first_word_str);
    s.clear();

    let my_string = String::from("hello world");
    let word = custom_first_word(&my_string);
    // すでに &str 型である
    let my_string_literal = "hello world";
    let word = custom_first_word(&my_string_literal[..]);
    let word = custom_first_word(my_string_literal);

    // 配列スライス
    let a = [1, 2, 3, 4, 5];
    let slice: &[i32] = &a[1..3];
}

fn takes_ownership(some_string: String) {
    println!("{}", some_string);
}

fn makes_copy(some_integer: i32) {
    println!("{}", some_integer);
}

fn gives_ownership() -> String {
    let some_string = String::from("hello");
    some_string
}

fn takes_and_gives_back(a_string: String) -> String {
    a_string
}

fn calculate_length(s: String) -> (String, usize) {
    let length = s.len();
    // 長さを計算するために実態をこの関数に移してしまうため、sも戻り値に返す必要がある
    (s, length)
}

// &をつけることで、所有権をもらわずに参照する
fn smart_calculate_length(s: &String) -> usize {
    s.len()
}

fn change(some_string: &String) {
    // 所有権がないので 以下はエラーになる
    // some_string.push_str(", world");
}

// mut で可変の参照も一応可能
fn valid_change(some_string: &mut String) {
    some_string.push_str(", world");
}

// sのポインタを参照先にわたすが、sのメモリ領域は削除されてしまう
// fn dangle() -> &String {
//     let s = String::from("hello");
//     &s
// }

fn nodangle() -> String {
    let s = String::from("hello");
    s
}

fn first_word_length(s: &String) -> usize {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return i;
        }
    }

    s.len()
}

fn first_word(s: &String) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}

fn custom_first_word(s: &str) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}