fn main() {
    let num_list = vec![34, 50, 25, 100, 65];
    let mut largest_num = num_list[0];

    for num in num_list {
        if largest_num < num {
            largest_num = num;
        }
    }

    println!("The largest number is {}", largest_num);

    let number_list = vec![34, 50, 25, 100, 65];
    let result = largest_prev(&number_list);
    println!("The largest number is {}", result);

    let number_list = vec![102, 34, 6000, 89, 54, 2, 43, 8];
    let result = largest_prev(&number_list);
    println!("The largest number is {}", result);

    let number_list = vec![34, 50, 25, 100, 65];
    let result = largest_i32(&number_list);
    println!("The largest number is {}", result);

    let char_list = vec!['y', 'm', 'a', 'q'];
    let result = largest_char(&char_list);
    println!("The largest char is {}", result);

    let number_list = vec![34, 50, 25, 100, 65];
    let result = largest(&number_list);
    println!("The largest number is {}", result);

    let char_list = vec!['y', 'm', 'a', 'q'];
    let result = largest(&char_list);
    println!("The largest char is {}", result);

    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.0, y: 4.0 };
    // can not compile
    // let wont_work = Point { x: 5, y: 4.0 };

    let both_integer = FlexiblePoint { x: 5, y: 10 };
    let both_float = FlexiblePoint { x: 1.0, y: 4.0 };
    let integer_and_float = FlexiblePoint { x: 5, y: 4.0 };

    let p = Point { x: 5, y: 10 };
    println!("p.x = {}", p.x());

    let p1 = FlexiblePoint { x: 5, y: 10.4 };
    let p2 = FlexiblePoint { x: "Hello", y: 'c' };
    let p3 = p1.mixup(p2);
    println!("p3.x = {}, p3.y = {}", p3.x, p3.y);

    let tweet = Tweet {
        username: String::from("horse_ebooks"),
        content: String::from("of course, as you probably already know, people"),
        reply: false,
        retweet: false,
    };
    println!("1 new tweet: {}", tweet.summarize());

    let article = NewsArticleWithDefault {
        headline: String::from("Penguins win the Stanley Cup Championship!"),
        location: String::from("Pittsburgh, PA, USA"),
        author: String::from("Iceburgh"),
        content: String::from(
            "The Pittsburgh Penguins once again are the best hockey team in the NHL.",
        ),
    };
    println!("New article available! {}", article.summarize());

    // ダンリング参照
    // let r;

    // {
    //     let x = 5;
    //     r = &x;
    // }

    // println!("r: {}", r);

    let string1 = String::from("abcd");
    let string2 = "xyz";

    let result = longest(string1.as_str(), string2);
    // 最長の文字列は、{}です
    println!("The longest string is {}", result);

    let string1 = String::from("long string is long");
    {
        let string2 = String::from("xyz");
        let result = longest(string1.as_str(), string2.as_str());
        println!("The longest string is {}", result);
    }

    // let string1 = String::from("long string is long");
    // let result;
    // {
    //     let string2 = String::from("xyz");
    //      error happen
    //     result = longest(string1.as_str(), string2.as_str());
    // }
    // println!("The longest string is {}", result);

    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let i = ImportantExcerpt {
        part: first_sentence,
    };

    // プログラム全体の期間で参照できる
    let s: &'static str = "I have a static lifetime.";
}

fn largest_prev(list: &[i32]) -> i32 {
    let mut largest_num = list[0];

    for &item in list.iter() {
        if largest_num < item {
            largest_num = item;
        }
    }

    largest_num
}

fn largest_i32(list: &[i32]) -> i32 {
    let mut largest_num = list[0];

    for &item in list.iter() {
        if largest_num < item {
            largest_num = item;
        }
    }

    largest_num
}

fn largest_char(list: &[char]) -> char {
    let mut largest_num = list[0];

    for &item in list.iter() {
        if largest_num < item {
            largest_num = item;
        }
    }

    largest_num
}

fn largest<T: PartialOrd + Copy>(list: &[T]) -> T {
    let mut largest = list[0];

    for &item in list.iter() {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn largest_anotehr<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}

struct Point<T> {
    x: T,
    y: T,
}

// Point<T>すべてに有効なメソッド定義
impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

// Point<f32>のみ有効なメソッド定義
impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

struct FlexiblePoint<T, U> {
    x: T,
    y: U,
}

impl<T, U> FlexiblePoint<T, U> {
    fn mixup<V, W>(self, other: FlexiblePoint<V, W>) -> FlexiblePoint<T, W> {
        FlexiblePoint {
            x: self.x,
            y: other.y,
        }
    }
}

pub trait Summary {
    fn summarize_author(&self) -> String {
        String::from("Default value")
    }
    // fn summarize(&self) -> String;
    fn summarize(&self) -> String {
        // デフォルト値を入れることができる
        // String::from("(Read more...)")
        format!("(Read more from {}...)", self.summarize_author())
    }
}

pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

pub struct NewsArticleWithDefault {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticleWithDefault {}

pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}

impl Summary for Tweet {
    fn summarize_author(&self) -> String {
        format!("@{}", self.username)
    }
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

pub fn notify<T: Summary>(item: T) {
    // 新ニュース！ {}
    println!("Breaking news! {}", item.summarize());
}

use std::fmt::Debug;
use std::fmt::Display;

// 2つの型を満たす引数が欲しい時は、＋をつかう
fn some_function<T: Display + Clone, U: Clone + Debug>(t: T, u: U) -> i32 {
    0
}

// whereを使っても綺麗にかけるよ
fn some_function_with_where<T, U>(t: T, u: U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug,
{
    0
}

struct Pair<T> {
    x: T,
    y: T,
}

// すべてのケースでnewメソッドはもつ
impl<T> Pair<T> {
    fn new(x: T, y: T) -> Self {
        Self { x, y }
    }
}

// Display + PartialOrd のときのみ
impl<T: Display + PartialOrd> Pair<T> {
    fn cmp_display(&self) {
        if self.x >= self.y {
            println!("The largest member is x = {}", self.x);
        } else {
            println!("The largest member is y = {}", self.y);
        }
    }
}

// fn longest(x: &str, y: &str) -> &str {
//     if x.len() > y.len() {
//         x
//     } else {
//         y
//     }
// }

// 全参照が同じライフタイム'a であることを示す
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }

    fn announce_and_return_part(&self, announcement: &str) -> &str {
        // お知らせします
        println!("Attention please: {}", announcement);
        self.part
    }
}

fn longest_with_an_announcement<'a, T>(x: &'a str, y: &'a str, ann: T) -> &'a str
where
    T: Display,
{
    // アナウンス！
    println!("Announcement! {}", ann);
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
