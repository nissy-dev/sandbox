use proconio::marker::Chars;
use proconio::{fastout, input};

use std::collections::HashMap;

#[fastout]
fn main() {
    input! {
        sa: Chars,
        sb: Chars,
        sc: Chars,
    }

    let mut data = HashMap::new();
    data.insert('a', sa);
    data.insert('b', sb);
    data.insert('c', sc);

    // 以下だと〜コーナーケースにぶち当たる...
    let mut turn = 'a';
    loop {
        if data[&turn].len() == 0 {
            println!("{}", turn.to_ascii_uppercase());
            break;
        }
        turn = data.get_mut(&turn).unwrap().pop().unwrap();
    }

    // 正解
    // let inputs = [sa, sb, sc];
    // let mut idx: [usize; 3] = [0, 0, 0];
    // let mut map: HashMap<char, usize> = HashMap::new();
    // map.insert('a', 0);
    // map.insert('b', 1);
    // map.insert('c', 2);

    // let mut turn = 'a';
    // loop {
    //     let i: usize = idx[map[&turn]];
    //     let s = &inputs[map[&turn]];
    //     if s.len() <= i {
    //         println!("{}", turn.to_uppercase());
    //         break;
    //     }
    //     idx[map[&turn]] += 1;
    //     turn = s[i];
    // }
}
