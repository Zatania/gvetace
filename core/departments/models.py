import sqlalchemy as sa

from core.models import BaseModel


class Department(BaseModel):
    __tablename__ = "departments"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(150), unique=True, nullable=False)

    def __repr__(self):
        return self.name

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)
