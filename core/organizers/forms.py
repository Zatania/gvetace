import wtforms as wtf
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional
from wtforms_sqlalchemy.fields import QuerySelectField

from core.auth.models import User
from core.departments.models import Department


class CreateOrganizerForm(FlaskForm):
    first_name = wtf.StringField("First Name", validators=[DataRequired()])
    last_name = wtf.StringField("Last Name", validators=[DataRequired()])
    email = wtf.EmailField("Email address", validators=[DataRequired()])
    password = wtf.PasswordField(
        "Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    password_confirmation = wtf.PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    department = QuerySelectField(
        "Department",
        query_factory=Department.all,
        validators=[DataRequired()],
    )

    def validate_email(self, email: wtf.FormField):
        user = User.where(email=email.data).first()
        if user:
            raise ValidationError("Email address is already in use")

class EditOrganizerForm(FlaskForm):
    first_name = wtf.StringField("First Name", validators=[DataRequired()])
    last_name = wtf.StringField("Last Name", validators=[DataRequired()])
    email = wtf.EmailField("Email address", validators=[DataRequired()])
    password = wtf.PasswordField(
        "Password",
        validators=[Optional(), EqualTo("password_confirmation", message="Passwords must match")],
    )
    password_confirmation = wtf.PasswordField("Confirm Password", validators=[Optional()])
    department = QuerySelectField(
        "Department",
        query_factory=Department.all,
        validators=[DataRequired()],
    )

    def __init__(self, original_email=None, *args, **kwargs):
        """
        original_email: the User.email before editing, so we only
        enforce uniqueness if they actually change it.
        """
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, field):
        # Only check uniqueness if they really changed their email
        if field.data != self.original_email:
            if User.where(email=field.data).first():
                raise ValidationError("Email address is already in use")

class DeleteForm(FlaskForm):
    """Empty form just to get a CSRF token."""
    pass
