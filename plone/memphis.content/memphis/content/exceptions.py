""" memphis content exceptions """

class BaseContentException(Exception):
    """ base class for content exceptions """


class BehaviorException(BaseContentException):
    """ base class for behavior exceptions """


class BehaviorNotFound(LookupError):
    """ behavior not found exceptions """


class SchemaNotFound(LookupError):
    """ schema not found exceptions """


class DatasheetException(BaseContentException):
    """ base class for datasheet exceptions """
