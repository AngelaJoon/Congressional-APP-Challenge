#!/usr/bin/python3
from flask import (
    Flask, render_template, redirect, url_for, abort,
    request, flash, session
)
import os, uuid, random, math, sqlite3, requests
from datetime import date

from decorators import login_required, welcome_screen
from post_models import (
    create_post_table, delete_post, get_posts, find_post, random_post,
    insert_post, count_posts, paginated_posts, update_post,
    add_image_column, add_rating_column, drop_post_table,
    add_location_columns,   # ✅ import it
)
from user_models import create_user_table, get_user, insert_user
from migrations import add_publish_date, insert_dates
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "LIgp9t3s"

posts_per_page = 3
my_user = {"email": "panda@cwhq.com", "password": "panda123"}

with app.app_context():
    create_post_table()
    add_image_column()
    add_rating_column()
    add_location_columns()  
    user_exist = get_user(my_user["email"], my_user["password"])
    if not user_exist:
        insert_user(my_user["email"], my_user["password"])

# app.py
from flask import jsonify

@app.route("/geocode", methods=["GET"])
def geocode():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify(error="missing query"), 400

    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": q,
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
            },
            headers={
                # Put a real contact so Nominatim won’t block you
                "User-Agent": "PawPoint/1.0 (acho021508@gmail.com)"
            },
            timeout=10,
        )
    except requests.RequestException as e:
        return jsonify(error=f"upstream_request_error: {e}"), 502

    # Handle common upstream statuses explicitly
    if resp.status_code == 429:
        return jsonify(error="rate_limited_by_nominatim"), 429
    if resp.status_code >= 500:
        return jsonify(error=f"upstream_{resp.status_code}"), 502
    if resp.status_code != 200:
        return jsonify(error=f"upstream_{resp.status_code}"), 502

    # Ensure JSON parse won’t crash your route
    try:
        data = resp.json()
    except ValueError:
        return jsonify(error="invalid_upstream_json"), 502

    if not data:
        return jsonify(error="no_results"), 404

    item = data[0]
    return jsonify(
        address=item.get("display_name"),
        lat=float(item["lat"]),
        lng=float(item["lon"]),
    )

@app.route("/")
@welcome_screen
def home_page():
    total_posts = count_posts()
    pages = math.ceil(total_posts / posts_per_page)
    current_page = request.args.get("page", 1, int)
    posts_data = paginated_posts(current_page, posts_per_page)
    return render_template(
        "page.html",
        posts=posts_data,
        current_page=current_page,
        total_posts=total_posts,
        pages=pages,
    )

@app.route("/home")
def carousel_page():
    return render_template("home.html")
@app.route("/welcome")
def welcome_page():
    return render_template("welcome.html")


@app.route("/<post_link>")
@welcome_screen
def post_page(post_link):
    post = find_post(post_link)
    if post:
        return render_template("post.html", post=post) #changed welcome.html to home.html
    else:
        abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


#@app.route("/random")
#def random_post_page():
    #post = random_post()
   # return redirect(url_for("post_page", post_link=post["permalink"]))


from werkzeug.utils import secure_filename
import os

@app.route("/new-post", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "GET":
        return render_template(
            "newpost.html", post_data={}, actionRoute=url_for("new_post")
        )

    # === HANDLE IMAGE UPLOAD ===
    image = request.files.get("image")
    image_url = None
    if image and image.filename != "":
        filename = secure_filename(image.filename)
        upload_folder = os.path.join("static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        image.save(filepath)
        image_url = f"/static/uploads/{filename}"

    # === BUILD POST DATA ===
# === BUILD POST DATA ===
    post_data = {
    "title": request.form["post-title"],
    "author": request.form["post-author"],
    "content": request.form["post-content"],
    "permalink": request.form["post-title"].replace(" ", "-"),
    "tags": request.form["post-tags"],
    "published_on": date.today(),
    "image": image_url,
    "rating": request.form.get("rating"),

    # 🔽 ADD THESE THREE LINES 🔽
    "address": request.form.get("address") or None,
    "latitude": (float(request.form.get("latitude")) if request.form.get("latitude") else None),
    "longitude": (float(request.form.get("longitude")) if request.form.get("longitude") else None),
    }


    existing_post = find_post(post_data["permalink"])
    if existing_post:
        app.logger.warning(f"duplicate post: {post_data['title']}")
        flash("error", "There's already a similar post, maybe use a different title")
        return render_template(
            "newpost.html", post_data=post_data, actionRoute=url_for("new_post")
        )

    insert_post(post_data)
    app.logger.info(f"new post: {post_data['title']}")
    flash("success", "Congratulations on publishing another blog post.")
    return redirect(url_for("post_page", post_link=post_data["permalink"]))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email-id"]
        password = request.form["password"]
        user = get_user(email, password)
        if user:
            session["logged_in"] = True
            flash("success", "You are now logged in")
            return redirect(url_for("home_page"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("login"))


@app.route("/edit/<post_link>")
@login_required
def editor(post_link):
    data = find_post(post_link)
    return render_template(
        "newpost.html", post_data=data, update=True, actionRoute=url_for("edit_post")
    )


import uuid

@app.route("/update", methods=["POST"])
@login_required
def edit_post():
    # === HANDLE IMAGE (new upload or fallback to existing) ===
    image = request.files.get("image")
    image_url = request.form.get("existing-image")  # fallback value

    if image and image.filename != "":
        try:
            filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
            upload_folder = os.path.join("static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            image.save(filepath)
            image_url = f"/static/uploads/{filename}"
            print("New image saved at:", image_url)
        except Exception as e:
            print("Failed to save new image:", e)
            flash("Image upload failed", "error")
            # optionally fall back to existing image or handle differently

    else:
        print("No new image uploaded. Using existing:", image_url)

    # === BUILD UPDATED POST DATA ===
# app.py -> in edit_post()
    post_data = {
    "title": request.form["post-title"],
    "author": request.form["post-author"],
    "content": request.form["post-content"],
    "permalink": request.form["post-permalink"],
    "tags": request.form["post-tags"],
    "published_on": request.form["post-date"],
    "post_id": request.form["post-id"],
    "image": image_url,
    "rating": request.form.get("rating"),
    "address": request.form.get("address"),
    "latitude": float(request.form.get("latitude") or 0) or None,
    "longitude": float(request.form.get("longitude") or 0) or None,
    }


    print("Updating post with data:", post_data)
    update_post(post_data)

    flash("You just updated a blog post", "update")
    return redirect(url_for("post_page", post_link=post_data["permalink"]))




@app.route("/migrations")
def db_migrations():
    try:
        add_publish_date()
        return "All migrations complete"
    except sqlite3.Error as er:
        return "<b>Error</b>:" + str(er)
    finally:
        insert_dates()


@app.route("/delete/<post_id>")
@login_required
def delete_post_page(post_id):
    delete_post(post_id)
    flash("update", "You just deleted a blog post")
    return redirect(url_for("home_page"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email-id"]
        password = request.form["password"]
        insert_user(email, password)
        flash("success", "You are now registered")
        return redirect(url_for("login"))
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
