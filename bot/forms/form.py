import re

class FormField:
    def __init__(self, name, placeholder, min_length=None, max_length=None, regex=None):
        self.name = name
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex

    def validate(self, value):
        if self.min_length and len(value) < self.min_length:
            return f"Минимальная длина поля '{self.name}' - {self.min_length} символов."
        if self.max_length and len(value) > self.max_length:
            return f"Максимальная длина поля '{self.name}' - {self.max_length} символов."
        if self.regex and not re.match(self.regex, value):
            return f"Поле '{self.name}' не соответствует формату."
        return None

class Form:
    def __init__(self, title, fields: list[FormField]):
        self.title = title
        self.fields = fields
        self.data = {}

    def validate(self):
        errors = {}
        for field in self.fields:
            error = field.validate(self.data.get(field.name, ""))
            if error:
                errors[field.name] = error
        return errors

    def is_valid(self):
        return not self.validate()

    def get_data(self):
        return self.data