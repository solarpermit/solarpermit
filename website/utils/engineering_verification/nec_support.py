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

@optional_getter('nominal_voltage_ac')
def get_nominal_voltage_ac(voltage):
    return volts(to_num(voltage))

@optional_getter('ac_output_voltage')
def get_ac_output_voltage(voltage):
    return volts(to_num(voltage))

@optional_getter('ac_output_amps')
def get_ac_output_amps(amperage):
    return amps(to_num(amperage))

@optional_getter('isc_atc')
def get_isc_stc(amperage):
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

@optional_getter('insulation')
def get_insulation(insulation):
    return str(insulation)

wire_sizes = ["18", "16", "14", "12", "10", "8", "6", "4", "3", "2", "1",
              "1/0", "2/0", "3/0", "4/0", "250", "300", "350", "400", "500",
              "600", "700", "750", "800", "900", "1000", "1200"]
ground_current_wire_sizes = { "Cu": { amps(15):   "14",
                                      amps(20):   "12",
                                      amps(60):   "10",
                                      amps(100):  "8",
                                      amps(200):  "6",
                                      amps(300):  "4",
                                      amps(400):  "3",
                                      amps(500):  "2",
                                      amps(600):  "1",
                                      amps(800):  "1/0",
                                      amps(1000): "2/0",
                                      amps(1200): "3/0",
                                      amps(1600): "4/0",
                                      amps(2000): "250",
                                      amps(2500): "350",
                                      amps(3000): "400",
                                      amps(4000): "500",
                                      amps(5000): "700",
                                      amps(6000): "800", },
                              "Al": { amps(15):   "12",
                                      amps(20):   "10",
                                      amps(60):   "8",
                                      amps(100):  "6",
                                      amps(200):  "4",
                                      amps(300):  "2",
                                      amps(400):  "1",
                                      amps(500):  "1/0",
                                      amps(600):  "2/0",
                                      amps(800):  "3/0",
                                      amps(1000): "4/0",
                                      amps(1200): "250",
                                      amps(1600): "350",
                                      amps(2000): "400",
                                      amps(2500): "600",
                                      amps(3000): "750",
                                      amps(4000): "750",
                                      amps(5000): "1200",
                                      amps(6000): "1200", }, }
def to_num(element):
    if isinstance(element, lxml.objectify.IntElement):
        return int(element)
    if isinstance(element, lxml.objectify.FloatElement):
        return float(element)
    if isinstance(element, lxml.objectify.LongElement):
        return long(element)
    return None
