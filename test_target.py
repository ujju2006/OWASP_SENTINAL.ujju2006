from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<body>
    <h1>Complex Target Application</h1>
    <ul>
        <li><a href="/login">Login Area</a></li>
        <li><a href="/search">Search Products</a></li>
        <li><a href="/profile?id=1">View Profile</a></li>
        <li><a href="/read_file?file=doc.txt">Read Docs</a></li>
        <li><a href="/ping">Ping Utility</a></li>
    </ul>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HOME_TEMPLATE)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return "Login Attempt"
    return """
    <form action="/login" method="POST">
        <input type="text" name="user">
        <input type="password" name="pass">
        <button type="submit">Go</button>
    </form>
    """

@app.route("/search")
def search():
    query = request.args.get('q', '')
    return f"<h2>Results for {query}</h2>"

@app.route("/profile")
def profile():
    pid = request.args.get('id', '')
    if "SLEEP" in pid or "DELAY" in pid.upper():
        import time; time.sleep(5)
    if "'" in pid:
        return "SQL syntax error near user_id", 500
    return "Profile page"

@app.route("/read_file")
def read_file():
    fname = request.args.get('file', '')
    if "passwd" in fname:
        return "root:x:0:0:root:/root:/bin/bash"
    if "win.ini" in fname:
        return "; for 16-bit app support"
    return "File contents"

@app.route("/ping", methods=["GET", "POST"])
def ping():
    if request.method == "POST":
        target = request.form.get("ip", "")
        if "id" in target:
            return "uid=1000(user) gid=1000(user)"
        if "whoami" in target:
            return "\\Users\\admin"
        if "ping" in target:
            import time; time.sleep(3)
            return "Pinging..."
    return """
    <form action="/ping" method="POST">
        <input type="text" name="ip" placeholder="8.8.8.8">
        <button type="submit">Ping</button>
    </form>
    """
    
# Trigger directory listing detection if crawler visits certain endpoint
@app.route("/assets/")
def assets():
    return "Index of /assets/ <br> <a href='app.js'>app.js</a>"

@app.route("/headers_test")
def headers():
    resp = app.response_class("test", status=200)
    resp.headers["Set-Cookie"] = "session=123" # Insecure cookie
    return resp

if __name__ == "__main__":
    app.run(port=5001, debug=True)
