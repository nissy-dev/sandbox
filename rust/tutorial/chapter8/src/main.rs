use itertools::join;
use std::collections::HashMap;
use std::io;

fn main() {
    let v: Vec<i32> = Vec::new();
    let mut v = Vec::new();
    v.push(5);
    v.push(6);
    v.push(7);
    v.push(8);
    // type inference, i32 (use vec! macro)
    let v = vec![1, 2, 3];

    let third: &i32 = &v[2];
    println!("The third element is {}", third);

    // get だと、Optionが返り値
    match v.get(2) {
        Some(third) => println!("The third element is {}", third),
        None => println!("There is no third element."),
    }

    let v = vec![1, 2, 3, 4, 5];
    // happen panic!
    // let _does_not_exist = &v[100];
    let does_not_exist = v.get(100);
    println!("The third element is {:#?}", does_not_exist);

    let mut v = vec![1, 2, 3, 4, 5];
    let first = &v[0];
    // 借用規則のため、mutableでもpushはできない
    // v.push(6);
    println!("The first element is: {}", first);

    let v = vec![100, 32, 57];
    for i in &v {
        println!("{}", i);
    }

    let mut v = vec![100, 32, 57];
    for i in &mut v {
        // 可変参照が参照している値を変更する、参照外し(15章で詳しく触れる)
        *i += 50;
    }
    for i in &v {
        println!("{}", i);
    }

    enum SpreadsheetCell {
        Int(i32),
        Float(f64),
        Text(String),
    }

    // NG
    // let test = vec![1, "test"];
    // enum の要素なら中身の型を変えられる (enum型で認識される)
    let _row = vec![
        SpreadsheetCell::Int(3),
        SpreadsheetCell::Text(String::from("blue")),
        SpreadsheetCell::Float(10.12),
    ];

    // every codes is the same
    let _s = String::from("initial contents");
    let data = "initial content";
    let _s = data.to_string();
    let _s = "initial contents".to_string();

    // encoded UTF-8
    let _hello = String::from("السلام عليكم");
    let _hello = String::from("Dobrý den");
    let _hello = String::from("Hello");
    let _hello = String::from("שָׁלוֹם");
    let _hello = String::from("नमस्ते");
    let _hello = String::from("こんにちは");
    let _hello = String::from("안녕하세요");
    let _hello = String::from("你好");
    let _hello = String::from("Olá");
    let _hello = String::from("Здравствуйте");
    let _hello = String::from("Hola");

    let mut s = String::from("foo");
    s.push_str("bar");
    println!("{}", s);

    let mut s1 = String::from("foo");
    let s2 = "bar";
    s1.push_str(s2);
    println!("s1 is {}", s1);
    // s2 is
    println!("s2 is {}", s2);

    let mut lo = String::from("lo");
    let l = 'l';
    // push は char 型
    lo.push(l);
    println!("lo is {}", lo);
    println!("l is {}", l);

    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");
    // note s1 has been moved here and can no longer be used
    // &String -> &str の型のキャストがおきている
    let s3 = s1 + &s2;
    // &str への足し算はできない
    // let s3 = &s1 + &s2;
    println!("{}", s3);

    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");
    let s = s1 + "-" + &s2 + "-" + &s3;
    println!("{}", s);

    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");
    let s = format!("{}-{}-{}", s1, s2, s3);
    println!("{}", s);
    println!("{}", s1);

    let s1 = String::from("hello");
    // rust の文字列は、添字アクセスを許さない
    // let h = s1[0];

    let len = String::from("Hola").len();
    println!("string length is {}", len);
    let len = String::from("Здравствуйте").len();
    // 文字数の12にはならない
    // 1文字で2byte占有するので、添字アクセスは適さない
    println!("string length is {}", len);

    let hello = "Здравствуйте";
    let s = &hello[0..4];
    println!("{}", s);
    // panic!
    // let s = &hello[0..1];

    for c in "नमस्ते".chars() {
        println!("{}", c);
    }

    for b in "こんにちは".chars() {
        println!("{}", b);
    }

    for b in "こんにちは".bytes() {
        println!("{}", b);
    }

    let mut scores = HashMap::new();
    scores.insert(String::from("blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    let teams = vec![String::from("Blue"), String::from("Yellow")];
    let initial_scores = vec![10, 50];
    // 推論は HashMap の key と value の型はしてくれる
    let mut _scores: HashMap<_, _> = teams.into_iter().zip(initial_scores.into_iter()).collect();

    let field_name = String::from("Favorite color");
    let field_value = String::from("Blue");

    let mut map = HashMap::new();
    map.insert(field_name, field_value);
    // field_name's ownership has HashMap..
    // println!("{}", field_name)

    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);
    let team_name = String::from("Blue");
    let score = scores.get(&team_name);
    println!("{:?}", score);

    // loop でとりだせる
    for (key, value) in &scores {
        println!("{}: {}", key, value);
    }

    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Blue"), 25);
    println!("{:?}", scores);

    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);
    // key の確認を entry で行い、or_insert で mutable な参照を返す
    scores.entry(String::from("Yellow")).or_insert(50);
    scores.entry(String::from("Blue")).or_insert(50);
    println!("{:?}", scores);

    let text = "hello world wonderful world";
    let mut map = HashMap::new();
    for word in text.split_whitespace() {
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }
    println!("{:?}", map);

    let mut values = vec![6.2, 3.0, 2.3, 5.8, 5.6];
    let mean = mean(&values);
    println!("mean is {}", mean);

    let median = median(&mut values);
    println!("median is {}", median);

    let values = vec![3, 3, 2, 1, 5, 7, 5, 3, 8, 4, 3, 5, 5];
    let mode = mode(&values);
    println!("mode is {:?}", mode);

    let value = "first";
    println!("{}", pig_laten(value));
    let value = "apple";
    println!("{}", pig_laten(value));

    text_interface();
}

fn mean(values: &Vec<f64>) -> f64 {
    let sum: f64 = values.iter().sum();
    let length = values.len();
    sum / length as f64
}

fn median(values: &mut Vec<f64>) -> f64 {
    // see: https://users.rust-lang.org/t/how-to-sort-a-vec-of-floats/2838
    values.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let length = values.len();
    let mid = &length / 2;
    if (&length % 2) == 0 {
        (values[mid - 1] + values[mid]) / 2.0
    } else {
        values[mid]
    }
}

// see : https://gist.github.com/ayoisaiah/185fec1ca98ce44fca1308753182ff2b
fn mode(values: &Vec<i32>) -> Vec<i32> {
    let mut counters = HashMap::new();
    for num in values {
        let count = counters.entry(num).or_insert(0);
        *count += 1;
    }

    // clonedで参照じゃなくなる (&T ->)
    let max_value = counters.values().cloned().max().unwrap_or(0);

    counters
        .into_iter()
        .filter(|&(_, v)| v == max_value)
        .map(|(&k, _)| k)
        .collect()
}

fn pig_laten(input_str: &str) -> String {
    let str_v: Vec<char> = input_str.chars().collect();
    let check = vec!['a', 'b', 'c', 'd', 'e'];
    if check.contains(&str_v[0]) {
        return format!("{}-{}", input_str, "hay");
    }
    format!("{}-{}{}", join(&str_v[1..], ""), &str_v[0], "ay")
}

fn text_interface() {
    println!("Please input operation!");
    println!("ex) Add Sally(name) to Engineering(department)");
    let mut database: HashMap<String, Vec<String>> = HashMap::new();

    loop {
        let mut command = String::new();
        io::stdin()
            .read_line(&mut command)
            .expect("Failed to read line");

        let text: Vec<&str> = command.split_whitespace().collect();
        let operation = text[0].to_lowercase();

        // ライフタイムの問題の解決方法がわからず、コピーした
        let name = text[1].to_string();
        let department = text[3].to_string();
        if operation == "add" {
            database.entry(department).or_insert(vec![]).push(name);
            println!("Member list");
            println!("============================");
            for (key, val) in &mut database {
                println!("Department: {}", key);
                val.sort();
                println!("Member: {}", join(val, ", "));
            }
            println!("============================");
        }
    }
}
