import os

from flask import Flask, redirect, url_for

from .admin.commands import group as admin_cli
from .admin.views import blueprint as admin_blueprint
from .auth.views import blueprint as auth_blueprint
from .events.views import blueprint as event_blueprint
from .organizers.views import blueprint as organizer_blueprint
from .services import csrf, db, login_manager, migrate
from .students.views import blueprint as student_blueprint

app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(
    SECRET_KEY=os.environ["SECRET_KEY"],
    SQLALCHEMY_DATABASE_URI="sqlite:///database.sqlite",
)

csrf.init_app(app)
login_manager.init_app(app)
db.init_app(app)
migrate.init_app(app)

app.cli.add_command(admin_cli)

app.register_blueprint(admin_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(event_blueprint)
app.register_blueprint(organizer_blueprint)
app.register_blueprint(student_blueprint)


@app.route("/")
def index():
    return redirect(url_for("auth.login"))
