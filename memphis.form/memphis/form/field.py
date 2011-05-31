##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Field Implementation"""
import zope.component
import zope.interface
import zope.schema.interfaces

from memphis import config
from memphis.form import interfaces, util
from memphis.form.error import \
    Errors, WidgetError, MultipleErrors, StrErrorViewSnippet


def _initkw(keepReadOnly=(), omitReadOnly=False, **defaults):
    return keepReadOnly, omitReadOnly, defaults


class Field(object):
    """Field implementation."""
    zope.interface.implements(interfaces.IField)

    widgetFactory = ''

    def __init__(self, field, name=None, prefix='', mode=None, interface=None,
                 ignoreContext=None):
        self.field = field
        if name is None:
            name = field.__name__
        assert name
        self.__name__ = util.expandPrefix(prefix) + name
        self.prefix = prefix
        self.mode = mode
        if interface is None:
            interface = field.interface
        self.interface = interface
        self.ignoreContext = ignoreContext

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class Fields(util.SelectionManager):
    """Field manager."""
    zope.interface.implements(interfaces.IFields)
    managerInterface = interfaces.IFields

    def __init__(self, *args, **kw):
        keepReadOnly, omitReadOnly, defaults = _initkw(**kw)

        fields = []
        for arg in args:
            if isinstance(arg, zope.interface.interface.InterfaceClass):
                for name, field in zope.schema.getFieldsInOrder(arg):
                    fields.append((name, field, arg))

            elif zope.schema.interfaces.IField.providedBy(arg):
                name = arg.__name__
                if not name:
                    raise ValueError("Field has no name")
                fields.append((name, arg, arg.interface))

            elif self.managerInterface.providedBy(arg):
                for form_field in arg.values():
                    fields.append(
                        (form_field.__name__, form_field, form_field.interface))

            elif isinstance(arg, Field):
                fields.append((arg.__name__, arg, arg.interface))

            else:
                raise TypeError("Unrecognized argument type", arg)

        self._data_keys = []
        self._data_values = []
        self._data = {}
        for name, field, iface in fields:
            if isinstance(field, Field):
                form_field = field
            else:
                if field.readonly:
                    if omitReadOnly and (name not in keepReadOnly):
                        continue
                customDefaults = defaults.copy()
                if iface is not None:
                    customDefaults['interface'] = iface
                form_field = Field(field, **customDefaults)
                name = form_field.__name__

            if name in self._data:
                raise ValueError("Duplicate name", name)

            self._data_values.append(form_field)
            self._data_keys.append(name)
            self._data[name] = form_field


    def select(self, *names, **kwargs):
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [util.expandPrefix(prefix) + name for name in names]
        mapping = self
        if interface is not None:
            mapping = dict([(field.field.__name__, field)
                            for field in self.values()
                            if field.field.interface is interface])
        return self.__class__(*[mapping[name] for name in names])


    def omit(self, *names, **kwargs):
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [util.expandPrefix(prefix) + name for name in names]
        return self.__class__(
            *[field for name, field in self.items()
              if not ((name in names and interface is None) or
                      (field.field.interface is interface and
                       field.field.__name__ in names)) ])


class FieldWidgets(util.Manager):
    """Widget manager for IWidget."""
    config.adapts(
        interfaces.IFieldsForm,
        zope.interface.Interface)
    zope.interface.implementsOnly(interfaces.IWidgets)

    prefix = 'widgets.'
    mode = interfaces.IInputMode
    errors = ()
    hasRequiredFields = False
    ignoreContext = False
    ignoreRequest = False
    ignoreReadonly = False
    setErrors = True

    def __init__(self, form, request):
        super(FieldWidgets, self).__init__()
        self.form = form
        self.request = request
        self.content = form.getContent()

    def update(self):
        """See interfaces.IWidgets"""
        # Create a unique prefix.
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.prefix)
        request = self.request
        sm = zope.component.getSiteManager()

        # Walk through each field, making a widget out of it.
        uniqueOrderedKeys = []
        for field in self.form.fields.values():
            # Step 0. Determine whether the context should be ignored.
            ignoreContext = self.ignoreContext
            if field.ignoreContext is not None:
                ignoreContext = field.ignoreContext

            # Step 1: Determine the mode of the widget.
            mode = self.mode
            if field.mode is not None:
                mode = field.mode
            elif field.field.readonly and not self.ignoreReadonly:
                mode = interfaces.IDisplayMode

            # Step 2: Get the widget for the given field.
            shortName = field.__name__

            widget = None
            factory = field.widgetFactory
            if isinstance(factory, basestring):
                widget = sm.queryMultiAdapter(
                    (field.field, request), interfaces.IWidget, name=factory)
            elif callable(factory):
                widget = factory(field.field, request)

            if widget is None:
                widget = sm.getMultiAdapter(
                    (field.field, request), interfaces.IDefaultWidget)

            # Step 3: Set the prefix for the widget
            widget.name = str(prefix + shortName)
            widget.id = str(prefix + shortName).replace('.', '-')

            # Step 4: Set the context
            widget.context = self.content

            # Step 5: Set the form
            widget.form = self.form

            # Step 6: Set some variables
            widget.ignoreContext = ignoreContext
            widget.ignoreRequest = self.ignoreRequest

            # Step 7: Set the mode of the widget
            widget.mode = mode

            # Step 8: Update the widget
            widget.update()
            #zope.event.notify(AfterWidgetUpdateEvent(widget))

            # Step 9: Add the widget to the manager
            if widget.required:
                self.hasRequiredFields = True
            uniqueOrderedKeys.append(shortName)

            self._data_values.append(widget)
            self._data[shortName] = widget
            widget.__parent__ = self
            widget.__name__ = shortName

            # allways ensure that we add all keys and keep the order given from
            # button items
            self._data_keys = uniqueOrderedKeys

    def extract(self):
        """See interfaces.IWidgets"""
        data = {}
        sm = zope.component.getSiteManager()
        errors = Errors()
        errorViews = []

        for name, widget in self.items():
            if widget.mode == interfaces.IDisplayMode:
                continue

            value = widget.field.missing_value
            try:
                widget.setErrors = self.setErrors
                raw = widget.extract()
                if raw is not interfaces.NO_VALUE:
                    value = sm.getMultiAdapter(
                        (widget.field, widget), 
                        interfaces.IDataConverter).toFieldValue(raw)

                if value is interfaces.NOT_CHANGED and not widget.ignoreContext:
                    value = sm.getMultiAdapter(
                        (self.context, field), interfaces.IDataManager).query()

                # validate value
                field = getattr(widget, 'field', None)
                if field is not None:
                    if self.content is not None:
                        field = field.bind(self.content)
                    sm.getMultiAdapter((self.form, field),
                                       interfaces.IValidator).validate(value)
            except (zope.interface.Invalid,
                    ValueError, MultipleErrors), error:
                errors.append(WidgetError(name, error))
                view = sm.getMultiAdapter(
                    (error, self.request), interfaces.IErrorViewSnippet)
                view.update(widget)
                if self.setErrors:
                    widget.error = view
                errorViews.append(view)

            data[widget.__name__] = value

        self.form.validate(data, errors)

        for error in errors:
            if interfaces.IWidgetError.providedBy(error):
                widget = self.get(error.name)
                error = error.error
            else:
                widget = None

            view = sm.queryMultiAdapter(
                (error, self.request), interfaces.IErrorViewSnippet)
            if view is None:
                view = StrErrorViewSnippet(error, self.request)
            view.update(widget)
            errorViews.append(view)
            
            if self.setErrors and widget is not None:
                widget.error = view

        if self.setErrors:
            self.errors = errorViews

        return data, errors


class FieldValidator(object):
    """Simple Field Validator"""
    zope.interface.implements(interfaces.IValidator)
    config.adapts(zope.interface.Interface,
                  zope.schema.interfaces.IField)

    def __init__(self, form, field):
        self.form = form
        self.field = field

    def validate(self, value):
        """See interfaces.IValidator"""
        if value is not interfaces.NOT_CHANGED:
            return self.field.validate(value)

    def __repr__(self):
        return "<%s for %s['%s']>" %(
            self.__class__.__name__,
            self.field.interface.getName(), self.field.__name__)
