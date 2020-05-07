fn main() {
    let mut user1 = User {
        username: String::from("someusername123"),
        email: String::from("someone@example.com"),
        sign_in_count: 1,
        active: true,
    };

    // 一部のフィールドのみを更新したくても、インスタンス全体が可変でなければならない
    user1.email = String::from("anotheremail@example.com");

    let user2_email =  String::from("user2@gmail.com");
    let user2_name =  String::from("user2");
    let _user2 = build_user(user2_email, user2_name);


    let _user3 = User {
        email: String::from("another@example.com"),
        username: String::from("anotherusername567"),
        active: user1.active,
        sign_in_count: user1.sign_in_count,
    };

    let _user4 = User {
        email: String::from("another@example.com"),
        username: String::from("anotherusername567"),
        ..user1
    };

    // structを使うことで、同じ型でも区別をつけることが可能
    struct Color(i32, i32, i32);
    struct Point(i32, i32, i32);
    let _black = Color(0, 0, 0);
    let _origin = Point(0, 0, 0);

    let width1 = 30;
    let height1 = 50;
    println!(
        "The area of the rectangle is {} square pixels.",
        area1(width1, height1)
    );

    let rect1 = (30, 50);
    println!(
        "The area of the rectangle is {} square pixels.",
        area2(rect1)
    );

    // refactor
    let rect2 = Rectangle { width: 30, height: 50 };
    println!(
        "The area of the rectangle is {} square pixels.",
        area3(&rect2)
    );

    // debug
    println!("rect2 is {:?}", rect2);
    println!("rect2 is {:#?}", rect2);

    println!(
        "The area of the rectangle is {} square pixels.",
        rect2.area()
    );

    let rect1 = Rectangle { width: 30, height: 50 };
    let rect2 = Rectangle { width: 10, height: 40 };
    let rect3 = Rectangle { width: 60, height: 45 };
    // rect1にrect2ははまり込む？
    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));
    println!("Can rect1 hold rect3? {}", rect1.can_hold(&rect3));

    let sq = Rectangle::square(3);
}

struct User {
    username: String,
    email: String,
    sign_in_count: u64,
    active: bool,
}

fn build_user(email: String, username: String) -> User {
    User {
        // email: email,
        email,
        // username: username,
        username,
        active: true,
        sign_in_count: 1,
    }
}

fn area1(width: u32, height: u32) -> u32 {
    width * height
}

fn area2(dimensions: (u32, u32)) -> u32 {
    dimensions.0 * dimensions.1
}

#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }

    // // インスタンスが存在しないメソッド（静的メソッド？）
    // fn square(size: u32) -> Rectangle {
    //     Rectangle { width: size, height: size }
    // }
}

// 複数に分けることが可能
impl Rectangle {
    // インスタンスが存在しないメソッド（静的メソッド？）
    fn square(size: u32) -> Rectangle {
        Rectangle { width: size, height: size }
    }
}

fn area3(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}