import flask
from flask_login import logout_user
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash

from .forms import LoginForm
from .models import User

blueprint = flask.Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form: LoginForm = LoginForm()
    if form.validate_on_submit() and auth_attempt(form):
        return handle_redirect()

    return flask.render_template("auth/login.html", form=form)


@blueprint.post("/logout")
def logout():
    logout_user()
    return flask.redirect("/")


def auth_attempt(form: LoginForm):
    user: User = User.where(email=form.email.data).first()
    if user and check_password_hash(user.password, form.password.data):
        login_user(user)
        return True

    flask.flash("Wrong email or password", "danger")
    return False


def handle_redirect():
    user: User = current_user
    if user.role == 1:
        return flask.redirect(flask.url_for("admin.dashboard"))
    if user.role == 2:
        return flask.redirect(flask.url_for("events.index"))
    if user.role == 3:
        return flask.redirect(flask.url_for("students.event_list"))

    return flask.abort(401)
