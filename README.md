# frmwrk

A tiny single-module Python web framework.

## Components

- `frmwrk.py`, the framework: request/response objects, URL routing, template rendering
- `demo.py`, a demo app with templates
- `srvr.py`, a minimal WSGI-compatible HTTP server
- `clnt.py`, a minimal HTTP client REPL

## Running the demo

With wsgiref:

    python demo.py

With gunicorn:

    uv run gunicorn demo:app

With the built-in server:

    python srvr.py demo:app

## Using the client

    python clnt.py localhost:8000
    > GET /
    > GET /greet/Ben
    > POST / name=Ben
