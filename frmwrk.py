"""A minimal web framework.  Use with wsgiref, gunicorn, or srvr.py"""

import re
from pathlib import Path
from urllib.parse import parse_qs


class App:
    """A WSGI application.  Routes requests to view functions based on URL patterns"""

    def __init__(self, urls):
        self.urls = urls

    def __call__(self, environ, start_response):
        # This is the WSGI interface: the server calls app(environ, start_response)
        request = Request(environ)
        for path, view_fn in self.urls:
            kwargs = match(path, request.path)
            if kwargs is not None:
                response = view_fn(request, **kwargs)
                break
        start_response(response.status, response.headers)
        return [response.body]


def render(template, context=None):
    return Response(template=template, context=context)


def redirect(location):
    return Response(text="", status=302, headers=[("Location", location)])


class Request:
    """An HTTP request

    Wraps the WSGI environ dict into a friendlier object.
    """

    def __init__(self, environ):
        self.method = environ["REQUEST_METHOD"]
        self.path = environ["PATH_INFO"]
        if self.method == "POST":
            # Parse URL-encoded form data (e.g. "x=1&y=2")
            body = environ["wsgi.input"].read(int(environ["CONTENT_LENGTH"]))
            self.POST = {k: v[0] for k, v in parse_qs(body.decode()).items()}


class Response:
    """An HTTP response

    Body comes from text or a template file + context.
    """

    def __init__(self, text=None, template=None, context=None, status=200, headers=None):
        if template:
            raw = Path(template).read_text()
            body = raw.format(**(context or {}))
        else:
            body = text
        status_phrases = {200: "OK", 302: "Found", 404: "Not Found"}
        self.status = f"{status} {status_phrases.get(status, '')}"
        self.headers = headers or [("Content-Type", "text/html")]
        self.body = body.encode()


def match(pattern, path):
    """Match a URL pattern like "/greet/[name]" against a path

    Returns a dict of captured values, or None if no match.
    """

    # Turn "/greet/[name]" into "/greet/([^/]+)" and extract ["name"]
    names = re.findall(r"\[(\w+)\]", pattern)
    regex = re.sub(r"\[\w+\]", r"([^/]+)", pattern)
    m = re.fullmatch(regex, path)
    if m:
        return dict(zip(names, m.groups()))
    return None
