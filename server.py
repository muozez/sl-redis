import socket
import threading
import signal
import sys
import time

HOST = "127.0.0.1"
PORT = 1717

store = {}
lock = threading.Lock()
running = True
server_socket = None

def resp_simple(msg):
    return f"+{msg}\r\n".encode()

def resp_error(msg):
    return f"-ERR {msg}\r\n".encode()

def resp_bulk(value):
    if value is None:
        return b"$-1\r\n"
    return f"${len(value)}\r\n{value}\r\n".encode()

def resp_int(num):
    return f":{num}\r\n".encode()

def parse_resp(data):
    lines = data.decode().split("\r\n")
    argc = int(lines[0][1:])
    args = []
    i = 1
    for _ in range(argc):
        length = int(lines[i][1:])
        i += 1
        args.append(lines[i])
        i += 1
    return args

def is_expired(expire_at):
    return expire_at and time.time() > expire_at

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    with conn:
        while running:
            data = conn.recv(4096)
            if not data:
                break

            try:
                args = parse_resp(data)
            except Exception:
                conn.sendall(resp_error("protocol error"))
                continue

            cmd = args[0].upper()

            if cmd == "GET" and len(args) == 2:
                key = args[1]
                with lock:
                    item = store.get(key)
                    if not item:
                        conn.sendall(resp_bulk(None))
                        continue

                    value, expire_at = item
                    if is_expired(expire_at):
                        del store[key]
                        conn.sendall(resp_bulk(None))
                        continue

                conn.sendall(resp_bulk(value))

            elif cmd == "SET" and len(args) >= 3:
                key = args[1]
                value = args[2]
                expire_at = None

                if len(args) == 5 and args[3].upper() == "EX":
                    expire_at = time.time() + int(args[4])

                with lock:
                    store[key] = (value, expire_at)

                conn.sendall(resp_simple("OK"))

            elif cmd == "TTL" and len(args) == 2:
                key = args[1]
                with lock:
                    item = store.get(key)
                    if not item:
                        conn.sendall(resp_int(-2))
                        continue

                    _, expire_at = item
                    if expire_at is None:
                        conn.sendall(resp_int(-1))
                        continue

                    ttl = int(expire_at - time.time())
                    conn.sendall(resp_int(max(ttl, -2)))

            else:
                conn.sendall(resp_error("unknown command"))

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
        print("RESP server listening...")

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
