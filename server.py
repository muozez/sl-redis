import socket
import threading

HOST = "127.0.0.1"
PORT = 1717

store = {
    "name": "muozez",
    "status": "active"
}

lock = threading.Lock()

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    with conn:
        while True:
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
                conn.sendall(value.encode())
            elif command == "SET" and len(parts) == 3:
                key, value = parts[1], parts[2]
                with lock:
                    store[key] = value
                conn.sendall(b"200 OK")
            else:
                conn.sendall(b"INVALID_COMMAND")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server listening...")

        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()

if __name__ == "__main__":
    main()
