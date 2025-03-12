from typeguard import typechecked
from src.srcMain.Config import Config

class TypecheckedMeta(type):
    def __new__(cls, name, bases, attrs):
        configTypecheck = Config().getConfig().get("typecheck")
        for name, value in attrs.items():
            if callable(value) and configTypecheck:
                attrs[name] = typechecked(value)
        return super().__new__(cls, name, bases, attrs)

class Typechecked(metaclass=TypecheckedMeta):
    pass