from typeguard import typechecked

class TypecheckedMeta(type):
    def __new__(cls, name, bases, attrs):
        for name, value in attrs.items():
            if callable(value):
                attrs[name] = typechecked(value)
        return super().__new__(cls, name, bases, attrs)

class Typechecked(metaclass=TypecheckedMeta):
    pass