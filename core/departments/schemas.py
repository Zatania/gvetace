from marshmallow import Schema, fields


class DepartmentSchema(Schema):
    name = fields.String()
