use proconio::{fastout, input};

#[fastout]
fn main() {
    input! {
        a: usize,
        b: usize,
        h: usize,
    }
    println!("{}", ((a + b) * h) / 2);
}
