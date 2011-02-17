import datetime
from zope import interface
from memphis import view, config, form, contenttype
from memphis.versions.interfaces import IVersionsBehavior, IVersionsSchema


config.action(
    view.registerActions,
    ('versions.html', IVersionsBehavior, 
     'Versions', 'Content versioning support.', 1000))


class Versions(view.View):
    view.pyramidView(
        'versions.html', IVersionsBehavior,
        template = view.template('memphis.versions:templates/versions.pt'))

    def update(self):
        self.versions = IVersionsBehavior(self.context)


class EditVersionContent(form.SubForm, view.Pagelet):
    interface.implements(form.ISubForm)
    config.adapts(IVersionsBehavior, None, contenttype.IEditContentForm,
                  name = 'edit.content.version')

    fields = form.Fields(IVersionsSchema).omit('proxy', 'date', 'version')
    fields['commit'].widgetFactory = 'singlecheckbox'

    def getContent(self):
        return IVersionsSchema(self.context)

    def applyChanges(self, data):
        changed = super(EditVersionContent, self).applyChanges(data)
        if changed:
            content = self.getContent()
            content.date = datetime.datetime.now()

        return changed
