use proconio::marker::Chars;
use proconio::{fastout, input};

#[fastout]
fn main() {
    input! {
        s: Chars
    }

    // 1 << d := pow(2, d)
    let n = s.len();
    let mut sum: usize = 0;
    for bit in 0..(1 << (n - 1)) {
        // bitフラグの取得
        // let mut bit_flag = vec![];
        // for i in 0..(n - 1) {
        //     if (bit & (1 << i)) != 0 {
        //         bit_flag.push(i);
        //     }
        // }

        let mut start = 0;
        for i in 0..(n - 1) {
            // bitwise operator
            // https://www.tutorialspoint.com/rust/rust_bitwise_operators.htm
            if (bit & (1 << i)) != 0 {
                let end = i + 1;
                let str_num: String = s[start..end].iter().collect();
                sum += str_num.parse::<usize>().unwrap();
                start = end;
            }
        }
        let str_num: String = s[start..].iter().collect();
        sum += str_num.parse::<usize>().unwrap();
    }

    println!("{:?}", sum);
}
