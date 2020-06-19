fn main() {
    let favorite_color: Option<&str> = None;
    let is_tuesday = false;
    let age: Result<u8, _> = "34".parse();

    if let Some(color) = favorite_color {
        // あなたのお気に入りの色、{}を背景色に使用します
        println!("Using your favorite color, {}, as the background", color);
    } else if is_tuesday {
        // 火曜日は緑の日！
        println!("Tuesday is green day!");
    } else if let Ok(age) = age {
        if age > 30 {
            // 紫を背景色に使用します
            println!("Using purple as the background color");
        } else {
            // オレンジを背景色に使用します
            println!("Using orange as the background color");
        }
    } else {
        // 青を背景色に使用します
        println!("Using blue as the background color");
    }

    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    while let Some(top) = stack.pop() {
        println!("{}", top);
    }

    let v = vec!['a', 'b', 'c'];
    for (index, value) in v.iter().enumerate() {
        println!("{} is at index {}", value, index);
    }

    let point = (3, 5);
    print_coordinates(&point);

    let some_option_value: Option<u32> = None;
    if let Some(x) = some_option_value {
        println!("{}", x);
    }

    if let x = 5 {
        println!("{}", x);
    };

    let x = 1;
    match x {
        1 => println!("one"),       // 1
        2 => println!("two"),       // 2
        3 => println!("three"),     // 3
        _ => println!("anything"),  // なんでも
    }

    let x = Some(5);
    let y = 10;
    match x {
        Some(50) => println!("Got 50"),
        // Some(10) ではない！！
        Some(y) => println!("Matched, y = {:?}", y),
        _ => println!("Default case, x = {:?}", x),
    }
    println!("at the end: x = {:?}, y = {:?}", x, y);

    let x = 1;
    match x {
        // 複数もいける
        1 | 2 => println!("one or two"),
        3 => println!("three"),
        // rangeもいける
        4 ... 6 => println!("four through six"),
        _ => println!("anything"),
    }

    let x = 'c';
    match x {
        // ASCII文字前半
        'a' ... 'j' => println!("early ASCII letter"),
        // ASCII文字後半
        'k' ... 'z' => println!("late ASCII letter"),
        _ => println!("something else"),
    }

    let p = Point { x: 0, y: 7 };
    let Point { x: a, y: b } = p;
    assert_eq!(0, a);
    assert_eq!(7, b);
    // 省略もできる
    let Point { x, y } = p;
    assert_eq!(0, x);
    assert_eq!(7, y);

    let p = Point { x: 0, y: 7 };
    match p {
        // 構造体の部分一致もできる
        Point { x, y: 0 } => println!("On the x axis at {}", x),
        Point { x: 0, y } => println!("On the y axis at {}", y),
        Point { x, y } => println!("On neither axis: ({}, {})", x, y),
    }

    let msg = Message::ChangeColor(0, 160, 255);
    match msg {
        Message::Quit => {
            // Quit列挙子には分配すべきデータがない
            println!("The Quit variant has no data to destructure.")
        },
        Message::Move { x, y } => {
            // x, y が分配されている
            println!("Move in the x direction {} and in the y direction {}", x, y)
        },
        Message::Write(text) => println!("Text message: {}", text),
        Message::ChangeColor(r, g, b) => {
            println!("Change the color to red {}, green {}, and blue {}", r, g, b)
        }
    }

    let points = vec![
        Point { x: 0, y: 0 },
        Point { x: 1, y: 5 },
        Point { x: 10, y: -3 },
    ];
    let sum_of_squares: i32 = points
        .iter()
        .map(|&Point { x, y }| x * x + y * y)
        .sum();

    let ((feet, inches), Point {x, y}) = ((3, 10), Point { x: 3, y: -10 });

    foo(3, 4);

    let mut setting_value = Some(5);
    let new_setting_value = Some(10);
    match (setting_value, new_setting_value) {
        (Some(_), Some(_)) => {
            println!("Can't overwrite an existing customized value");
        },
        _ => {
            setting_value = new_setting_value;
        }
    }
    println!("setting is {:?}", setting_value);

    let numbers = (2, 4, 8, 16, 32);
    match numbers {
        (first, _, third, _, fifth) => {
            // 何らかの数値: {}, {}, {}
            println!("Some numbers: {}, {}, {}", first, third, fifth)
        },
    }


    // こんにちは！
    let s = Some(String::from("Hello!"));
    if let Some(_s) = s {
        println!("found a string");
    }
    // _s は値を束縛する
    // println!("{:?}", s);

    let s = Some(String::from("Hello!"));
    if let Some(_) = s {
        println!("found a string");
    }
    println!("{:?}", s);

    let origin = NPoint { x: 0, y: 0, z: 0 };
    match origin {
        NPoint { x, .. } => println!("x is {}", x),
    }

    let numbers = (2, 4, 8, 16, 32);
    match numbers {
        (first, .., last) => {
            println!("Some numbers: {}, {}", first, last);
        },
    }

    let robot_name = Some(String::from("Bors"));
    match robot_name {
        Some(name) => println!("Found a name: {}", name),
        None => (),
    }
    // エラーが出る
    // println!("robot_name is: {:?}", robot_name);

    let robot_name = Some(String::from("Bors"));
    match robot_name {
        // match の中で参照を取るには、ref を使う
        Some(ref name) => println!("Found a name: {}", name),
        None => (),
    }
    println!("robot_name is: {:?}", robot_name);

    let mut robot_name = Some(String::from("Bors"));
    match robot_name {
        // 可変参照版
        Some(ref mut name) => *name = String::from("Another name"),
        None => (),
    }
    println!("robot_name is: {:?}", robot_name);


    let num = Some(4);
    match num {
        Some(x) if x < 5 => println!("less than five: {}", x),
        Some(x) => println!("{}", x),
        None => (),
    }

    let x = Some(5);
    let y = 10;
    match x {
        Some(50) => println!("Got 50"),
        // 組み合わせもできる
        Some(n) if n == y => println!("Matched, n = {:?}", n),
        _ => println!("Default case, x = {:?}", x),
    }
    println!("at the end: x = {:?}, y = {:?}", x, y);

    let msg = NMessage::Hello { id: 5 };
    match msg {
        // @ を使ってパターン評価しつつ、id_variable にマッチした値を束縛する
        NMessage::Hello { id: id_variable @ 3...7 } => {
            println!("Found an id in range: {}", id_variable)
        },
        NMessage::Hello { id: 10...12 } => {
            println!("Found an id in another range")
        },
        NMessage::Hello { id } => {
            println!("Found some other id: {}", id)
        },
    }
}


fn print_coordinates(&(x, y): &(i32, i32)) {
    // 現在の位置: ({}, {})
    println!("Current location: ({}, {})", x, y);
}

fn foo(_: i32, y: i32) {
    // このコードは、y引数を使うだけです: {}
    println!("This code only uses the y parameter: {}", y);
}

struct Point {
    x: i32,
    y: i32,
}

struct NPoint {
    x: i32,
    y: i32,
    z: i32,
}

enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

enum NMessage {
    Hello { id: i32 },
}
