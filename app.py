import os, sqlite3, secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "studio.db")
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("STUDIO_SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif","webp","mp4","mov","webm","pdf","xml","txt","csv","docx","xlsx","zip"}

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER NOT NULL,
            receiver_id INTEGER, body TEXT, file_name TEXT, created_at TEXT NOT NULL)""")
        admin = con.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not admin:
            con.execute("INSERT INTO users(username,email,password_hash,is_admin,created_at) VALUES(?,?,?,?,?)",
                ("admin","admin@example.local",generate_password_hash("ChangeMe-123!"),1,datetime.now().isoformat(timespec="seconds")))

init_db()

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        with db() as con:
            user = con.execute("SELECT is_admin FROM users WHERE id=?", (session["user_id"],)).fetchone()
        if not user or not user["is_admin"]:
            abort(403)
        return fn(*args, **kwargs)
    return wrapped

def current_user():
    if not session.get("user_id"): return None
    with db() as con:
        return con.execute("SELECT id,username,email,is_admin,created_at FROM users WHERE id=?", (session["user_id"],)).fetchone()

@app.context_processor
def inject_user():
    return {"current_user": current_user()}

@app.route("/")
def home():
    return render_template("index.html", page="home")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if len(username) < 3 or "@" not in email or len(password) < 8:
            flash("Username (3+ characters), valid email, and password (8+ characters) required.", "error")
        else:
            try:
                with db() as con:
                    con.execute("INSERT INTO users(username,email,password_hash,is_admin,created_at) VALUES(?,?,?,?,?)",
                        (username,email,generate_password_hash(password),0,datetime.now().isoformat(timespec="seconds")))
                flash("Account created. Please sign in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username or email is already registered.", "error")
    return render_template("auth.html", mode="register", page="register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        identity = request.form.get("identity","").strip().lower()
        password = request.form.get("password","")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE lower(username)=? OR lower(email)=?", (identity,identity)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("admin") if user["is_admin"] else url_for("home"))
        flash("Incorrect username/email or password.", "error")
    return render_template("auth.html", mode="login", page="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin():
    with db() as con:
        users = con.execute("SELECT id,username,email,is_admin,created_at FROM users ORDER BY id DESC").fetchall()
        messages = con.execute("""SELECT messages.*, users.username AS sender FROM messages
                                  JOIN users ON users.id=messages.sender_id ORDER BY messages.id DESC LIMIT 30""").fetchall()
    return render_template("admin.html", users=users, messages=messages, page="admin")

@app.route("/admin/user/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_admin(user_id):
    if user_id == session["user_id"]:
        flash("You cannot change your own admin status here.", "error")
    else:
        with db() as con:
            row = con.execute("SELECT is_admin FROM users WHERE id=?", (user_id,)).fetchone()
            if row:
                con.execute("UPDATE users SET is_admin=? WHERE id=?", (0 if row["is_admin"] else 1, user_id))
                flash("User role updated.", "success")
    return redirect(url_for("admin"))

@app.route("/chat", methods=["GET","POST"])
@login_required
def chat():
    if request.method == "POST":
        body = request.form.get("body","").strip()
        upload = request.files.get("file")
        saved_name = None
        if upload and upload.filename:
            original = secure_filename(upload.filename)
            ext = original.rsplit(".",1)[-1].lower() if "." in original else ""
            if ext not in ALLOWED_EXTENSIONS:
                flash("File type not allowed.", "error")
                return redirect(url_for("chat"))
            saved_name = secrets.token_hex(8) + "_" + original
            upload.save(os.path.join(UPLOAD_DIR, saved_name))
        if body or saved_name:
            with db() as con:
                con.execute("INSERT INTO messages(sender_id,receiver_id,body,file_name,created_at) VALUES(?,?,?,?,?)",
                    (session["user_id"],None,body,saved_name,datetime.now().isoformat(timespec="seconds")))
        return redirect(url_for("chat"))
    with db() as con:
        messages = con.execute("""SELECT messages.*, users.username AS sender FROM messages
                                  JOIN users ON users.id=messages.sender_id ORDER BY messages.id ASC LIMIT 200""").fetchall()
    return render_template("chat.html", messages=messages, page="chat")

@app.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.route("/browser", methods=["GET"])
def browser():
    query = request.args.get("q","").strip()
    return render_template("browser.html", query=query, page="browser")

@app.route("/tools")
@login_required
def tools_page():
    return render_template("tools.html", page="tools")

@app.errorhandler(403)
def forbidden(_):
    return render_template("message.html", title="Access denied", message="This area is for administrators only.", page=""), 403

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
