import re
from flask import render_template, request, make_response, redirect
from flask import Flask
import time
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--debug",
    action="store_true",
    default=False,
    help="Use debug mode to launch Flask server",
)
parser.add_argument(
    "--ssl",
    action="store_true",
    default=False,
    help="Use self-signed SSL with Flask server",
)
parser.add_argument("--port", type=int, default=5000)
args = parser.parse_args()

app = Flask("Flask Web App")


def check_sql_injection(input_text):
    pattern = r"\b(and|like|exec|insert|select|drop|grant|alter|delete|update|count|chr|mid|master|truncate|char|delclare|or)\b|(\*|;)"
    print(input_text)
    input_text = str(input_text).lower()
    return re.search(pattern, input_text)


global_alert = "None"


@app.before_request
def before_request():
    global global_alert
    # prevent SQL injection
    if request.json:
        for v in request.json.values():
            r = check_sql_injection(v)
            if r:
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                warn_string = "Possible SQL injection detected @ " + date_time
                print(warn_string)
                global_alert = warn_string
    if request.form:
        for v in request.form.values():
            r = check_sql_injection(v)
            if r:
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                warn_string = "Possible SQL injection detected @ " + date_time
                print(warn_string)
                global_alert = warn_string
    if args.ssl:
        # hook to redirect to HTTPS, does not seem to work on localhost
        scheme = request.headers.get("X-Forwarded-Proto")
        if scheme and scheme == "http" and request.url.startswith("http://"):
            url = request.url.replace("http://", "https://", 1)
            code = 301
            return redirect(url, code=code)


@app.route("/")
def hello_world():
    return render_template("home.html")


@app.route("/inputs", methods=["GET", "POST"])
def inputs_page(data="No data"):
    global global_alert
    if request.method == "POST":
        data = request.form["text"]
    r = make_response(render_template("inputs.html", data=data, alert=global_alert))
    r.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    r.headers["Content-Security-Policy"] = "default-src 'self'"
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["X-XSS-Protection"] = "1; mode=block"
    r.headers["Server"] = "None"
    return r


@app.route("/inputs_unsafe", methods=["GET", "POST"])
def inputs_page_unsafe(data="No data"):
    global global_alert
    if request.method == "POST":
        data = request.form["text"]
    return render_template("inputs_unsafe.html", data=data, alert=global_alert)


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
        PERMANENT_SESSION_LIFETIME=600,
    )
    r = make_response(render_template("home.html"))
    cookie_name = str(int(time.time()))
    # r.set_cookie("username", "flask", secure=True, httponly=True, samesite="Lax")
    r.set_cookie(cookie_name, "1", max_age=1)
    r.set_cookie(cookie_name + "_persistent", "2", max_age=100)
    return r


@app.route("/test_exception")
def test_exception_page():
    _ = 1 / 0
    return "Exception"


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    print("Launching with adhoc SSL certificate:", args.ssl)
    if args.ssl:
        app.run(
            host="127.0.0.1",
            port=args.port,
            debug=args.debug,
            ssl_context=("cert.pem", "key.pem"),
        )
    else:
        app.run(host="127.0.0.1", port=args.port, debug=args.debug)
