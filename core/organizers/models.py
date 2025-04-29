import sqlalchemy as sa
from sqlalchemy.orm import relationship

from core.auth.models import User
from core.models import BaseModel


class Organizer(BaseModel):
    __tablename__ = "organizers"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    department_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = relationship("User", uselist=False)
    department = relationship("Department")

    def __repr__(self):
        return self.full_name

    @property
    def full_name(self):
        user: User = self.user
        return f"{user.first_name} {user.last_name}"

    def delete(self):
        user: User = self.user
        user.delete()
        super().delete()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)
