import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import InstrumentedList

from core.models import BaseModel
from core.students.models import Student


class EventOrganizer(BaseModel):
    __tablename__ = "event_organizer"
    id = sa.Column(sa.Integer, primary_key=True)
    event_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )
    organizer_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("organizers.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "event_id",
            "organizer_id",
            name="uq_event_id_organizer_id_event_organizer_table",
        ),
    )


class EventStudent(BaseModel):
    __tablename__ = "event_student"
    id = sa.Column(sa.Integer, primary_key=True)
    event_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )


class Event(BaseModel):
    __tablename__ = "events"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(254), unique=True, nullable=False)
    address = sa.Column(sa.String(254), nullable=False)
    date = sa.Column(sa.Date, nullable=False)
    time_in = sa.Column(sa.Time, nullable=False)
    time_out = sa.Column(sa.Time, nullable=False)
    latitude = sa.Column(sa.Float, nullable=False)
    longitude = sa.Column(sa.Float, nullable=False)
    radius = sa.Column(sa.Integer, nullable=False)

    organizers = relationship("Organizer", secondary="event_organizer", lazy="dynamic")
    students = relationship(
        "Student", secondary="event_student", lazy="dynamic", overlaps="events",
    )
