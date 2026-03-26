"""A minimal WSGI-compatible HTTP server.  Usage: python srvr.py demo:app"""

import io
import socket
import sys


def serve(app, host="localhost", port=8000):
    """Listen for HTTP requests and dispatch them to a WSGI app"""

    # Set up a TCP socket and start listening for connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Serving on http://{host}:{port}")

    while True:
        # Wait for a client connection, then read the raw HTTP request
        conn, _ = server_socket.accept()
        data = conn.recv(65536)

        method, path, headers, body = parse_request(data)
        environ = build_environ(method, path, headers, body)

        # WSGI requires us to pass start_response to the app, which it calls
        # with the status and headers before returning the body
        response_started = []

        def start_response(status, response_headers):
            response_started.append((status, response_headers))

        result = app(environ, start_response)
        body = b"".join(result)

        # Build the raw HTTP response
        status, response_headers = response_started[0]
        response_headers.append(("Content-Length", str(len(body))))
        response = f"HTTP/1.1 {status}\r\n"
        for key, value in response_headers:
            response += f"{key}: {value}\r\n"
        response += "\r\n"

        # Send the response back to the client
        conn.sendall(response.encode() + body)
        conn.close()


def parse_request(data):
    """Split raw HTTP bytes into method, path, headers dict, and body bytes"""

    header_data, _, body = data.partition(b"\r\n\r\n")
    lines = header_data.decode().split("\r\n")
    method, path, _ = lines[0].split(" ")
    headers = {}
    for line in lines[1:]:
        key, value = line.split(": ", 1)
        headers[key] = value
    return method, path, headers, body


def build_environ(method, path, headers, body):
    """Build the WSGI environ dict that gets passed to the application"""

    return {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": headers.get("Content-Length", "0"),
        "CONTENT_TYPE": headers.get("Content-Type", ""),
        "wsgi.input": io.BytesIO(body),
    }


if __name__ == "__main__":
    module_name, app_name = sys.argv[1].split(":")
    module = __import__(module_name)
    app = getattr(module, app_name)
    serve(app)
