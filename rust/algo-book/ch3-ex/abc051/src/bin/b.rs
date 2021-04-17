use proconio::{fastout, input};

#[fastout]
fn main() {
    input! {
        (k, s): (isize, isize),
    }

    let mut cnt = 0;
    for a in 0..(k + 1) {
        for b in 0..(k + 1) {
            let tmp = s - (a + b);
            if tmp >= 0 && tmp <= k {
                cnt += 1
            }
        }
    }
    println!("{}", cnt)
}
