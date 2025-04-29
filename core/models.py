from sqlalchemy_mixins import AllFeaturesMixin

from .services import db


class BaseModel(db.Model, AllFeaturesMixin):
    __abstract__ = True


BaseModel.set_session(db.session)
