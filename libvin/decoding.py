"""
libvin - VIN Vehicle information number checker
(c) Copyright 2012 Maxime Haineault <max@motion-m.ca>
"""

from libvin.static import *
from libvin import wmi_map


VIN_SIZE = 17
"""For model years 1981 to present, the VIN is composed of 17 
alphanumeric values"""


PROHIBITED_LETTERS = 'IOQ'
r"""The letters I,O, Q are prohibited from any VIN position"""


PROHIBITED_MODEL_LETTERS = 'UZ0'
r"""The tenth position of the VIN represents the Model Year and 
does not permit the use of the characters U and Z, as well 
as the numeric zero (0)
"""


r"""The ninth position of the VIN is a calculated value based on 
the other 16 alphanumeric values, it's called the 
"Check Digit". The result of the check digit can ONLY be a 
numeric 0-9 or letter "X".
"""
ALLOWED_CHECK_DIGIT_LETTERS = 'X0123456789'


class BadVin(Exception):
    r"""If VIN is incorrect according to specification, exception is raised."""
    pass

class Vin(object):

    def __init__(self, vin):
        if not vin:
            raise BadVin('Vin is empty')
        
        self.vin = vin.upper()
        
        if not self.is_valid():
            raise BadVin('Vin is not valid')

    @property
    def country(self):
        """
        Returns the World Manufacturer's Country.
        """
        if not self.vin[0] in WORLD_MANUFACTURER_MAP:
            return None

        countries = WORLD_MANUFACTURER_MAP[self.vin[0]]['countries']

        for codes in countries:
            if self.vin[0] in codes:
                return countries[codes]

        return None

    def decode(self):
        return self.vin

    def is_valid(self):
        r"""Returns True if a VIN is valid, otherwise returns False."""
        if hasattr(self, '_is_valid'):
            return getattr(self, '_is_valid')
        
        _is_valid = False
        
        if len(self.vin) != VIN_SIZE:
            _is_valid = False
        elif any(x in PROHIBITED_LETTERS for x in self.vin):
            _is_valid = False
        elif self.vin[9] in PROHIBITED_MODEL_LETTERS:
            _is_valid = False
        elif not self.vin[8] in ALLOWED_CHECK_DIGIT_LETTERS:
            _is_valid = False
        else:
            _is_valid = True

        setattr(self, '_is_valid', _is_valid)
        return _is_valid

    @property
    def is_pre_2010(self):
        """
        Returns true if the model year is in the 1980-2009 range

        In order to identify exact year in passenger cars and multipurpose 
        passenger vehicles with a GVWR of 10,000 or less, one must read 
        position 7 as well as position 10. For passenger cars, and for 
        multipurpose passenger vehicles and trucks with a gross vehicle 
        weight rating of 10,000 lb (4,500 kg) or less, if position 7 is 
        numeric, the model year in position 10 of the VIN refers to a year 
        in the range 1980-2009. If position 7 is alphabetic, the model year 
        in position 10 of VIN refers to a year in the range 2010-2039.
        """
        return self.vin[6].isdigit()

    @property
    def less_than_500_built_per_year(self):
        """
        A manufacturer who builds fewer than 500 vehicles 
        per year uses a 9 as the third digit
        """
        try:
            return int(self.vin[2]) is 9
        except ValueError:
            return False

    @property
    def region(self):
        """
        Returns the World Manufacturer's Region. Possible results:
        """
        if not self.vin[0] in WORLD_MANUFACTURER_MAP:
            return None
        return WORLD_MANUFACTURER_MAP[self.vin[0]]['region']

    @property
    def vis(self):
        """
        Returns the Vehicle Idendifier Sequence (ISO 3779)
        Model Year, Manufacturer Plant and/or Serial Number
        """
        return self.vin[-8:]

    @property
    def vds(self):
        """
        Returns the Vehicle Descriptor Section (ISO 3779)
        Assigned by Manufacturer; Check Digit is Calculated
        """
        return self.vin[3:9]

    @property
    def vsn(self):
        """
        Returns the Vehicle Sequential Number
        """
        if self.less_than_500_built_per_year:
            return self.vin[-3:]
        else:
            return self.vin[-6:]

    @property
    def wmi(self):
        """
        Returns the World Manufacturer Identifier (any standards)
        Assigned by SAE
        """
        return self.vin[0:3]

    @property
    def manufacturer(self):
        wmi = self.wmi
        print self.wmi
        if wmi[:3] in wmi_map.WMI_MAP:
            return wmi_map.WMI_MAP[wmi[:3]]
        if wmi[:2] in wmi_map.WMI_MAP:
            return wmi_map.WMI_MAP[wmi[:2]]
        return None

    make = manufacturer

    @property
    def year(self):
        """
        Returns the model year of the vehicle
        """
        if self.is_pre_2010:
            return YEARS_CODES_PRE_2010.get(self.vin[9], None)
        else:
            return YEARS_CODES_PRE_2040.get(self.vin[9], None)


def decode(vin):
    v = Vin(vin)
    return v.decode()
