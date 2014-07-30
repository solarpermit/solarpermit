# TODO: move this
from website.views.api2 import ValidationError

def check1(*args):
    pass

def check2(*args):
    raise ValidationError("stuff")

def check3(*args):
    raise Exception()
