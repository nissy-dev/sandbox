use proconio::{fastout, input};

#[fastout]
fn main() {
    input! {
        s: String,
    }

    let mut diff = Vec::new();
    for i in 0..(s.len() - 2) {
        diff.push((s[i..(i + 3)].parse::<isize>().unwrap() - 753).abs());
    }
    println!("{}", diff.iter().min().unwrap());
}
