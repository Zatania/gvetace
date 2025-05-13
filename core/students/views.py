from datetime import datetime, timezone

import face_recognition
import flask
from flask_login import current_user

from core.events.models import Event
from core.students.models import Attendance, Student

from core import geotag

blueprint = flask.Blueprint("students", __name__, template_folder="templates")


@blueprint.route("/home")
def event_list():
    student = Student.where(user_id=current_user.id).first()
    return flask.render_template("students/event_list.html", student=student)


@blueprint.route("/events/<event_id>/time-in", methods=["GET", "POST"])
def time_in(event_id: str):
    event: Event = Event.find_or_fail(event_id)
    student: Student = Student.where(user_id=current_user.id).first()
    attendance = Attendance.where(student_id=student.id, event_id=event.id).first()

    if attendance and attendance.time_in:
        flask.flash("Time-in already recorded.", "info")
        return flask.render_template("students/time_in.html", event=event, disable_form=True)

    if flask.request.method == "POST":
        # safe-get the upload and ensure it’s non-empty
        file = flask.request.files.get("time_in_image")
        if not file or file.filename == "":
            flask.flash("No image provided. Please choose a photo to submit.", "danger")
        coords = geotag.extract_coords(file)

        if coords is None:
            flask.flash("Image does not contain location data. Please enable location tagging in your camera.", "danger")
            return flask.render_template("students/time_in.html", event=event)

        if geotag.within_radius(
            (event.latitude, event.longitude), coords, event.radius
        ):
            # rewind so face_recognition actually sees the image
            file.stream.seek(0)
            student_image = face_recognition.load_image_file(student.face_image)
            submitted_image = face_recognition.load_image_file(file)

            student_encodings = face_recognition.face_encodings(student_image)
            if not student_encodings:
                flask.flash("No face detected in the reference image. Please contact admin.", "danger")
                return flask.render_template("students/time_in.html", event=event)

            student_encoding = student_encodings[0]
            submitted_encodings = face_recognition.face_encodings(submitted_image)

            if not submitted_encodings:
                flask.flash("No face detected in the submitted image. Please try again with a clearer photo.", "danger")
                return flask.render_template("students/time_out.html", event=event)

            submitted_encoding = submitted_encodings[0]

            result = face_recognition.compare_faces([student_encoding], submitted_encoding)[0]
            if not result:
                flask.flash("Face recognition failed, please try again.", "danger")
                return flask.render_template("students/time_in.html", event=event)

            attendance.time_in = datetime.now(timezone.utc)
            attendance.save()

            flask.flash("Attendance successfully recorded.", "success")
            return flask.redirect(flask.url_for("students.time_in", event_id=event.id))

        flask.flash(
            "You are not within the venue, please take a picture closer to the designated area and submit again.",
            "danger",
        )

    return flask.render_template("students/time_in.html", event=event)



@blueprint.route("/events/<event_id>/time-out", methods=["GET", "POST"])
def time_out(event_id: str):
    event: Event = Event.find_or_fail(event_id)
    student: Student = Student.where(user_id=current_user.id).first()
    attendance = Attendance.where(student_id=student.id, event_id=event.id).first()

    if not attendance or not attendance.time_in:
        flask.flash("You must time in before you can time out.", "danger")
        return flask.render_template("students/time_out.html", event=event, disable_form=True)

    if attendance and attendance.time_out:
        flask.flash("Time-out already recorded.", "info")
        return flask.render_template("students/time_out.html", event=event, disable_form=True)

    if flask.request.method == "POST":
        # safe-get the upload and ensure it’s non-empty
        file = flask.request.files.get("time_out_image")
        if not file or file.filename == "":
            flask.flash("No image provided. Please choose a photo to submit.", "danger")
        coords = geotag.extract_coords(file)

        if coords is None:
            flask.flash("Image does not contain location data. Please enable location tagging in your camera.", "danger")
            return flask.render_template("students/time_in.html", event=event)

        if geotag.within_radius(
            (event.latitude, event.longitude), coords, event.radius
        ):
            # rewind so face_recognition actually sees the image
            file.stream.seek(0)
            student_image = face_recognition.load_image_file(student.face_image)
            submitted_image = face_recognition.load_image_file(file)

            student_encodings = face_recognition.face_encodings(student_image)
            if not student_encodings:
                flask.flash("No face detected in the reference image. Please contact admin.", "danger")
                return flask.render_template("students/time_in.html", event=event)

            student_encoding = student_encodings[0]
            submitted_encodings = face_recognition.face_encodings(submitted_image)
            if not submitted_encodings:
                flask.flash("No face detected in the submitted image. Please try again with a clearer photo.", "danger")
                return flask.render_template("students/time_out.html", event=event)

            submitted_encoding = submitted_encodings[0]

            result = face_recognition.compare_faces([student_encoding], submitted_encoding)[0]
            if not result:
                flask.flash("Face recognition failed, please try again.", "danger")
                return flask.render_template("students/time_out.html", event=event)

            attendance.time_out = datetime.now(timezone.utc)
            attendance.save()

            flask.flash("Attendance successfully recorded.", "success")
            return flask.redirect(flask.url_for("students.time_out", event_id=event.id))

        flask.flash(
            "You are not within the venue, please take a picture closer to the designated area and submit again.",
            "danger",
        )

    return flask.render_template("students/time_out.html", event=event)
