from django import forms

from vat import validate

class VATField(forms.CharField):
    """
    >>> f = VATField(external_validation=True)
    >>> f.clean("SE556056625801")
    'SE556056625801'
    """
    def __init__(self, external_validation=False, required=True):
        self.external_validation = external_validation
        super(VATField, self).__init__(required=required, min_length=3)

    def clean(self, value):
        if not value:
            return value

        try:
            is_valid, vat_number = validate.validate(value,
                                                     self.external_validation)
        except validate.CommunicationError:
            raise forms.ValidationError(u"Unable to contact VAT validation "
                                        u"service.")
        if not is_valid:
            raise forms.ValidationError(u"Not a valid VAT number.")

        return vat_number

if __name__ == '__main__':
    import doctest
    doctest.testmod()
