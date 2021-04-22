import flask

app = flask.Flask(__name__)

state_dict = {"error": False,
              "running": False,
              "loaded": False,
              "open": False}


@app.route("/")
def return_states():
    return str(state_dict)


@app.route("/open")
def open():
    state_dict["open"] = True
    return str(state_dict)

@app.route("/load")
def load():
    if state_dict["open"] == True:
        state_dict["loaded"] = True
    else:
        state_dict["error"] = True
    return str(state_dict)


@app.route("/close")
def close():
    state_dict["open"] = False
    return str(state_dict)


@app.route("/start")
def start():
    if state_dict["open"] == True:
        state_dict["error"] = True
    if state_dict["error"] == True:
        pass
    else:
        state_dict["running"] = True
    return str(state_dict)


@app.route("/stop")
def stop():
    if state_dict["running"] == True:
        state_dict["running"] = False
    state_dict["error"] = False
    return str(state_dict)


if __name__ == "__main__":
    app.run(debug=True)
