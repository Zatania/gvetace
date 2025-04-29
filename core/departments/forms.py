import wtforms as wtf
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class CreateDepartmentForm(FlaskForm):
    name = wtf.StringField("Department Name", validators=[DataRequired()])

class DeleteForm(FlaskForm):
    pass
