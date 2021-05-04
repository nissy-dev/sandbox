import time
import socket
from concurrent.futures import ThreadPoolExecutor


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 8080))
        server_sock.listen()
        handle_connection(server_sock)


def handle_connection(sock):
    with ThreadPoolExecutor(max_workers=1000) as executor:
        while True:
            (connect, address) = sock.accept()
            print("address: ", address)

            # リクエストを受け取ってレスポンスを返す
            executor.submit(server_response, connect)


def server_response(connect):
    req = connect.recv(1024).decode("utf-8")
    res_start_line = req.split("\r\n")[0]
    if res_start_line == "GET /echo HTTP/1.1":
        res_start_line = "HTTP/1.1 200 OK\r\n\r\n"
        res_body = "Hello, World!\r\n"
        connect.send(bytes(res_start_line + res_body, "utf-8"))
    elif res_start_line == "GET /sleep HTTP/1.1":
        time.sleep(10)
        res_start_line = "HTTP/1.1 200 OK\r\n\r\n"
        res_body = "Server just fell asleep for a moment...\r\n"
        connect.send(bytes(res_start_line + res_body, "utf-8"))
    else:
        print("Empty Response...")

    # コネクションのシャットダウン
    connect.shutdown(0)
    connect.close()


if __name__ == "__main__":
    start_server()
