# python package

from memphis.schema import api
from memphis.schema.interfaces import _
from memphis.schema.richtext.field import RichText

# RichText
api.registerField('richtext', RichText, 
                  _("Rich text"),
                  _("Text field with different mime type support."))
