import socket

HOST = "127.0.0.1"
PORT = 1717

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server listening...")
    conn, addr = s.accept()

    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode().strip()
            print("Received:", message)

            if message.upper().startswith("GET "):
                key = message[4:].strip()
                value = store.get(key, "KEY_NOT_FOUND")
                conn.sendall(value.encode())
            else:
                conn.sendall(b"INVALID COMMAND")
