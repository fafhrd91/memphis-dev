""" content dump view """
from StringIO import StringIO
from memphis import view, content, config


class DumpView(view.View):
    view.zopeView('dumpall')

    def __call__(self):
        out = StringIO()
        context = self.context

        print >>out, '============================='
        print >>out, context.__class__, context.__class__.__bases__
        print >>out, repr(context)
        print >>out, '\n'
        items = context.__dict__.items()
        items.sort()
        for k, v in items:
            try:
                print >>out, '%s: '%k, repr(v)
            except:
                pass

        return out.getvalue()


class ContentDumpView(DumpView):
    view.zopeView('dumpall', content.IContent)

    def __call__(self):
        out = StringIO()

        print >>out, '\n\n--------- datasheets --------'
        for key, val in self.context.__datasheets__.items():
            print >> out, '\nDatasheet: %s'%key
            print >> out, '------------'
            items = list(val.items())
            items.sort()
            for k, v in items:
                print >>out, '%s: %s'%(k, v)

        return super(ContentDumpView, self).__call__() + out.getvalue()
