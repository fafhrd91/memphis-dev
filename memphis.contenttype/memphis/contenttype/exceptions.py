from zope.interface import Invalid


class DuplicateIDError(KeyError):
    pass


class ContainerError(Exception):
    """An error of a container with one of its components."""


class InvalidContainerType(Invalid, TypeError):
    """The type of a container is not valid."""


class InvalidItemType(Invalid, TypeError):
    """The type of an item is not valid."""


class InvalidType(Invalid, TypeError):
    """The type of an object is not valid."""
