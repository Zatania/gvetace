from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

from core.organizers.models import Organizer


class EventOrganizersForm(FlaskForm):
    organizers = QuerySelectMultipleField("Organizers", query_factory=Organizer.all)
