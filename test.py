from flask import Flask, render_template, request, g, jsonify

app = Flask(__name__, static_url_path='/assets', static_folder="assets")
#cl = None
@app.route("/")
def landing():
    userid = ""
    error_message = ""
    host_url = request.headers["Host"]
    return render_template("landing.html", **locals())




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True);