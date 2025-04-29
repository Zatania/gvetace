import flask

from .forms import CreateDepartmentForm, DeleteForm
from .models import Department

blueprint = flask.Blueprint(
    "departments",
    __name__,
    url_prefix="/departments",
    template_folder="templates",
)


@blueprint.route("/")
def index():
    departments = Department.all()
    delete_form = DeleteForm()
    return flask.render_template("admin/departments/index.html", departments=departments, delete_form=delete_form)


@blueprint.route("/create", methods=["GET", "POST"])
def create():
    form: CreateDepartmentForm = CreateDepartmentForm()
    if form.validate_on_submit():
        Department.create(name=form.name.data)
        flask.flash("Department created successfully", "success")
        return flask.redirect(flask.url_for("admin.departments.index"))

    return flask.render_template("admin/departments/create.html", form=form)

@blueprint.route("/<int:department_id>/edit", methods=["GET", "POST"])
def edit(department_id):
    department = Department.get_by_id(department_id)
    if not department:
        flask.abort(404)

    form = CreateDepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.save()  # This will save the updated department
        flask.flash("Department updated successfully", "success")
        return flask.redirect(flask.url_for("admin.departments.index"))

    return flask.render_template("admin/departments/edit.html", form=form, department=department)


@blueprint.route("/<int:department_id>/delete", methods=["POST"])
def delete(department_id):
    department = Department.get_by_id(department_id)
    if not department:
        flask.abort(404)

    department.delete()  # This will delete the department
    flask.flash("Department deleted successfully", "success")
    return flask.redirect(flask.url_for("admin.departments.index"))
