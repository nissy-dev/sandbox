use std::error::Error;

use extism::*;
use walkdir::WalkDir;

fn main() -> Result<(), Box<dyn Error>> {
    let path = std::env::args().nth(2).expect("no path given");

    let url =
        Wasm::url("https://github.com/extism/plugins/releases/latest/download/count_vowels.wasm");
    let manifest = Manifest::new([url]);
    let mut plugin = Plugin::new(&manifest, [], true).unwrap();

    let res = plugin
        .call::<&str, &str>("count_vowels", "Hello, world!")
        .unwrap();
    println!("{}", res);

    // walk directory
    for entry in WalkDir::new("./") {
        println!("{}", entry?.path().display());
    }

    Ok(())
}
