pub mod client;
pub mod network;

// mod netwrok {
//     fn connect() {}

//     mod server {
//         fn connect() {}
//     }
// }

// mod client {
//     fn connect() {}
// }

mod outermost {
    pub fn middle_function() {}

    pub fn middle_secret_function() {}

    pub mod inside {
        pub fn inner_function() {
            super::middle_secret_function();
        }

        pub fn secret_function() {}
    }
}

fn _try_me() {
    outermost::middle_function();
    outermost::middle_secret_function();
    outermost::inside::inner_function();
    outermost::inside::secret_function();
}

#[cfg(test)]
mod tests {
    use super::client;
    #[test]
    fn it_works() {
        super::client::connect();
        client::connect();
        assert_eq!(2 + 2, 4);
    }
}
