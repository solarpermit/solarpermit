import lxml
import itertools

import website.views.engineering_verification as eng
from . import nec_support as nec
# TODO: move this
from website.views.api2 import ValidationError

def nec2014_690_7_A(directives=None, ac=None, dc=None, ground=None):
    ambient_low_f = nec.get_override_ambient_low_f(directives) or fahrenheit(-40)
    def voc_ambient(module):
        specs = nec.get_specifications(module)
        voc = nec.get_voc_stc(specs)
        coeff = nec.get_temperature_coefficient_of_voc(specs)
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
        specs = nec.get_specifications(component)
        dc_voltage_max = nec.get_dc_voltage_max(specs) or nec.volts(600)
        if voc > dc_voltage_max:
            raise ValidationError("NEC 2014 690.7(A): VOC of %s (at an ambient temperature of %s) exceeds maximum voltage of %s of the %s with id '%s'." % (voc, nec.format_as_fahrenheit(ambient_low_f), dc_voltage_max, component.tag, component.id))
        return voc
    if eng.is_electrical(dc):
        for child in dc.iterchildren():
            recurse(child)

def nec2014_690_8(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.8: Current of %s at %s with id '%s' exceeds 80%% of its max_amps value."
    def recurse(component):
        current = nec.amps(0)
        for child in component.iterchildcomponents():
            current += recurse(child)
        specs = nec.get_specifications(component)
        this_current = nec.amps(0)
        if component.tag == 'module':
            this_current = nec.get_isc_stc(specs)
            if this_current is None:
                raise ValidationError("NEC 2014 690.8: No isc_stc specified for module with id '%s'." % component.id)
        elif component.tag == 'inverter':
            this_current = nec.get_ac_output_amps(specs)
            if this_current is None:
                raise ValidationError("NEC 2014 690.8: No ac_output_amps specified for module with id '%s'." % component.id)
        current = max(current, this_current)
        max_current = nec.get_max_amps(specs)
        if max_current is None:
            raise ValidationError("NEC 2014 690.8: No max_amps defined for %s with id '%s'." % (component.tag, component.id))
        if (current > (.8 * max_current)):
            raise ValidationError(fail_msg % (current, component.tag, component.id))
        return current
    for tree in filter(eng.is_electrical, (ac, dc)):
        for child in tree.iterchildren():
            recurse(child)

def nec2014_690_6_1(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.6: AC module with id of '%s' is downstream of an inverter."
    if eng.is_electrical(ac):
        for module in ac.iterdescendants('module'):
            if module.iterancestors('inverter'):
                raise ValidationError(fail_msg % module.id)

def nec2014_690_6_2(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.6: AC module with id of '%s' must not also appear in the DC tree."
    if eng.is_electrical(ac):
        for module in ac.iterdescendants('module'):
            if dc.findcomponent(module.id):
                raise ValidationError(fail_msg % module.id)

def nec2014_690_6_3(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.6: AC module with id of '%s' must have both output_ac_voltage and output_ac_amps specified."
    if eng.is_electrical(ac):
        for module in ac.iterdescendants('module'):
            specs = nec.get_specifications(module)
            voltage = nec.get_ac_output_voltage(specs)
            current = nec.get_ac_output_amps(specs)
            if voltage is None or current is None:
                raise ValidationError(fail_msg % module.id)

def nec2014_690_9(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.43: No breaker or fused_disconnect found between %s with id '%s' and the %s with id '%s'"
    for type in ('main_panel', 'sub_panel'):
        if eng.is_electrical(ac):
            for panel in ac.iterdescendants(type):
                for inverter in panel.itercomponents('inverter'):
                    if len(filter(lambda component: component.tag in ('breaker', 'fused_disconnect'),
                                  itertools.takewhile(lambda parent: parent != panel,
                                                      inverter.iterancestors()))) == 0:
                        raise ValidationError(fail_msg % (panel.tag, panel.id, inverter.tag, inverter.id))

def nec2014_690_12_dc(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.12: Inverter with id '%s' has no integrated_dc_disconnect and there is no disconnect or or fused_disconnect between it and the modules connected to it."
    if eng.is_electrical(dc):
        for inverter in dc.itercomponents('inverter'):
            specs = nec.get_specifications(inverter)
            if not nec.get_integrated_dc_disconnect(specs):
                for module in inverter.itercomponents('module'):
                    if not any(filter(lambda component: component.tag in ('disconnect', 'fused_disconnect'),
                                      itertools.takewhile(lambda parent: parent != inverter,
                                                          module.iterancestors()))):
                        raise ValidationError(fail_msg % (inverter.id))

def nec2014_690_12_ac(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.12: There is no disconnect or or fused_disconnect between inverter with id '%s' and the main_panel."
    if eng.is_electrical(dc):
        for inverter in dc.itercomponents('inverter'):
            specs = nec.get_specifications(inverter)
            if not nec.get_integrated_dc_disconnect(specs):
                if not any(filter(lambda component: component.tag == 'breaker',
                                  itertools.takewhile(lambda parent: parent.tag != 'main_panel',
                                                      inverter.iterancestors()))):
                    for module in inverter.itercomponents('module'):
                        if not any(filter(lambda component: component.tag in ('disconnect', 'fused_disconnect'),
                                          itertools.takewhile(lambda parent: parent != inverter,
                                                              module.iterancestors()))):
                            raise ValidationError(fail_msg % (inverter.id))

def nec2014_690_13(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.13: There are DC components between inverter with id '%s' and module with id '%s', but the inverter does not have an integrated_dc_disconnect, nor is there a disconnect or fused_disconnect between them."
    def is_disconnect(component):
        return component.tag in ('disconnect', 'fused_disconnect')
    if eng.is_electrical(dc):
        for inverter in dc.iterdescendants('inverter'):
            for module in inverter.itercomponents('module'):
                intervening_components = list(itertools.takewhile(lambda c: c != module,
                                                                  inverter.itercomponents()))
                if len(intervening_components) > 0:
                    specs = nec.get_specifications(inverter)
                    integrated_dc_disconnect = nec.get_integrated_dc_disconnect(specs)
                    if not (integrated_dc_disconnect or len(list(filter(is_disconnect, intervening_components))) > 0):
                        raise ValidationError(fail_msg % (inverter.id, module.id))

def nec2014_690_13_D(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.13(D): More than 6 disconnects exist in the dc tree."
    def is_disconnect(component):
        if component.tag == 'breaker':
            return True
        if component.tag in ('disconnect', 'fused_disconnect'):
            return not (any(component.iterancestors('inverter')) and \
                        any(component.itercomponents('module')))
        if component.tag == 'inverter':
            specs = nec.get_specifications(component)
            if nec.get_integrated_dc_disconnect(specs):
                return True
    if eng.is_electrical(dc):
        if len(list(filter(is_disconnect, dc.itercomponents()))) > 6:
            raise ValidationError(fail_msg)

def nec2014_690_15(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.15: There are no breakers or fused AC disconnects between inverter with id '%s' and main_panel with id '%s'."
    def is_disconnect(component):
        return component.tag in ('breaker', 'fused_disconnect')
    if eng.is_electrical(ac):
        for panel in ac.iterdescendants('main_panel'):
            for inverter in itertools.takewhile(lambda component: component.tag == 'inverter',
                                                panel.itercomponents()):
                intervening_components = itertools.takewhile(lambda c: c != panel,
                                                             inverter.itercomponents())
                if len(list(filter(is_disconnect, intervening_components))) == 0:
                    raise ValidationError(fail_msg % (inverter.id, panel.id))

def nec2014_690_15_D(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.15(D): More than 6 disconnects exist in the ac tree."
    def is_disconnect(component):
        if component.tag == 'breaker':
            if len(list(component.iterancestors('sub_panel'))) > 0:
                return False
            return True
        if component.tag in ('disconnect', 'fused_disconnect'):
            return True
    if eng.is_electrical(ac):
        if len(list(filter(is_disconnect, ac.itercomponents()))) > 6:
            raise ValidationError(fail_msg)

def nec2014_690_43(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.43: %s with id '%s' is connected to %s but not to ground."
    for tree in filter(eng.is_electrical, (ac, dc)):
        for component in tree.itercomponents():
            if component.tag not in ('breaker', 'wire'):
                if len(filter(lambda node: node.tag == component.tag,
                              ground.findcomponent(component.id))) == 0:
                    raise ValidationError(fail_msg % (component.tag, component.id, tree.tag))

def nec2014_690_45(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.45: Wire with id '%s' needs to be size '%s' or larger to handle %s current during a ground fault."
    def recurse(component):
        current = nec.amps(0)
        for child in component.iterchildcomponents():
            current += recurse(child)
        specs = nec.get_specifications(component)
        this_current = nec.amps(0)
        if component.tag == 'module':
            this_current = nec.get_isc_stc(specs)
            if this_current is None:
                raise ValidationError("NEC 2014 690.45: No isc_stc specified for module with id '%s'." % component.id)
        elif component.tag == 'inverter':
            this_current = nec.get_ac_output_amps(specs)
            if this_current is None:
                raise ValidationError("NEC 2014 690.45: No ac_output_amps specified for module with id '%s'." % component.id)
        current = max(current, this_current)
        if component.tag == 'wire':
            size = nec.get_size_awg(specs)
            material = nec.get_material(specs)
            if size is None:
                raise ValidationError("NEC 2014 690.45: wire with id '%s' has no size_awg." % component.id)
            if material is None:
                raise ValidationError("NEC 2014 690.45: wire with id '%s' has no material." % component.id)
            sizes = nec.ground_current_wire_sizes[material]
            for (c, s) in sizes.iteritems():
                if c >= current:
                    if nec.wire_sizes.index(s) > nec.wire_sizes.index(size):
                        raise ValidationError(fail_msg % (component.id, s, current))
                    break;
        return current
    if eng.is_electrical(ground):
        for child in ground.iterchildren():
            recurse(child)


def nec2014_690_46(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.46: Wire with id '%s' is connected to a ground_lug, and so must be 6 AWG or larger"
    def doTest(wire):
        specs = nec.get_specifications(wire)
        size = nec.get_size_awg(specs)
        if nec.wire_sizes.index(size) <= 3:
            raise ValidationError(fail_msg % wire.id)

    for lug in ground.itercomponents('ground_lug'):
        for wire in lug.iterchildcomponents('wire'):
            doTest(wire)
    if eng.is_electrical(ground):
        for wire in ground.itercomponents('wire'):
            if len(list(wire.iterchildcomponents('ground_lug'))) > 0:
                doTest(wire)

def nec2014_690_47_B_2(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.47(B)(2): Grounding rod with id '%s' is not made of copper."
    if eng.is_electrical(ground):
        for rod in ground.itercomponents('grounding_rod'):
            specs = nec.get_specifications(rod)
            material = nec.get_material(specs)
            if material != "Cu":
                raise ValidationError(fail_msg % rod.id)
