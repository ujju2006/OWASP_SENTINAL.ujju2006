import secrets
from flask import Flask, render_template, request, url_for, session, abort
import json
import os
import uuid
from scanner.engine import ScannerEngine

app = Flask(__name__)
app.secret_key = secrets.token_hex(64)
# Harden Session Cookies
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
)

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403, "CSRF Token Validation Failed")

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

# Basic security headers for the scanner itself
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com cdnjs.cloudflare.com; font-src fonts.gstatic.com cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net;"
    return response

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        
        # Ensure url starts with scheme
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
            
        try:
            engine = ScannerEngine(url)
            results, score = engine.run_full_scan()
            
            os.makedirs("reports", exist_ok=True)
            report_id = str(uuid.uuid4())
            with open(f"reports/results_{report_id}.json", "w") as f:
                json.dump(results, f, indent=4)
                
            return render_template("dashboard.html", results=results, score=score, target_url=url, report_id=report_id)
        except Exception as e:
            # Handle SSRF blocks or other top-level errors gracefully
            return render_template("index.html", error=str(e))
            
    return render_template("index.html")

if __name__ == "__main__":
    # Removed debug=True to prevent Werkzeug PIN RCE exploits
    app.run(host="127.0.0.1", port=5002)
