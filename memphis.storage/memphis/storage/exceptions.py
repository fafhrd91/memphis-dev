""" storage exceptions """

class BaseException(Exception):
    """ base class for storage exceptions """


class StorageException(BaseException):
    """ storage related exceptions """


class BehaviorException(BaseException):
    """ base class for behavior exceptions """


class BehaviorNotFound(LookupError):
    """ behavior not found exceptions """


class SchemaNotFound(LookupError):
    """ schema not found exceptions """


class DatasheetException(BaseException):
    """ base class for datasheet exceptions """
