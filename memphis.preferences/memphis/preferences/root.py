""" Root Preference """
from zope import interface
from memphis import config, storage, view
from interfaces import _, IPreferences


class Preferences(storage.BehaviorBase):
    interface.implements(IPreferences)
    storage.behavior('memphis.preferences', schema=IPreferences)

    __title__ = _(u'Personal preferences')
    __description__ = _('This area allows you to change personal preferences.')

    __name__ = 'preferences'
    __parent__ = view.Root

    __schema__ = None # ISchema instance

    categories = {}
    preferences = {}

    @classmethod
    def get(cls, principal):
        if cls.__schema__ is None:
            cls.__schema__ = storage.getSchema(IPreferences)

        rec = cls.__schema__.query(
            cls.__schema__.Type.principal == principal).first()
        if rec is None:
            item = storage.insertItem(IPreferences)
            IPreferences(item).principal = principal
        else:
            item = storage.getItem(rec.oid)

        item.id = principal
        return Preferences(item)

    # methods for traversing
    def __contains__(self, name):
        return name in self.catgories

    def __getitem__(self, name):
        category = self.categories[name]

        clone = category.__class__.__new__(category.__class__)
        clone.update(category)
        clone.context = self.__context__
        clone.__parent__ = self
        return clone

    # access preference object
    def getPreference(self, iface):
        pref = self.preferences[iface]
        return pref.__bind__(self.item)

    @classmethod
    def addCategory(cls, category):
        if category.__name__ in cls.categories:
            raise KeyError(category.__name__)

        cls.categories[category.__name__] = category

    @classmethod
    def addPreference(cls, pref):
        cls.preferences[pref.__name__] = pref
        cls.preferences[pref.__schema__] = pref
        category = cls.categories[pref.__category__]
        category.addPreference(pref)
