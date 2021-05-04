use std::io;

fn main() {
    let mut x = 5;
    println!("The value of x is: {}", x);
    x = 6;
    println!("The value of x is: {}", x);

    const MAX_POINTS: u32 = 100_000;
    println!("MAX_POINTS is {}", MAX_POINTS);

    let x = 5;
    let x = x + 1;
    let x = x * 2;
    println!("The value of x is: {}", x);

    // valid
    let spaces = "   ";
    let spaces = spaces.len();
    println!("The number of spaces is: {}", spaces);

    // invalid
    // let mut spaces = "   ";
    // spaces = spaces.len();

    let _guess : u32 = "42".parse().expect("Not a number!");
    let x = 2.0;
    println!("The value of x is: {}", x);
    let y: f32 = 3.0;
    println!("The value of y is: {}", y);
    let sum = 5 + 10;
    println!("The value of sum is: {}", sum);
    let diff = 95.5 - 4.3;
    println!("The value of diff is: {}", diff);
    let prod = 4 * 30;
    println!("The value of prod is: {}", prod);
    let quotient = 56.7 / 32.2;
    println!("The value of quotient is: {}", quotient);
    let reminder = 43 % 5;
    println!("The value of reminder is: {}", reminder);

    // tuple
    let tup : (i32, f64, u8) = (500, 6.4, 1);
    let (_x, y, _z) = tup;
    println!("The value of y: {}", y);

    let x : (i32, f64, u8) = (500, 6.4, 1);
    let _five = x.0;
    let _six = x.1;
    let _one = x.2;

    // array
    let a = [1, 2, 3, 4, 5];
    let _months = [
        "January", "February", "March", "April", 
        "May", "June", "July", "August", "September", 
        "October", "November", "December"
    ];
    let _first = a[0];
    let _second = a[1];
    // let index = 10;
    // let element = a[index];
    // println!("The value of element is: {}", element);

    // function
    another_fn(5, 6);

    // 式と文の違い
    let x = 5;
    let y = {
        let x = 3;
        // no need semicolon
        x + 1
    };
    // show y=4
    println!("The value of y is: {}", y);

    let x = five();
    println!("The value of x is: {}", x);

    let x = plus_one(5);
    println!("The value of x is: {}", x);


    // if statement
    let number = 3;
    if number < 5 {
        println!("condition was true");
    } else {
        println!("condition was false");
    }

    // throw comiple error
    // if number {
    //     println!("number was three");
    // }

    if number != 0 {
        println!("number was something other than zero");
    }

    let number = 6;
    if number % 4 == 0 {
        println!("number is divisible by 4");
    } else if number % 3 == 0 {
        println!("number is divisible by 3");
    } else if number % 2 == 0 {
        println!("number is divisible by 2");
    } else {
        println!("number is not divisible by 4, 3, or 2");
    }

    // use if in let statement
    let cond = true;
    let number = if cond {
        5
    } else {
        6
    };
    println!("The value of number is: {}", number);

    // throw compile error
    // let number = if cond {
    //     5
    // } else {
    //     "six"
    // };

    // loop
    let mut number = 3;
    while number != 0 {
        println!("{}!", number);
        number = number - 1;
    }
    println!("LIFTOFF!!!");

    // for loop (slow)
    let a = [10, 20, 30, 40, 50];
    let mut index = 0;
    while index < 5 {
        println!("the value is: {}", a[index]);
        index = index + 1;
    }

    // for loop (fast)
    for element in a.iter() {
        println!("the value is: {}", element);
    }

    for number in (1..4).rev() {
        println!("{}!", number);
    }
    println!("LIFTOFF!!!");

    // 華氏 (fahrenheit) → 摂氏 (celsius)
    temp_converter();

    // show fibonacci
    show_fibonacci()
}

fn another_fn(x: i32, y: i32) {
    println!("Another function!");
    println!("The value of x is: {}", x);
    println!("The value of y is: {}", y);
}

fn five() -> i32 {
    5
}

fn plus_one(x: i32) -> i32 {
    x + 1
}

// no need semicolon
// fn plus_one_invalid(x: i32) -> i32 {
//     x + 1;
// }


fn temp_converter() {
    println!("Please input fahrenheit today!");

    let mut fahrenheit = String::new();

    io::stdin()
        .read_line(&mut fahrenheit)
        .expect("Failed to read line");

    let fahrenheit: f64 = fahrenheit.trim().parse().unwrap();

    let celsius = (5.0 / 9.0) * (fahrenheit - 32.0);
    println!("celsius is {:.1}", celsius);
}

fn show_fibonacci() {
    println!("Please input number!");

    let mut n = String::new();

    io::stdin()
        .read_line(&mut n)
        .expect("Failed to read line");

    let n: i64 = n.trim().parse().unwrap();
    let ans = fib(n);
    println!("fibonacci number is {}", ans);

    let mut f_n: i64 = 0;
    let mut f_n1: i64 = 1;
    let mut f_n2: i64 = 0;
    let mut cnt: i64 = 2;
    while cnt <= n {
        f_n2 = f_n1 + f_n;
        f_n = f_n1;
        f_n1 = f_n2;
        cnt += 1;
    }
    println!("fibonacci number is {}", f_n2);
}

// 再帰実装
fn fib(n: i64) -> i64 {
    if n < 2 {
        return n;
    } else {
        return fib(n-1) + fib(n-2);
    }
}