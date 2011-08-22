""" datasheet edit form """
from memphis import form, view
from memphis.content.interfaces import _, IContent, IDatasheet

from pagelets import IDatasheetForm


class DatasheetEdit(form.SubForm):
    #view.pagelet(IDatasheetForm, IDatasheet)

    @property
    def prefix(self):
        return self.context.__id__

    @property
    def fields(self):
        return form.Fields(self.context.__schema__, omitReadOnly=True)

    @property
    def label(self):
        if self.context.__id__ != 'content.instance':
            return self.context.__title__

    @property
    def description(self):
        if self.context.__id__ != 'content.instance':
            return self.context.__description__
