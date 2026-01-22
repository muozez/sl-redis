import socket

HOST = "127.0.0.1"
PORT = 1717

store = {
    "name": "muozez",
    "age": 22
}


def handle_client(conn, addr):
    print(f"COnnected {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            print(f"{addr} -> message")

            if message.upper().startswith("GET "):
                key = message[4:].strip()
                value = store.get(key, "KEY_NOT_FOUND")
                conn.sendall(value.encode())
