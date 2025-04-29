import flask

from core.departments.admin import blueprint as department_blueprint
from core.events.models import Event
from core.organizers.admin import blueprint as organizer_blueprint
from core.organizers.models import Organizer
from core.students.admin import blueprint as student_blueprint
from core.students.models import Student

blueprint = flask.Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
)


@blueprint.route("/dashboard")
def dashboard():
    student_count = len(Student.all())
    organizer_count = len(Organizer.all())
    event_count = len(Event.all())
    context = dict(
        student_count=student_count,
        organizer_count=organizer_count,
        event_count=event_count,
    )

    return flask.render_template("admin/dashboard.html", **context)


blueprint.register_blueprint(department_blueprint)
blueprint.register_blueprint(organizer_blueprint)
blueprint.register_blueprint(student_blueprint)
