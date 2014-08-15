import lxml
from units_support import *

from website.views.api2 import checked_getter, optional_getter, ValidationError

def pass_fail(func):
    def testcase(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ValidationError as e:
            return (False, func.__name__, e.args[0])
        except Exception as e:
            return (False, func.__name__, "Unknown Error")
        return (True, func.__name__)

def predefined_coeff(ambient):
    ambient = celsius(ambient)
    if ambient >= celsius(25):
        return 1.0
    if ambient >= celsius(20):
        return 1.02
    if ambient >= celsius(15):
        return 1.04
    if ambient >= celsius(10):
        return 1.06
    if ambient >= celsius(5):
        return 1.08
    if ambient >= celsius(0):
        return 1.10
    if ambient >= celsius(-5):
        return 1.12
    if ambient >= celsius(-10):
        return 1.14
    if ambient >= celsius(-15):
        return 1.16
    if ambient >= celsius(-20):
        return 1.18
    if ambient >= celsius(-25):
        return 1.20
    if ambient >= celsius(-30):
        return 1.21
    if ambient >= celsius(-35):
        return 1.23
    if ambient >= celsius(-40):
        return 1.25
    raise ValidationError("ambient temp too low")

@checked_getter('specifications')
def get_specifications(node):
    return node

@optional_getter('override_ambient_low_f')
def get_override_ambient_low_f(override):
    return fahrenheit(to_num(override))

@optional_getter('temperature_coefficient_of_voc')
def get_temperature_coefficient_of_voc(coeff):
    return volts_per_fahrenheit(to_num(coeff))

@checked_getter('voc_stc')
def get_voc_stc(voc):
    return volts(to_num(voc))

@optional_getter('dc_voltage_max')
def get_dc_voltage_max(voltage):
    return volts(to_num(voltage))

@optional_getter('integrated_dc_disconnect')
def get_integrated_dc_disconnect(disconnect):
    return bool(disconnect)

@optional_getter('ac_output_voltage')
def get_ac_output_voltage(voltage):
    return volts(to_num(voltage))

@optional_getter('ac_output_amps')
def get_ac_output_amps(amperage):
    return amps(to_num(amperage))

@optional_getter('isc_atc')
def get_isc_atc(amperage):
    return amps(to_num(amperage))

@optional_getter('max_amps')
def get_max_amps(amperage):
    return amps(to_num(amperage))

@optional_getter('material')
def get_material(mat):
    return str(mat)

@optional_getter('size_awg')
def get_size_awg(awg):
    return str(awg)

wire_sizes = ["14", "12", "10", "8", "6", "4", "3", "2", "1", "1/0", "2/0", "3/0", "4/0", "250", "350", "400", "500", "700", "800"]

def to_num(element):
    if isinstance(element, lxml.objectify.IntElement):
        return int(element)
    if isinstance(element, lxml.objectify.FloatElement):
        return float(element)
    if isinstance(element, lxml.objectify.LongElement):
        return long(element)
    return None
