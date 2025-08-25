from flask import Flask, render_template, request, session, redirect, url_for
from .posts import create_posts_table, insert_post, select_all_posts, select_post_by_id
from .connection import display_tables
import os
from uuid import uuid4
from werkzeug.utils import secure_filename


app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
   return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
   title = request.form["title"].strip()
   content = request.form["content"].strip()


   image_file = request.files.get("image")
   image_name = None


   if image_file and image_file.filename and allowed_file(image_file.filename):
       ext = image_file.filename.rsplit(".", 1)[1].lower()
       # Unique, safe filename
       safe_name = secure_filename(f"{uuid4().hex}.{ext}")
       image_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
       image_file.save(image_path)
       image_name = safe_name


   insert_post(title, content, image_name)
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
