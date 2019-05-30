from wtforms.validators import ValidationError

class Unique(object):
    def __init__(self, model, field_first, field_second, message='This element already exists.'):
        self.model = model
        self.field_first = field_first
        self.field_second = field_second
        self.message = message

    def __call__(self, form, field_first, field_second):
        check = self.model.query.filter(self.field_first == field_first.data).first()

        if check.field_second == self.field_second:
            raise ValidationError(self.message)
