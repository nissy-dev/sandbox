extern crate once_cell;
extern crate socket2;

use once_cell::sync::Lazy;
use socket2::{Domain, Protocol, SockAddr, Socket, Type};
use std::io;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr, SocketAddr, UdpSocket};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Barrier};
use std::thread::{spawn, JoinHandle};
use std::time::Duration;

pub const PORT: u16 = 7645;
// リンクローカル (ルータに転送されない、同一セグメント内で使う) マルチキャストアドレスを設定する
// IPv4 は 224.0.0.0 ~ 224.0.0..225 まで
pub static MULTICAST_IPV4: Lazy<IpAddr> = Lazy::new(|| IpAddr::V4(Ipv4Addr::new(224, 0, 0, 123)));
// IPv6 は FF02:: で始まるアドレス (いくつか予約されたアドレスがあるのでそれ以外)
pub static MULTICAST_IPV6: Lazy<IpAddr> =
    Lazy::new(|| IpAddr::V6(Ipv6Addr::new(0xFF02, 0, 0, 0, 0, 0, 0, 0x0123)));

pub fn multicast_listener(
    response: &'static str,
    client_done: Arc<AtomicBool>,
    addr: SocketAddr,
) -> JoinHandle<()> {
    // A barrier to not start the client test code until after the server is running
    let server_barrier = Arc::new(Barrier::new(2));
    let client_barrier = Arc::clone(&server_barrier);

    let join_handle = spawn(move || {
        // listener creation
        let listener = join_multicast(addr).expect("failed to create listener");
        println!("{}:server: joined: {}", response, addr);

        // Wait for all server to start
        server_barrier.wait();
        println!("{}:server: is ready", response);

        // We'll be looping until the client indicates it is done.
        while !client_done.load(std::sync::atomic::Ordering::Relaxed) {
            // test receive and response code will go here...
            let mut buf = [0u8; 64]; // receive buffer

            // we're assuming failures were timeouts, the client_done loop will stop us
            match listener.recv_from(&mut buf) {
                Ok((len, remote_addr)) => {
                    let data = &buf[..len];

                    println!(
                        "{}:server: got data: {} from: {}",
                        response,
                        String::from_utf8_lossy(data),
                        remote_addr
                    );

                    let responder = new_socket(&remote_addr)
                        .expect("failed to create responder")
                        .into_udp_socket();

                    // we send the response that was set at the method beginning
                    responder
                        .send_to(response.as_bytes(), &remote_addr)
                        .expect("failed to respond");

                    println!("{}:server: sent response to: {:?}", response, remote_addr);
                }
                Err(err) => {
                    println!("{}:server: got an error: {}", response, err);
                }
            }
        }

        println!("{}:server: client is done", response);
    });

    client_barrier.wait();
    join_handle
}

// This will guarantee we always tell the server to stop
struct NotifyServer(Arc<AtomicBool>);

impl Drop for NotifyServer {
    fn drop(&mut self) {
        self.0.store(true, Ordering::Relaxed);
    }
}

fn new_socket(addr: &SocketAddr) -> io::Result<Socket> {
    let domain = if addr.is_ipv4() {
        Domain::ipv4()
    } else {
        Domain::ipv6()
    };

    let socket = Socket::new(domain, Type::dgram(), Some(Protocol::udp()))?;

    // we're going to use read timeouts so that we don't hang waiting for packets
    socket.set_read_timeout(Some(Duration::from_millis(100)))?;

    Ok(socket)
}

fn join_multicast(addr: SocketAddr) -> io::Result<UdpSocket> {
    let socket = new_socket(&addr)?;

    // depending on the IP protocol we have slightly different work
    let ip_addr = addr.ip();
    match ip_addr {
        IpAddr::V4(ref mdns_v4) => {
            // join to the multicast address, with all interfaces
            socket.join_multicast_v4(mdns_v4, &Ipv4Addr::new(0, 0, 0, 0))?;
        }
        IpAddr::V6(ref mdns_v6) => {
            // join to the multicast address, with all interfaces (ipv6 uses indexes not addresses)
            socket.join_multicast_v6(mdns_v6, 0)?;
            socket.set_only_v6(true)?;
        }
    };

    // bind us to the socket address.
    socket.bind(&SockAddr::from(addr))?;
    Ok(socket.into_udp_socket())
}

pub fn new_sender(addr: &SocketAddr) -> io::Result<Socket> {
    let socket = new_socket(&addr)?;

    if addr.is_ipv4() {
        socket.set_multicast_if_v4(&Ipv4Addr::new(0, 0, 0, 0))?;
        socket.bind(&SockAddr::from(SocketAddr::new(
            Ipv4Addr::new(0, 0, 0, 0).into(),
            0,
        )))?;
    } else {
        socket.set_multicast_if_v6(11)?;
        socket.bind(&SockAddr::from(SocketAddr::new(
            Ipv6Addr::new(0, 0, 0, 0, 0, 0, 0, 0).into(),
            0,
        )))?;
    }

    Ok(socket)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ipv4_multicast() {
        test_multicast("ipv4", *MULTICAST_IPV4);
    }

    #[test]
    fn test_ipv6_multicast() {
        test_multicast("ipv6", *MULTICAST_IPV6);
    }

    // Our generic test over different IPs
    fn test_multicast(test: &'static str, addr: IpAddr) {
        assert!(addr.is_multicast());
        let addr = SocketAddr::new(addr, PORT);

        let client_done = Arc::new(AtomicBool::new(false));
        let notify = NotifyServer(Arc::clone(&client_done));

        multicast_listener(test, client_done, addr);

        // client test code send and receive code after here
        println!("{}:client: running", test);

        let message = b"Hello from client!";

        // create the sending socket
        let socket = new_sender(&addr).expect("could not create sender!");
        socket
            .send_to(message, &SockAddr::from(addr))
            .expect("could not send_to!");

        let mut buf = [0u8; 64]; // receive buffer

        // get our expected response
        match socket.recv_from(&mut buf) {
            Ok((len, _)) => {
                let data = &buf[..len];
                let response = String::from_utf8_lossy(data);

                println!("{}:client: got data: {}", test, response);

                // verify it's what we expected
                assert_eq!(test, response);
            }
            Err(err) => {
                println!("{}:client: had a problem: {}", test, err);
                assert!(false);
            }
        }

        // make sure we don't notify the server until the end of the client test
        drop(notify);
    }
}
