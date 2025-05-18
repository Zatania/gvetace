import os

import flask
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import abort

from core.auth.models import User
from core.config import Config
from core.departments.models import Department

from .forms import CreateStudentForm, DeleteForm
from .models import Student


blueprint = flask.Blueprint(
    "students",
    __name__,
    url_prefix="/students",
    template_folder="templates",
)

@blueprint.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return flask.send_from_directory(os.path.join(Config.BASE_DIR, "uploads"), filename)


@blueprint.route("/")
def index():
    students = Student.all()
    delete_form = DeleteForm()
    return flask.render_template("admin/students/index.html", students=students, delete_form=delete_form)


@blueprint.route("/create", methods=["GET", "POST"])
def create():
    form: CreateStudentForm = CreateStudentForm()
    if form.validate_on_submit():
        user: User = User.create(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=generate_password_hash("password"),
            role=3,
        )
        department: Department = form.department.data

        profile = flask.request.files["profile"]
        extension = profile.filename.split(".")[-1]
        filename = f"{user.first_name.lower()}_{user.last_name.lower()}.{extension}"
        profile.save(
            os.path.join(
                Config.BASE_DIR,
                "uploads",
                filename,
            )
        )
        Student.create(user_id=user.id, department_id=department.id, profile=filename)

        Student.create(user_id=user.id, department_id=department.id, profile=filename)
        flask.flash("Student account created successfully", "success")

        return flask.redirect(flask.url_for("admin.students.index"))

    return flask.render_template("admin/students/create.html", form=form)

@blueprint.route("/<int:student_id>/edit", methods=["GET", "POST"])
def edit(student_id):
    student: Student = Student.find_or_fail(student_id)
    user: User = student.user

    form = CreateStudentForm(current_user=user, obj=user) # This auto-fills first_name, last_name, email

    # Manually set department since it's a relationship field
    form.department.data = student.department

    if flask.request.method == "POST" and form.validate():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data

        # Update password only if provided and confirmed
        password = form.password.data
        confirm_password = form.password_confirmation.data
        if password and confirm_password and password == confirm_password:
            user.password = generate_password_hash(password)

        user.save()

        # Update department
        student.department = form.department.data

        # Update profile image only if a new one is uploaded
        profile = flask.request.files.get("profile")
        if profile and profile.filename:
            extension = profile.filename.split(".")[-1]
            filename = f"{user.first_name.lower()}_{user.last_name.lower()}.{extension}"
            profile.save(os.path.join(Config.BASE_DIR, "uploads", filename))
            student.profile = filename

        student.save()
        flask.flash("Student updated successfully", "success")
        return flask.redirect(flask.url_for("admin.students.index"))

    return flask.render_template("admin/students/edit.html", form=form, student=student)

@blueprint.route("/<int:student_id>/delete", methods=["POST"])
def delete(student_id):
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400)
    student = Student.find_or_fail(student_id)
    student.delete()
    flask.flash("Student deleted successfully", "success")
    return flask.redirect(flask.url_for("admin.students.index"))
