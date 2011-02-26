from zope import schema
from memphis.schema import api
from memphis.schema.interfaces import _

# Boolean
api.registerField('boolean', schema.Bool, 
                  _("Boolean"),
                  _("Boolean field (YES or NO)."))

# Integer
api.registerField('int', schema.Int,
                  _("Integer"),
                  _("Field containing an Integer Value."))

# Text
api.registerField('text', schema.Text,
                  _("Text"),
                  _("Field containing text with newlines."))

# Text Line
api.registerField('textline', schema.TextLine,
                  _("Text Line"),
                  _("Field containing text line without newlines."))

# Float
api.registerField('float', schema.Float,
                  _("Float"),
                  _("Field containing a Float."))

# Decimal
api.registerField('decimal', schema.Decimal,
                  _("Decimal"),
                  _("Field containing a Dicmal."))

# Date
api.registerField('date', schema.Date,
                  _("Date"),
                  _("Field containing a date."))

# Datetime
api.registerField('datetime', schema.Datetime,
                  _("DateTime"),
                  _("Field containing a DateTime."))

# Time
api.registerField('time', schema.Time,
                  _("Time"),
                  _("Field containing a time."))

# Timedelta
api.registerField('timedelta', schema.Timedelta,
                  _("Timedelta"),
                  _("Field containing a timedelta."))
