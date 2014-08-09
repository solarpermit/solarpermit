# coding: utf-8
from units import unit
import units
import units.predefined

units.predefined.define_units()
units.scaled_unit('R', 'K', 5.0/9.0)

volts = unit('V')
kelvin = unit('K')
rankine = unit('R')

def fahrenheit(num):
    if isinstance(num, float) or isinstance(num, int):
        return rankine(num + 459.67)
    elif isinstance(num, units.quantity.Quantity):
        return rankine(num)
def celsius(num):
    if isinstance(num, float) or isinstance(num, int):
        return kelvin(num + 273.15)
    elif isinstance(num, units.quantity.Quantity):
        return kelvin(num)

volts_per_fahrenheit = volts / rankine
volts_per_celsius = volts / kelvin

def format_as_fahrenheit(temp):
    temp = rankine(temp)
    return "%.0f °F" % (temp.num - 459.67)
def format_as_celsius(temp):
    temp = kelvin(temp)
    return "%.0f °C" % (temp.num - 273.15)
