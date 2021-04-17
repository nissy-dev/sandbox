use proconio::{fastout, input};

#[fastout]
fn main() {
    input! {
        n: usize,
        mut a: [usize; n]
    }

    let mut cnt = 0;
    while true {
        for i in 0..n {
            let quotient = a[i] / 2;
            let remainder = a[i] % 2;
            if remainder != 0 {
                println!("{}", cnt);
                return;
            }
            a[i] = quotient;
        }
        cnt += 1;
    }
    println!("{}", cnt)
}
