extern crate communicator;

fn main() {
    communicator::client::connect();
    communicator::network::connect();
    communicator::network::server::connect();

    a::series::of::nested_modules();
    of::nested_modules();
    nested_modules();

    let red = Red;
    let yellow = Yellow;
    let green = TrafficLight::Green;
    let green = Green;
}

pub mod a {
    pub mod series {
        pub mod of {
            pub fn nested_modules() {
                println!("nest function!")
            }
        }
    }
}

// 外部からもアクセス可能
pub use a::series::of;
use a::series::of::nested_modules;

enum TrafficLight {
    Red,
    Yellow,
    Green,
}

// 複数指定することも可能
use TrafficLight::{Red, Yellow};
// * ですべてを取り込む（非推奨）
use TrafficLight::*;
