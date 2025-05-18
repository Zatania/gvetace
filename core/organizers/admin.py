import flask
import csv
import io
from flask import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from core.auth.models import User
from core.departments.models import Department
from sqlalchemy_mixins.activerecord import ModelNotFoundError

from .forms import CreateOrganizerForm, EditOrganizerForm, DeleteForm
from core.events.forms import EventOrganizersForm
from core.students.models import Attendance, Student
from .models import Organizer
from core.events.models import Event

blueprint = flask.Blueprint(
    "organizers",
    __name__,
    url_prefix="/organizers",
    template_folder="templates",
)


@blueprint.route("/")
def index():
    organizers = Organizer.all()
    delete_form = DeleteForm()
    return flask.render_template(
        "admin/organizers/index.html",
        organizers=organizers,
        delete_form=delete_form,
    )

@blueprint.route("/<int:organizer_id>/events")
def organizer_events(organizer_id):
    organizer = Organizer.get_by_id(organizer_id) or flask.abort(404)
    events = organizer.events.order_by(Event.date).all()
    return flask.render_template(
        "event/index.html",
        organizer=organizer,
        events=events,
    )

@blueprint.route("/<int:organizer_id>/events/<int:event_id>", methods=["GET", "POST"])
def show(organizer_id: int, event_id: int):
    organizer = Organizer.get_by_id(organizer_id) or flask.abort(404)
    event: Event = Event.find_or_fail(event_id)

    # optional: ensure the event actually belongs to this organizer
    if not organizer.events.filter_by(id=event.id).first():
        flask.abort(404)

    form: EventOrganizersForm = EventOrganizersForm(obj=event)
    organizers = Organizer.all()

    return flask.render_template(
        "event/view.html",
        organizer=organizer,
        event=event,
        form=form,
        organizers=organizers,
    )



@blueprint.route("/<int:organizer_id>/events/<int:event_id>/students", methods=["GET", "POST", "DELETE"])
def student_list(organizer_id: int, event_id: int):
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

    return flask.render_template("event/student_list.html", **context)

@blueprint.route("/<int:organizer_id>/events/<int:event_id>/attendance", methods=["GET"])
def attendance_list(organizer_id: int, event_id: int):
    organizer = Organizer.get_by_id(organizer_id) or flask.abort(404)
    event = Event.find_or_fail(event_id)

    # Ensure event belongs to the organizer
    if not organizer.events.filter_by(id=event.id).first():
        flask.abort(404)

    # Query attendance records for this event
    attendance_records = Attendance.where(event_id=event.id).all()

    return flask.render_template(
        "event/attendance_list.html",
        event=event,
        attendance_records=attendance_records,
    )

@blueprint.route("/<int:organizer_id>/events/<int:event_id>/density", methods=["GET"])
def density(organizer_id: int, event_id: int):
    # make sure organizer & event exist and belong together
    organizer = Organizer.get_by_id(organizer_id) or flask.abort(404)
    event = Event.find_or_fail(event_id)
    if not organizer.events.filter_by(id=event.id).first():
        flask.abort(404)

    # aggregate attendance by department
    # Attendance → Student → Department
    session = Attendance.query.session  # or however you get your Session
    results = (
        session.query(
            Department.name.label("dept"),
            func.count(Attendance.id).label("cnt"),
        )
        .join(Student, Student.id == Attendance.student_id)
        .join(Department, Department.id == Student.department_id)
        .filter(Attendance.event_id == event.id)
        .group_by(Department.name)
        .order_by(Department.name)
        .all()
    )

    names = [r.dept for r in results]
    attendances = [r.cnt for r in results]

    return flask.render_template(
        "event/density.html",  # or wherever you put density.html
        event=event,
        names=names,
        attendances=attendances,
    )

@blueprint.route("/create", methods=["GET", "POST"])
def create():
    form: CreateOrganizerForm = CreateOrganizerForm()
    if form.validate_on_submit():
        department: Department = form.department.data
        user: User = User.create(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role=2,
        )
        Organizer.create(user_id=user.id, department_id=department.id)
        flask.flash("Organizer account created successfully.", "success")
        return flask.redirect(flask.url_for("admin.organizers.index"))

    return flask.render_template("admin/organizers/create.html", form=form)

@blueprint.route("/<int:organizer_id>/edit", methods=["GET", "POST"])
def edit(organizer_id):
    organizer = Organizer.get_by_id(organizer_id) or flask.abort(404)
    user = organizer.user

    # Pass original_email so the form knows what to skip
    form = EditOrganizerForm(original_email=user.email, obj=user)
    # And set the department choice
    form.department.data = organizer.department

    if form.validate_on_submit():
        # update the user record
        user.first_name = form.first_name.data
        user.last_name  = form.last_name.data
        user.email      = form.email.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data)

        # update organizer
        organizer.department = form.department.data
        organizer.save()

        flask.flash("Organizer updated successfully.", "success")
        return flask.redirect(flask.url_for("admin.organizers.index"))

    return flask.render_template(
        "admin/organizers/edit.html",
        form=form,
        organizer=organizer
    )



@blueprint.route("/<int:organizer_id>/delete", methods=["POST"])
def delete(organizer_id):
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400)

    organizer = Organizer.get_by_id(organizer_id)
    if not organizer:
        abort(404)

    organizer.delete()
    flask.flash("Organizer deleted successfully.", "success")
    return flask.redirect(flask.url_for("admin.organizers.index"))

@blueprint.route("/<int:organizer_id>/events/<int:event_id>/attendance/download", methods=["GET"])
def attendance_csv(organizer_id: int, event_id: int):
    organizer = Organizer.get_by_id(organizer_id) or flask.abort(404)
    event = Event.find_or_fail(event_id)

    if not organizer.events.filter_by(id=event.id).first():
        flask.abort(404)

    records = Attendance.where(event_id=event.id).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Full Name", "Time In", "Time Out", "Status", "Verification Status"])
    for a in records:
        writer.writerow([
            a.student_name,
            a.time_in_local or "",
            a.time_out_local or "",
            {1: "Present", 2: "Present (No time-out)", 3: "Late", 4: "Absent"}[a.status],
            "Verified",
        ])

    buffer.seek(0)
    # use secure_filename to strip unsafe chars
    filename = secure_filename(f"{event.name}-{event.date}.csv")
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )
