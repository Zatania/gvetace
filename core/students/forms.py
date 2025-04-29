import wtforms as wtf
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.validators import DataRequired, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField

from core.auth.models import User
from core.departments.models import Department


class CreateStudentForm(FlaskForm):
    def __init__(self, current_user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user

    first_name = wtf.StringField("First Name", validators=[DataRequired()])
    last_name = wtf.StringField("Last Name", validators=[DataRequired()])
    email = wtf.EmailField("Email address", validators=[DataRequired()])
    password = wtf.PasswordField("Password")  # No DataRequired here
    password_confirmation = wtf.PasswordField("Confirm Password")

    department = QuerySelectField(
        "Department",
        query_factory=Department.all,
        validators=[DataRequired()],
    )
    profile = FileField(
        "Profile",
        validators=[FileAllowed(["jpg", "png"], "Please upload an image")],
    )

    def validate_email(self, email: wtf.FormField):
        user = User.where(email=email.data).first()
        if user and (not self.current_user or user.id != self.current_user.id):
            raise ValidationError("Email address is already in use")

    def validate(self):
        # Custom password check
        rv = super().validate()
        if not rv:
            return False

        if self.password.data or self.password_confirmation.data:
            if self.password.data != self.password_confirmation.data:
                self.password_confirmation.errors.append("Passwords must match")
                return False
        return True

class DeleteForm(FlaskForm):
    """Empty form just to get a CSRF token."""
    pass
