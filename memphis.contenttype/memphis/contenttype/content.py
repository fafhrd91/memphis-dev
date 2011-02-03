"""

$Id: content.py 11717 2011-01-25 07:35:53Z fafhrd91 $
"""


class Content(object):

    def __init__(self, item, relation=None):
        self.item = item
        self.relation = relation
