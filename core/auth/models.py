import sqlalchemy as sa
from flask_login import UserMixin

from core.models import BaseModel
from core.services import login_manager


class User(BaseModel, UserMixin):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String(150), nullable=False)
    last_name = sa.Column(sa.String(150))
    email = sa.Column(sa.String(255), unique=True, nullable=False)
    password = sa.Column(sa.String(128), nullable=False)
    role = sa.Column(sa.Integer, nullable=False)


@login_manager.user_loader
def load_user(user_id: int | str):
    return User.find(user_id)
