use proconio::{fastout, input};

#[fastout]
fn main() {
    input! {
        max_num: usize,
    }

    let init: usize = 0;
    let mut counter: usize = 0;
    let flag: [bool; 3] = [false, false, false];

    // &mut : 可変の参照
    saiki(init, &mut counter, flag, max_num);
    println!("{}", counter);
}

fn saiki(n: usize, counter: &mut usize, flag: [bool; 3], max_num: usize) {
    // ベースケース
    if n > max_num {
        return;
    }

    // 753数の判定
    if flag.iter().all(|&x| x == true) {
        // 再代入
        *counter += 1;
    }

    // 7を加えていく
    saiki(n * 10 + 7, counter, [true, flag[1], flag[2]], max_num);

    // 5を加えていく
    saiki(n * 10 + 5, counter, [flag[0], true, flag[2]], max_num);

    // 3を加えていく
    saiki(n * 10 + 3, counter, [flag[0], flag[1], true], max_num);
}
