extern crate add_one;
extern crate rand;

fn main() {
    let num = 10;
    // こんにちは世界！{}+1は{}!
    println!(
        "Hello, world! {} plus one is {}!",
        num,
        add_one::add_one(num)
    );
}
