"""Demo app.  Run with: python demo.py / gunicorn demo:app / python srvr.py demo:app"""

from frmwrk import App, render, redirect


# View functions
def home(request):
    if request.method == "POST":
        return redirect(f"/greet/{request.POST['name']}")
    return render("home.html")


def greet(request, name):
    return render("greet.html", {"name": name})


# URL routing: list of (pattern, view_function) pairs, checked in order
urls = [
    ("/", home),
    ("/greet/[name]", greet),
]

# This is the WSGI application object
app = App(urls)


if __name__ == "__main__":
    # Serve with the simple server from Python's wsgiref module
    from wsgiref.simple_server import make_server

    print("Serving on http://localhost:8000")
    make_server("localhost", 8000, app).serve_forever()
