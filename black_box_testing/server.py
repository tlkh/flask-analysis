from flask import render_template, request, make_response, redirect
from flask import Flask
import time
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", default=False,
                    help="Use debug mode to launch Flask server")
parser.add_argument("--ssl", action="store_true", default=False,
                    help="Use self-signed SSL with Flask server")
parser.add_argument("--port", type=int, default=5000)
args = parser.parse_args()


app = Flask("Flask Web App")

if args.ssl:
    @app.before_request
    def before_request():
        """hook to redirect to HTTPS, does not seem to work on localhost"""
        scheme = request.headers.get('X-Forwarded-Proto')
        if scheme and scheme == 'http' and request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)


@app.route("/")
def hello_world():
    return render_template("home.html")


@app.route("/inputs", methods=["GET", "POST"])
def inputs_page(data="No data"):
    if request.method == "POST":
        data = request.form["text"]
    return render_template("inputs.html", data=data)


@app.route("/inputs_unsafe", methods=["GET", "POST"])
def inputs_page_unsafe(data="No data"):
    if request.method == "POST":
        data = request.form["text"]
    return render_template("inputs_unsafe.html", data=data)


@app.route("/test_headers")
def test_headers_page():
    r = make_response(render_template("home.html"))
    r.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    r.headers["Content-Security-Policy"] = "default-src 'self'"
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["X-XSS-Protection"] = "1; mode=block"
    r.headers["Server"] = "None"
    return r


@app.route("/test_cookie_options")
def test_cookies_page():
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=600
    )
    r = make_response(render_template("home.html"))
    cookie_name = str(int(time.time()))
    #r.set_cookie("username", "flask", secure=True, httponly=True, samesite="Lax")
    r.set_cookie(cookie_name, "1", max_age=1)
    r.set_cookie(cookie_name+"_persistent", "2", max_age=100)
    return r


@app.route("/test_exception")
def test_exception_page():
    _ = 1/0
    return "Exception"


if __name__ == "__main__":
    print("Launching with adhoc SSL certificate:", args.ssl)
    if args.ssl:
        app.run(host="127.0.0.1", port=args.port, debug=args.debug,
                ssl_context=("cert.pem", "key.pem"))
    else:
        app.run(host="127.0.0.1", port=args.port, debug=args.debug)
