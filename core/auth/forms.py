import wtforms as wtf
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = wtf.EmailField("Email address", validators=[DataRequired()])
    password = wtf.PasswordField("Password", validators=[DataRequired()])
