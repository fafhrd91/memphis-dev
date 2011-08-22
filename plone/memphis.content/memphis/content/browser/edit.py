""" content edit form """
from zope import interface
from memphis import form, config, view, content
from memphis.content.interfaces import _, IContent

from datasheet import DatasheetEdit
from interfaces import IEditContentForm


class EditContent(form.EditForm, view.View):
    interface.implements(IEditContentForm)
    view.zopeView('edit.html', IContent,
                  layout = 'body',
                  permission = 'Modify portal content')

    fields = form.Fields()

    @property
    def label(self):
        return 'Edit %s'%self.context.__type__.title

    def listInlineForms(self):
        context = self.context
        ct = context.__type__

        forms = []
        for schId in ct.schemas:
            schema = content.querySchema(schId)
            if schema is not None:
                ds = context.getDatasheet(schId)
                eform = DatasheetEdit(ds, self.request, self)
                eform.mode = self.mode
                eform.update()
                forms.append((schId, eform))

        forms.extend(super(EditContent, self).listInlineForms())
        return forms
