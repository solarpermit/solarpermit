import pdb
import units.predefined

from . import nec_support as nec
# TODO: move this
from website.views.api2 import ValidationError

def nec2014_690_7_A(directives=None, ac=None, dc=None, ground=None):
    ambient_low_f = nec.get_override_ambient_low_f(directives, 'override_ambient_low_f') or fahrenheit(-40)
    def voc_ambient(module):
        specs = nec.get_prop(module, 'specifications')
        voc = nec.get_voc_stc(specs, 'voc_stc')
        coeff = nec.get_temperature_coefficient_of_voc(specs, 'temperature_coefficient_of_voc')
        if coeff is None:
            return nec.predefined_coeff(ambient_low_f) * voc
        else:
            deltaT = nec.celsius(25) - ambient_low_f
            return voc + (coeff * deltaT)
    def recurse(component):
        voc = nec.volts(0)
        if component.tag == 'module':
            voc = voc_ambient(component)
        for child in component.iterchildcomponents():
            voc += recurse(child)
        specs = nec.get_prop(component, 'specifications')
        dc_voltage_max = nec.get_dc_voltage_max(specs, 'dc_voltage_max') or nec.volts(600)
        if voc > dc_voltage_max:
            raise ValidationError("NEC 2014 690.7(A): VOC of %s (at an ambient temperature of %s) exceeds maximum voltage of %s of the %s with id '%s'." % (voc, nec.format_as_fahrenheit(ambient_low_f), dc_voltage_max, component.tag, component.id))
        return voc
    for child in dc.iterchildren():
        recurse(child)
