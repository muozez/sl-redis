import socket
import threading
import signal
import sys

HOST = "127.0.0.1"
PORT = 1717

store = {
    "name": "muozez",
    "status": "active"
}

lock = threading.Lock()
server_socket = None
running = True

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    with conn:
        while running:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode().strip()
                print(f"{addr} -> {message}")

                parts = message.split(" ", 2)
                command = parts[0].upper()

                if command == "GET" and len(parts) == 2:
                    key = parts[1]
                    with lock:
                        value = store.get(key, "KEY_NOT_FOUND")
                    conn.sendall((value + "\r\n").encode())

                elif command == "SET" and len(parts) == 3:
                    key, value = parts[1], parts[2]
                    with lock:
                        store[key] = value
                    conn.sendall(b"200 OK\r\n")

                else:
                    conn.sendall(b"INVALID_COMMAND\r\n")

            except ConnectionResetError:
                break

    print(f"Disconnected: {addr}")

def shutdown_handler(sig, frame):
    global running
    print("\nShutting down server...")
    running = False
    if server_socket:
        server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)

def main():
    global server_socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        server_socket = s
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("Server listening...")

        while running:
            try:
                conn, addr = s.accept()
                threading.Thread(
                    target=handle_client,
                    args=(conn, addr),
                    daemon=True
                ).start()
            except OSError:
                break

if __name__ == "__main__":
    main()
