fn main() {
    let mut num = 5;

    // as *const T でポインタを生成できる
    let r1 = &num as *const i32; // 参照があるところのアドレスが表示される, 参照は値のアドレスを保持する
    let r2 = &mut num as *mut i32; // 参照があるところのアドレスが表示される
    let r3 = num as *const i32; // 値があるところのアドレスが表示される
    let r4 = num as *mut i32; // 値があるところのアドレスが表示される
    let r5 = &num;
    println!("{:?}", r1);
    println!("{:?}", r2);
    println!("{:?}", r3);
    println!("{:?}", r4);
    println!("{:?}", r5);

    // 以下のように、直接ポインタも生成できる
    // 値の存在がするかどうかは保証しない
    let address = 0x012345usize;
    let r = address as *const i32;
    println!("{:?}", r);

    // ポインタの実態を取得
    unsafe {
        // println!("r is: {}", *r); // Segmentation fault
        println!("r1 is: {}", *r1);
        println!("r2 is: {}", *r2);
    }

    // unsafeな関数を呼び出すには、unsafeブロックが必要
    unsafe fn dangerous() {}
    unsafe {
        dangerous();
    }

    let mut v = vec![1, 2, 3, 4, 5, 6];
    let r = &mut v[..];
    let (a, b) = r.split_at_mut(3);
    assert_eq!(a, &mut [1, 2, 3]);
    assert_eq!(b, &mut [4, 5, 6]);

    let (a, b) = split_at_mut(r, 3);
    assert_eq!(a, &mut [1, 2, 3]);
    assert_eq!(b, &mut [4, 5, 6]);

    // 以下のように任意のメモリアドレスからスライスを生成することもできる
    let address = 0x012345usize;
    let r = address as *mut i32;
    let slice = unsafe { slice::from_raw_parts_mut(r, 10000) };
    // 但し値がない場合はセグフォになる
    // println!("{:?}", slice); // Segmentation fault: 11

    unsafe {
        // externの関数を呼ぶ際は、unsafeブロックを使う
        println!("Absolute value of -3 according to C: {}", abs(-3));
    }

    println!("name is: {}", HELLO_WORLD);
    add_to_count(3);
    unsafe {
        // mutableなstatic変数 (グローバル変数)は、unsafeでアクセスできる
        println!("COUNTER: {}", COUNTER);
    }

    assert_eq!(
        Point { x: 1, y: 0 } + Point { x: 2, y: 3 },
        Point { x: 3, y: 3 }
    );

    let person = Human;
    Pilot::fly(&person);
    Wizard::fly(&person);
    person.fly();

    println!("A baby dog is called a {}", Dog::baby_name());
    // Traitでoverrideした時は、以下のフルパス記法を使う
    println!("A baby dog is called a {}", <Dog as Animal>::baby_name());

    let w = Wrapper(vec![String::from("hello"), String::from("world")]);
    println!("w = {}", w);

    // str : 動的サイズ付け型
    // なのでstrの変数を生成したり、strを引数に取ることはできない
    // let s2: str = "How's it going?";
    // &str 参照はアドレスと"長さ"の情報
    let _s1: &str = "Hello there!";

    let answer = do_twice(add_one, 5);
    println!("The answer is: {}", answer);

    let list_of_numbers = vec![1, 2, 3];
    let list_of_strings: Vec<String> = list_of_numbers.iter().map(|i| i.to_string()).collect();
    println!("{:?}", list_of_strings);
    let list_of_strings: Vec<String> = list_of_numbers.iter().map(ToString::to_string).collect();
    println!("{:?}", list_of_strings);
}

// fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
//     let len = slice.len();

//     assert!(mid <= len);

//     // 同じスライスから２度の借用が行われているので、コンパイルエラーになる
//     // 実際は、2つのスライスがかぶることがないので問題ない
//     (&mut slice[..mid], &mut slice[mid..])
// }

use std::slice;

// safe rust で呼び出せる
fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    // スライスの生ポインタを返す
    let ptr = slice.as_mut_ptr();
    println!("{:?}", ptr);

    assert!(mid <= len);

    unsafe {
        // slice::from_raw_parts_mutとoffsetはunsafe
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.offset(mid as isize), len - mid),
        )
    }
}

// extern ブロックで他の言語で定義されたコードの関数を使うことができる
extern "C" {
    // インターフェイスを定義する
    fn abs(input: i32) -> i32;
}

// rustのグローバル変数は、staticで定義
static HELLO_WORLD: &str = "Hello, world!";
static mut COUNTER: u32 = 0;

fn add_to_count(inc: u32) {
    unsafe {
        // mutableなstatic変数 (グローバル変数)は、unsafeでアクセスできる
        COUNTER += inc;
    }
}

// struct Context<'a>(&'a str);
// struct Parser<'a> {
//     context: &'a Context<'a>,
// }
// impl<'a> Parser<'a> {
//     fn parse(&self) -> Result<(), &str> {
//         Err(&self.context.0[1..])
//     }
// }

// fn parse_context(context: Context) -> Result<(), &str> {
//     // ParserとContextはこの関数のスコープに閉じているので、このスコープに閉じた関数
//     // parse関数自体は、Contextの参照を返すので矛盾する
//     Parser { context: &context }.parse()
// }

// なので、ParserとContextに異なるライフタイム引数を与える
struct Context<'s>(&'s str);
struct Parser<'c, 's> {
    context: &'c Context<'s>,
}
impl<'c, 's> Parser<'c, 's> {
    fn parse(&self) -> Result<(), &'s str> {
        Err(&self.context.0[1..])
    }
}

fn parse_context(context: Context) -> Result<(), &str> {
    Parser { context: &context }.parse()
}

struct Ref<'a, T>(&'a T);

use std::ops::Add;

#[derive(Debug, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

impl Add for Point {
    type Output = Point;

    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}

struct Millimeters(u32);
struct Meters(u32);

impl Add<Meters> for Millimeters {
    type Output = Millimeters;

    fn add(self, other: Meters) -> Millimeters {
        Millimeters(self.0 + (other.0 * 1000))
    }
}

trait Pilot {
    fn fly(&self);
}

trait Wizard {
    fn fly(&self);
}

struct Human;

impl Pilot for Human {
    fn fly(&self) {
        println!("This is your captain speaking.");
    }
}

impl Wizard for Human {
    fn fly(&self) {
        println!("Up!");
    }
}

impl Human {
    fn fly(&self) {
        println!("*waving arms furiously*");
    }
}

trait Animal {
    fn baby_name() -> String;
}

struct Dog;

impl Dog {
    fn baby_name() -> String {
        String::from("Spot")
    }
}

impl Animal for Dog {
    fn baby_name() -> String {
        String::from("puppy")
    }
}

use std::fmt;

trait OutlinePrint: fmt::Display {
    fn outline_print(&self) {
        let output = self.to_string();
        let len = output.len();
        println!("{}", "*".repeat(len + 4));
        println!("*{}*", " ".repeat(len + 2));
        println!("* {} *", output);
        println!("*{}*", " ".repeat(len + 2));
        println!("{}", "*".repeat(len + 4));
    }
}

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

impl OutlinePrint for Point {}

struct Wrapper(Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}

fn add_one(x: i32) -> i32 {
    x + 1
}

fn do_twice(f: fn(i32) -> i32, arg: i32) -> i32 {
    f(arg) + f(arg)
}

fn returns_closure() -> Box<Fn(i32) -> i32> {
    // クロージャーは型アノテーションがないので、Boxを使わないと返却できない
    Box::new(|x| x + 1)
}
