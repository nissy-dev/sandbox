use whiteread::parse_line;

fn main() {
    let input_str: String = parse_line().unwrap();
    let mut cnt: i32 = 0;
    for i in input_str.chars() {
        if i.to_string() == "1" {
            cnt += 1
        }
    }
    println!("{}", cnt)
}
