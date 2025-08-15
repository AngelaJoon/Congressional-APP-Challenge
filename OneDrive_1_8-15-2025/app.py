from flask import Flask, render_template, request, session, redirect, url_for
from .posts import create_posts_table, insert_post, select_all_posts, select_post_by_id
from .connection import display_tables

app = Flask(__name__)

with app.app_context():
    create_posts_table()

app.secret_key = "gUG*7BNmM*[*hUd7&y6hb}GlTcub`C"

my_username = "cody"
my_password = "wiz92ard"


@app.route("/")
def home():
    posts = select_all_posts()
    return render_template("home.html", posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == my_username and password == my_password:
            session["logged_in"] = True
            return redirect(url_for("editor"))
        else:
            return render_template("login.html", failed_login=True)

    if session.get("logged_in"):
        return redirect(url_for("editor"))
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("login"))


@app.route("/editor")
def editor():
    if session.get("logged_in"):
        return render_template("editor.html")
    else:
        return redirect(url_for("login"))


@app.route("/posts/create", methods=["POST"])
def create_post():
    title = request.form["title"]
    content = request.form["content"]
    insert_post(title, content)
    return redirect(url_for("home"))


@app.route("/tables")
def tables():
    return display_tables()

@app.route("/blog/<post_id>")
def blog(post_id):
    post = select_post_by_id(post_id)
    if post:
        return render_template("blog.html", post=post)
    else:
        return "post not found"