from flask import Blueprint, render_template

frontend_blueprint = Blueprint(
    "frontend_blueprint",
    __name__,
    static_folder="../frontend/build/assets",
    static_url_path="assets",
    template_folder="../frontend/build",
)

@frontend_blueprint.route("/")
def index():
    return render_template("index.html")

@frontend_blueprint.route("/shows")
def shows_page():
    return render_template("index.html")

@frontend_blueprint.route("/shows/<string:show>")
def show_page(show: str):
    return render_template("index.html")

@frontend_blueprint.route("/shows/<string:show>/episodes")
def show_episodes_page(show: str):
    return render_template("index.html")

@frontend_blueprint.route("/shows/<string:show>/search")
def show_search_page(show: str):
    return render_template("index.html")

@frontend_blueprint.route("/shows/<string:show>/reminder")
def show_reminder_page(show: str):
    return render_template("index.html")

@frontend_blueprint.route("/login")
def login_page():
    return render_template("index.html")

@frontend_blueprint.route("/profile/<string:user>")
def profile_page(user: str):
    return render_template("index.html")

@frontend_blueprint.route("/profile/<string:user>/settings")
def profile_settings_page(user: str):
    return render_template("index.html")
