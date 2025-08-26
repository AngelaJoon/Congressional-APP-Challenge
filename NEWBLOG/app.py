#!/usr/bin/python3


from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    abort,
    request,
    flash,
    session,
)

import random, math, sqlite3
from datetime import date
from decorators import login_required, welcome_screen
from post_models import (
    create_post_table,
    delete_post,
    get_posts,
    find_post,
    random_post,
    insert_post,
    count_posts,
    paginated_posts,
    update_post,
)

from user_models import create_user_table, get_user, insert_user
from migrations import add_publish_date, insert_dates

app = Flask(__name__)

######## SET THE SECRET KEY ###############
# You can write random letters yourself or
# Go to https://randomkeygen.com/ and select a
# random secret key
####################
app.secret_key = "LIgp9t3s"

posts_per_page = 3

my_user = {"email": "panda@cwhq.com", "password": "panda123"}

with app.app_context():
    create_post_table()
    create_user_table()
    user_exist = get_user(my_user["email"], my_user["password"])
    if not user_exist:
        insert_user(my_user["email"], my_user["password"])


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


@app.route("/welcome")
def welcome_page():
    return render_template("welcome.html")


@app.route("/<post_link>")
@welcome_screen
def post_page(post_link):
    post = find_post(post_link)
    if post:
        return render_template("post.html", post=post)
    else:
        abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


@app.route("/random")
def random_post_page():
    post = random_post()
    return redirect(url_for("post_page", post_link=post["permalink"]))


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "GET":
        return render_template(
            "newpost.html", post_data={}, actionRoute=url_for("new_post")
        )
    else:
        post_data = {
            "title": request.form["post-title"],
            "author": request.form["post-author"],
            "content": request.form["post-content"],
            "permalink": request.form["post-title"].replace(" ", "-"),
            "tags:": request.form["post-tags"],
            "published_on": date.today(),
        }

        existing_post = find_post(post_data["permalink"])
        if existing_post:
            app.logger.warning(f"duplicate post: {post_data['title']}")
            flash(
                "error", "There's already a similar post, maybe use a different title"
            )
            return render_template(
                "newpost.html", post_data=post_data, actionRoute=url_for("new_post")
            )
        else:
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


@app.route("/update", methods=["POST"])
@login_required
def edit_post():
    post_data = {
        "title": request.form["post-title"],
        "author": request.form["post-author"],
        "content": request.form["post-content"],
        "permalink": request.form["post-permalink"],
        "tags:": request.form["post-tags"],
        "published_on": request.form["post-date"],
        "post_id": request.form["post-id"],
    }
    update_post(post_data)
    flash("update", "You just updated a blog post")
    return redirect(url_for("post_page", post_link=request.form["post-permalink"]))


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
