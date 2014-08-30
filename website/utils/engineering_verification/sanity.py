import lxml
import website.views.engineering_verification as eng
import itertools

from . import nec_support as nec
# TODO: move this
from website.views.api2 import ValidationError

def sanity_1(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: No main_panel found in %s tree."
    for tree in (ac, ground):
        if len(list(tree.itercomponents('main_panel'))) == 0:
            raise ValidationError(fail_msg % tree.tag)

def sanity_2(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: %s with id '%s' has no specifications or definition."
    for tree in (ac, dc, ground):
        for component in tree.itercomponents():
            if not (hasattr(component, 'specifications') or hasattr(component, 'definition')):
                raise ValidationError(fail_msg % (component.tag, component.id))

def sanity_3(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: A %s inside the %s has no id."
    for tree in (ac, dc, ground):
        for component in tree.itercomponents():
            if not hasattr(component, 'id'):
                raise ValidationError(fail_msg % (component.tag, tree.tag))

def sanity_4(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: Wire with id '%s' has no size_awg, insulation or material."
    for tree in (ac, dc, ground):
        for wire in tree.itercomponents('wire'):
            specs = nec.get_specifications(wire)
            size = nec.get_size_awg(specs)
            insulation = nec.get_insulation(specs)
            material = nec.get_material(specs)
            if size is None or insulation is None or material is None:
                raise ValidationError(fail_msg % wire.id)

def sanity_5(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: size_awg for wire with id '%s' isn't in the list of available wire sizes."
    for tree in (ac, dc, ground):
        for wire in tree.itercomponents('wire'):
            specs = nec.get_specifications(wire)
            size = nec.get_size_awg(specs)
            if not size in nec.wire_sizes:
                raise ValidationError(fail_msg % wire.id)

def sanity_6(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Inverter with id '%s' has output_ac_voltage of %s which does not match the nominal_votage (%s) of the upstream %s with id %s."
    for inverter in ac.itercomponents('inverter'):
        specs = nec.get_specifications(inverter)
        output_voltage = nec.get_ac_output_voltage(specs)
        for ancestor in itertools.takewhile(lambda component: component.tag not in ('ac', 'dc', 'ground'),
                                            inverter.iterancestors()):
            specs = nec.get_specifications(ancestor)
            nominal_voltage = nec.get_nominal_voltage_ac(specs)
            if nominal_voltage is not None and output_voltage is not None and (output_voltage != nominal_voltage):
                raise ValidationError(fail_msg % (inverter.id, output_voltage, nominal_voltage, ancestor.tag, ancestor.id))

def sanity_7(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: main_panel with id '%s' must have nominal_voltage_ac set."
    for tree in (ac, ground):
        for panel in tree.itercomponents('main_panel'):
            specs = nec.get_specifications(panel)
            voltage = nec.get_nominal_voltage_ac(specs)
            if voltage is None:
                raise ValidationError(fail_msg % panel.id)

def sanity_8(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: The %s with id '%s' has a specification named '%s' which looks like a component; specifications may only contain text nodes and not elements."
    for tree in (ac, dc, ground):
        for component in tree.itercomponents():
            specs = nec.get_specifications(component)
            for spec in specs.iterchildren():
                if isinstance(spec, eng.ElectricalElement):
                    raise ValidationError(fail_msg % (component.tag, component.id, spec.tag))

def sanity_9(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "Sanity test: All systems must have at least one grounding_rod."
    for tree in (ac, dc, ground):
        if len(tree.itercomponents('grounding_rod')) > 0:
            raise ValidationError(fail_msg)
