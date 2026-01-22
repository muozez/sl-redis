import socket
import threading
import signal
import sys
import time

HOST = "127.0.0.1"
PORT = 1717

store = {
    "name": ("muozez", None),
    "status": ("active", None)
}

lock = threading.Lock()
server_socket = None
running = True

def is_expired(expire_at):
    return expire_at is not None and time.time() > expire_at

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    with conn:
        while running:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            print(f"{addr} -> {message}")

            parts = message.split(" ")
            command = parts[0].upper()

            if command == "GET" and len(parts) == 2:
                key = parts[1]
                with lock:
                    item = store.get(key)
                    if not item:
                        conn.sendall(b"KEY_NOT_FOUND\r\n")
                        continue

                    value, expire_at = item
                    if is_expired(expire_at):
                        del store[key]
                        conn.sendall(b"KEY_EXPIRED\r\n")
                        continue

                conn.sendall((value + "\r\n").encode())

            elif command == "SET" and len(parts) in (3, 4):
                key = parts[1]
                value = parts[2]
                ttl = int(parts[3]) if len(parts) == 4 else None
                expire_at = time.time() + ttl if ttl else None

                with lock:
                    store[key] = (value, expire_at)

                conn.sendall(b"200 OK\r\n")

            else:
                conn.sendall(b"INVALID_COMMAND\r\n")

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
