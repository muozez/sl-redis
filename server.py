import socket
import threading

HOST = "127.0.0.1"
PORT = 1717

store = {
    "name": "muozez",
    "status": "active"
}

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            print(f"{addr} -> {message}")

            if message.upper().startswith("GET "):
                key = message[4:].strip()
                value = store.get(key, "KEY_NOT_FOUND")
                conn.sendall(value.encode())
            else:
                conn.sendall(b"INVALID_COMMAND")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server listening...")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            thread.start()

if __name__ == "__main__":
    main()
