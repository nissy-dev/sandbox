fn main() {
    let _four = IpAddrKind::V4;
    let _six = IpAddrKind::V6;

    let home = IpAddr {
        kind: IpAddrKind::V4,
        address: String::from("127.0.0.1"),
    };
    let loopback = IpAddr {
        kind: IpAddrKind::V6,
        address: String::from("::1"),
    };
    println!("{:?}", home);
    println!("{:?}", loopback);

    let home = IpAddr2::V4(String::from("127.0.0.1"));
    let loopback = IpAddr2::V6(String::from("::1"));
    println!("{:?}", home);
    println!("{:?}", loopback);

    let home = IpAddr3::V4(127, 0, 0, 1);
    let loopback = IpAddr3::V6(String::from("::1"));
    println!("{:?}", home);
    println!("{:?}", loopback);

    let m = Message::Write(String::from("hello"));
    m.call();

    let _some_number = Some(5);
    let _some_string = Some("a string");
    let _absent_number: Option<i32> = None;

    let penny = Coin::Penny;
    let value = value_in_cents(&penny);
    println!("{}", value);
    println!("{:#?}", penny);

    let quarter = Coin2::Quarter(UsState::Alaska);
    let value = value_in_cents_2(&quarter);
    println!("{}", value);
    println!("{:#?}", quarter);

    let five = Some(5);
    let _six = plus_one(five);
    let _none = plus_one(None);

    let some_u8_value = 0u8;
    match some_u8_value {
        1 => println!("one"),
        3 => println!("three"),
        5 => println!("five"),
        7 => println!("seven"),
        // _ で省略できる
        _ => (),
    }

    // ケースが少ないときは、if let でかける
    let some_u8_value = Some(0u8);
    match some_u8_value {
        Some(3) => println!("three"),
        _ => (),
    }

    let some_u8_value = Some(3);
    if let Some(3) = some_u8_value {
        println!("three");
    }

    let mut count = 0;
    match quarter {
        // {:?}州のクォーターコイン
        Coin2::Quarter(state) => println!("State quarter from {:?}!", state),
        _ => count += 1,
    }
    println!("{}", count);

    let mut count = 0;
    let penny = Coin2::Penny;
    // 上の match と同じ！
    if let Coin2::Quarter(state) = penny {
        println!("State quarter from {:?}!", state);
    } else {
        count += 1;
    }
    println!("{}", count)
}

#[derive(Debug)]
enum IpAddrKind {
    V4,
    V6,
}

#[derive(Debug)]
struct IpAddr {
    kind: IpAddrKind,
    address: String,
}

#[derive(Debug)]
enum IpAddr2 {
    V4(String),
    V6(String),
}

#[derive(Debug)]
enum IpAddr3 {
    V4(u8, u8, u8, u8),
    V6(String),
}

enum Message {
    Quit,
    Move { x: u32, y: u32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

impl Message {
    fn call(&self) {
        println!("hello!");
    }
}

#[derive(Debug)]
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn value_in_cents(coin: &Coin) -> u32 {
    match coin {
        Coin::Penny => {
            println!("Lucky Penny!");
            1
        }
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}

#[derive(Debug)]
enum UsState {
    Alabama,
    Alaska,
}

#[derive(Debug)]
enum Coin2 {
    Penny,
    Nickel,
    Dime,
    Quarter(UsState),
}

fn value_in_cents_2(coin: &Coin2) -> u32 {
    match coin {
        Coin2::Penny => 1,
        Coin2::Nickel => 5,
        Coin2::Dime => 10,
        Coin2::Quarter(state) => {
            // 中身を受け取れる
            println!("State quarter from {:?}!", state);
            25
        }
    }
}

fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i + 1),
    }
}
