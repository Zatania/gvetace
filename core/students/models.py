import os
from datetime import datetime, timedelta, timezone
import pytz

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from core.auth.models import User
from core.config import Config
from core.models import BaseModel
MANILA = pytz.timezone("Asia/Manila")


class Student(BaseModel):
    __tablename__ = "students"
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
    profile = sa.Column(sa.String(254), nullable=False)

    user = relationship("User", uselist=False)
    department = relationship("Department")
    events = relationship("Event", secondary="event_student")

    @property
    def full_name(self):
        user: User = self.user
        return f"{user.first_name} {user.last_name}"

    def delete(self):
        user: User = self.user
        user.delete()
        super().delete()

    @property
    def face_image(self):
        return os.path.join(Config.BASE_DIR, "uploads", self.profile)


class Attendance(BaseModel):
    __tablename__ = "attendances"
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
    time_in = sa.Column(sa.DateTime)
    time_out = sa.Column(sa.DateTime)

    event = relationship("Event")
    student = relationship("Student")

    @property
    def status(self):
        # Build the event start and threshold as naïve datetimes
        event_start = datetime.combine(self.event.date, self.event.time_in)
        late_threshold = event_start + timedelta(minutes=15)

        if not self.time_in:
            return 4  # Absent

        # Now both sides are naïve
        if self.time_in <= late_threshold:
            return 1  # Present on time
        elif self.time_in > late_threshold and self.time_out:
            return 2  # Present but no timeout
        else:
            return 3  # Late
    @property
    def student_name(self):
        """
        Returns the student's full name if the User exists,
        otherwise returns 'Student Deleted'.
        """
        # if the related Student or its User has been deleted,
        # self.student or self.student.user could be None
        if self.student and self.student.user:
            u = self.student.user
            return f"{u.first_name} {u.last_name}"
        return "Student Deleted"

    @property
    def time_in_local(self) -> str | None:
        """Asia/Manila datetime in 12-hour format."""
        if not self.time_in:
            return None
        return self.time_in.astimezone(MANILA).strftime("%B %d, %Y %I:%M:%S %p")

    @property
    def time_out_local(self) -> str | None:
        """Asia/Manila datetime in 12-hour format."""
        if not self.time_out:
            return None
        return self.time_out.astimezone(MANILA).strftime("%B %d, %Y %I:%M:%S %p")
