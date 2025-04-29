import flask

blueprint = flask.Blueprint(
    "organizers",
    __name__,
    template_folder="templates",
)
