from marshmallow import Schema, fields, EXCLUDE


class FormSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    seed = fields.Str()
    height = fields.Int()
    width = fields.Int()
    scale = fields.Int()
    x_offset = fields.Int()
    y_offset = fields.Int()
    octaves = fields.Int()
    persistence = fields.Float()
