"""A minimal HTTP client REPL.  Usage: python clnt.py localhost:8000"""

import socket
import sys


def main():
    """REPL loop.  Enter: METHOD /path [body]  e.g. POST /greet name=Ben"""

    host, port = sys.argv[1].split(":")
    port = int(port)

    while True:
        line = input("> ").strip()
        parts = line.split(" ", 2)
        method = parts[0].upper()
        path = parts[1]
        body = parts[2] if len(parts) > 2 else None

        response = send_request(host, port, method, path, body)
        print(response)


def send_request(host, port, method, path, body=None):
    """Send an HTTP request and return the full response as a string"""

    # Open a TCP connection to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # Build the HTTP request line and headers
    request = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\n"
    if body:
        request += f"Content-Length: {len(body)}\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
    request += "\r\n"
    if body:
        request += body

    sock.sendall(request.encode())

    # Read until we have the full headers
    raw = b""
    while b"\r\n\r\n" not in raw:
        raw += sock.recv(4096)

    header_data, _, rest = raw.partition(b"\r\n\r\n")
    headers = header_data.decode()

    # Read the body based on Content-Length
    content_length = 0
    for line in headers.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":")[1].strip())

    body_data = rest
    while len(body_data) < content_length:
        body_data += sock.recv(4096)

    # Close the connection
    sock.close()

    # Reassemble the full response as a string
    return headers + "\r\n\r\n" + body_data.decode()


if __name__ == "__main__":
    main()
