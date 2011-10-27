import re

def dk_format(v):
    return '%s %s %s %s' % (v[:4], v[4:6], v[6:8], v[8:10])

def gb_format(v):
    if len(v) == 11:
        return '%s %s %s' % (v[:5], v[5:9], v[9:11])
    if len(v) == 14:
        return '%s %s' % (gb_format(v[:11]), v[11:15])
    return v

def fr_format(v):
    return '%s %s' % (v[:4], v[4:])

# List created from information available at:
# http://ec.europa.eu/taxation_customs/vies/faqvies.do#item19
# and a little from:
# http://www.skatteverket.se/foretagorganisationer/moms/momsvidhandelmedeulander/kontrollerakoparensmomsregisteringsnummer/momsregistreringsnummer.4.18e1b10334ebe8bc80002649.html

# Values in the dict are tuples containing 2-3 elements: Country name,
# compiled regular expression object and an optional format function

VAT = {
    'AT': (u"Austria", re.compile(r'^ATU\d{8}$')),
    'BE': (u"Belgium", re.compile(r'^BE0?\d{9}$')),
    'BG': (u"Bulgaria", re.compile(r'^BG\d{9,10}$')),
    'CY': (u"Cyprus", re.compile(r'^CY\d{8}[A-Z]$')),
    'CZ': (u"Czech Republic", re.compile(r'^CZ\d{8,10}$')),
    'DE': (u"Germany", re.compile(r'^DE\d{9}$')),
    'DK': (u"Denmark", re.compile(r'^DK\d{8}$'), dk_format),
    'EE': (u"Estonia", re.compile(r'^EE\d{9}$')),
    'EL': (u"Greece", re.compile(r'^EL\d{9}$')),
    'ES': (u"Spain", re.compile(r'^ES[A-Z0-9]\d{7}[A-Z0-9]$')),
    'FI': (u"Finland", re.compile(r'^FI\d{8}$')),
    'FR': (u"France", re.compile(r'^FR[A-HJ-NP-Z0-9][A-HJ-NP-Z0-9]\d{9}$'),
           fr_format),
    'GB': (u"United Kingdom",
           re.compile(r'^(GB(GD|HA)\d{3}|GB\d{9}|GB\d{12})$'),
           gb_format),
    'HU': (u"Hungary", re.compile(r'^HU\d{8}$')),
    'IE': (u"Ireland", re.compile(r'^IE\d[A-Z0-9\+\*]\d{5}[A-Z]$')),
    'IT': (u"Italy", re.compile(r'^IT\d{11}$')),
    'LT': (u"Lithuania", re.compile(r'^LT(\d{9}|\d{12})$')),
    'LU': (u"Luxembourg", re.compile(r'^LU\d{8}$')),
    'LV': (u"Latvia", re.compile(r'^LV\d{11}$')),
    'MT': (u"Malta", re.compile(r'^MT\d{8}$')),
    'NL': (u"The Netherlands", re.compile(r'^NL\d{9}B\d{2}$')),
    'PL': (u"Poland", re.compile(r'^PL\d{10}$')),
    'PT': (u"Portugal", re.compile(r'^PT\d{9}$')),
    'RO': (u"Romania", re.compile(r'^RO\d{2,10}$')),
    'SE': (u"Sweden", re.compile(r'^SE\d{10}01$')),
    'SI': (u"Slovenia", re.compile(r'^SI\d{8}$')),
    'SK': (u"Slovakia", re.compile(r'^SK\d{10}$')),
}

EU_VATS = VAT.keys()

class CommunicationError(Exception):
    """There was en error in the communication with a remote API."""
    pass


def validate(s, external_validation=False):
    """
    >>> validate('ATU99999999')[0]
    True
    >>> validate('BE0999999999')[0]
    True
    >>> validate('BG9999999999')[0]
    True
    >>> validate('BG999999999')[0]
    True
    >>> validate('CY99999999L')[0]
    True
    >>> validate('CZ9999999999')[0]
    True
    >>> validate('CZ999999999')[0]
    True
    >>> validate('CZ99999999')[0]
    True
    >>> validate('DE999999999')[0]
    True
    >>> validate('DK99 99 99 99')[0]
    True
    >>> validate('EE999999999')[0]
    True
    >>> validate('EL999999999')[0]
    True
    >>> validate('ESX9999999X')[0]
    True
    >>> validate('FI99999999')[0]
    True
    >>> validate('FRXX 999999999')
    (True, 'FRXX 999999999')
    >>> validate('FRII 999999999')[0]
    False
    >>> validate('GBHA999')[0]
    True
    >>> validate('GBGD999')[0]
    True
    >>> validate('GBPD999')[0]
    False
    >>> validate('GB999 9999 99 999')
    (True, 'GB999 9999 99 999')
    >>> validate('GB999999999')
    (True, 'GB999 9999 99')
    >>> validate('GB999 9999 99')
    (True, 'GB999 9999 99')
    >>> validate('HU99999999')[0]
    True
    >>> validate('IE9+99999A')[0]
    True
    >>> validate('IE9*99999B')[0]
    True
    >>> validate('IE9C99999D')[0]
    True
    >>> validate('IT99999999999')[0]
    True
    >>> validate('LT999999999999')[0]
    True
    >>> validate('LT999999999')[0]
    True
    >>> validate('LU99999999')[0]
    True
    >>> validate('LV99999999999')[0]
    True
    >>> validate('MT99999999')[0]
    True
    >>> validate('NL999999999B99')[0]
    True
    >>> validate('PL9999999999')[0]
    True
    >>> validate('PT999999999')[0]
    True
    >>> validate('RO9')[0]
    False
    >>> validate('RO99')[0]
    True
    >>> validate('RO999999999')[0]
    True
    >>> validate('SE999999999901')[0]
    True
    >>> validate('SI99999999')[0]
    True
    >>> validate('SK9999999999')[0]
    True
    """
    s = s.replace(' ', '')
    s = s.upper()

    if len(s) < 2:
        return False

    country_code = s[:2]

    if not VAT.has_key(country_code):
        return False, None

    try:
        country_name, validator, format_fun = VAT[country_code]
    except ValueError, e:
        country_name, validator = VAT[country_code]
        format_fun = lambda v: v

    if not validator.match(s):
        return False, None

    s = format_fun(s)

    if external_validation and country_code in EU_VATS:
        if not eu_validation(country_code, s[2:]):
            return False, None

    return True, s

WSDL = 'http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'
def eu_validation(country_code, vat_number):
    """
    >>> eu_validation('SE', '556814968501')
    True
    """
    try:
        import suds
    except ImportError:
        raise ImportError("suds is require to validate against the European "
                          "Commission's web service.")

    c = suds.client.Client(WSDL)
    try:
        v = c.service.checkVat(country_code, vat_number)
    except suds.WebFault:
        raise CommunicationError()

    # there are some pretty interesting properties attached to the validation
    # instance. exposing those might be in the scope of this application.
    return v.valid

if __name__ == '__main__':
    import doctest
    doctest.testmod()
