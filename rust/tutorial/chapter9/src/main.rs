use std::fs::File;
use std::io;
use std::io::ErrorKind;
use std::io::Read;
use std::net::IpAddr;

fn main() {
    // panic!("crash and burn");

    // let v = vec![1, 2, 3];
    // v[99];

    // errorならpanicする
    // let f = File::open("hello.txt").unwrap();
    // unwrap のエラー文言をカスタマイズできる
    // let f = File::open("hello.txt").expect("Failed to open hello.txt");

    let f = File::open("hello.txt");
    let f = match f {
        Ok(file) => file,
        Err(ref error) if error.kind() == ErrorKind::NotFound => match File::create("hello.txt") {
            Ok(fc) => fc,
            Err(e) => panic!("Tried to create file but there was a problem: {:?}", e),
        },
        Err(error) => panic!("There was a problem opening the file: {:?}", error),
    };

    println!("{:?}", f);
    let hello = read_username_from_file();
    println!("{:?}", hello);
    let hello = smart_read_username_from_file();
    println!("{:?}", hello);

    // これは、外から受け取る値をパースしてないので、unwrapでもOK
    let home: IpAddr = "127.0.0.1".parse().unwrap();
    println!("{:?}", home);
}

fn read_username_from_file() -> Result<String, io::Error> {
    let f = File::open("hello.txt");

    let mut f = match f {
        Ok(file) => file,
        Err(e) => return Err(e),
    };

    let mut s = String::new();

    match f.read_to_string(&mut s) {
        Ok(_) => Ok(s),
        Err(e) => Err(e),
    }
}

fn smart_read_username_from_file() -> Result<String, io::Error> {
    // ? で error のケースを終了してくれる
    // let mut f = File::open("hello.txt")?;
    // let mut s = String::new();
    // f.read_to_string(&mut s)?;
    // 連結もできる
    let mut s = String::new();
    File::open("hello.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
