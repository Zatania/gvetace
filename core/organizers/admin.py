import flask
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import abort

from core.auth.models import User
from core.departments.models import Department

from .forms import CreateOrganizerForm, EditOrganizerForm, DeleteForm
from .models import Organizer

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
