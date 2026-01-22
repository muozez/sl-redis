# SL-Redis

SL-Redis is a very simple Redis-like in-memory key–value server written in Python.

It implements a minimal subset of the Redis RESP protocol and supports basic commands such as `SET`, `GET`, and `TTL`, including key expiration.

## Features
- In-memory key–value storage
- RESP protocol parsing
- `SET` with optional `EX` (expire in seconds)
- `GET` command
- `TTL` command
- Multi-client support using threads

## Usage
Run the server:
```bash
python server.py
````

Connect using `redis-cli`:

```bash
redis-cli -p 1717
```

## Notes

This project is for learning and experimentation purposes only and is not intended for production use.