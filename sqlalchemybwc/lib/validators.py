import formencode
from savalidation.validators import EntityLinker, ValidatorBase


class BaseValidator(formencode.validators.FancyValidator):
    def __classinit__(cls, new_attrs):
        depricated_methods = getattr(cls, '_deprecated_methods', None) or \
            new_attrs.get('_deprecated_methods')
        if depricated_methods is not None:
            for old, new in depricated_methods:
                if old in new_attrs:
                    method = new_attrs.pop(old)
                    setattr(cls, new, method)
                    new_attrs[new] = method
        return formencode.validators.FancyValidator.__classinit__(cls, new_attrs)


class _UniqueValidator(BaseValidator):
    """
    Calls the given callable with the value of the field.  If the return value
    does not evaluate to false, Invalid is raised
    """

    __unpackargs__ = ('fieldname', 'cls', 'instance')
    messages = {
        'notunique': u'the value for this field is not unique',
    }

    def validate_python(self, value, state):
        existing_record = self.cls.get_by(**{self.fieldname: value})
        if existing_record and existing_record is not state.entity:
            raise formencode.Invalid(self.message('notunique', state), value, state)


class _UniqueValidationHandler(ValidatorBase):
    type = 'field'

    def create_fe_validators(self):
        if not self.field_names:
            raise ValueError('validates_unique() must be passed at least one field name')
        for field_to_validate in self.field_names:
            valinst = _UniqueValidator(
                cls=self.entitycls,
                fieldname=field_to_validate
            )
            self.create_fev_meta(valinst, field_to_validate)


validates_unique = EntityLinker(_UniqueValidationHandler)
