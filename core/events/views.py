import flask
import sqlalchemy as sa
from marshmallow.exceptions import ValidationError
from sqlalchemy_mixins.activerecord import ModelNotFoundError

from core.departments.models import Department
from core.organizers.models import Organizer
from core.students.models import Attendance, Student
from core.services import db

from .forms import EventOrganizersForm
from .models import Event
from .schemas import EventSchema

blueprint = flask.Blueprint(
    "events",
    __name__,
    url_prefix="/events",
    template_folder="templates",
)


@blueprint.route("/")
def index():
    events = Event.all()
    return flask.render_template("events/index.html", events=events)


@blueprint.route("/create")
def create():
    return flask.render_template("events/create.html")


@blueprint.post("/")
def store():
    try:
        form_data = flask.request.form.to_dict()
        payload = EventSchema().load(form_data)
        event = Event.create(**payload)
    except ValidationError as err:
        return flask.jsonify(err.messages, 422)
    else:
        return flask.jsonify(EventSchema().dump(event))


@blueprint.route("/<event_id>", methods=["GET", "POST"])
def show(event_id: str):
    event: Event = Event.find_or_fail(event_id)
    form: EventOrganizersForm = EventOrganizersForm()
    organizers = Organizer.all()
    context = dict(event=event, form=form, organizers=organizers)

    if form.validate_on_submit():
        event.organizers = form.organizers.data
        event.save()
        flask.flash("Updated organizers for this event.", "success")

    return flask.render_template("events/show.html", **context)


@blueprint.route("/<event_id>/students", methods=["GET", "POST", "DELETE"])
def student_list(event_id: str):
    event: Event = Event.find_or_fail(event_id)
    students = Student.all()
    context = dict(event=event, students=students)

    if flask.request.method == "POST":
        try:
            student = Student.find_or_fail(flask.request.form.get("student_id", None))
            event.students.append(student)
            Attendance.create(
                event_id=event.id,
                student_id=student.id,
            )
            event.save()
        except ModelNotFoundError:
            return flask.jsonify(message="Student not found"), 404
        return flask.render_template("events/invitation-control.html", **context)
    elif flask.request.method == "DELETE":
        try:
            student = Student.find_or_fail(flask.request.form.get("student_id", None))
            event.students.remove(student)
            attendance = Attendance.where(
                event_id=event.id, student_id=student.id
            ).first()
            attendance.delete()
            event.save()
        except ModelNotFoundError:
            return flask.jsonify(message="Student not found"), 404
        return flask.render_template("events/invitation-control.html", **context)

    return flask.render_template("events/student_list.html", **context)


@blueprint.route("/<event_id>/attendance")
def attendance_list(event_id: str):
    event: Event = Event.find_or_fail(event_id)
    departments = Department.all()
    names = [e.name for e in departments]
    attendances = []

    for department in departments:
        conn = db.session.connection()
        result = conn.execute(
            sa.text(
                """
                SELECT COUNT(*)
                FROM attendances
                INNER JOIN students ON attendances.student_id = students.id
                WHERE department_id = :department_id
                AND attendances.time_in IS NOT NULL
                AND attendances.time_out IS NOT NULL
                AND event_id = :event_id
                """
            ),
            dict(
                department_id=department.id,
                event_id=event.id,
            ),
        ).fetchall()
        attendances.append(len(result))
    context = dict(event=event, names=names, attendances=attendances)

    return flask.render_template("events/attendance_list.html", **context)
