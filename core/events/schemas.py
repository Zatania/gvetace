import marshmallow as ma
from marshmallow import fields


class EventSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    address = fields.String(required=True)
    date = fields.Date(required=True)
    time_in = fields.Time(required=True)
    time_out = fields.Time(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    radius = fields.Integer(required=True)
