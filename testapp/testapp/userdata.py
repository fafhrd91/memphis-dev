from zope import interface, schema
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from pyramid.i18n import TranslationStringFactory
from memphis import storage, config, form, view, users

_ = TranslationStringFactory('learningweb')


COLLEGES = (
        'Central',
        'Coleman',
        'District',
        'Northeast',
        'Northwest',
        'Southeast',
        'Southwest',
        )

COLLEGE_VOCAB = SimpleVocabulary(
    [SimpleTerm('', title=_('Select a college'))] +
    [SimpleTerm(college, title=_(college)) for college in COLLEGES])


class ILearningWebUserData(interface.Interface):
    storage.schema('learningweb')

    firstname = schema.TextLine(
        title=_(u'First Name'),
        description=_(u'Your first name as it appears on your syllabus.'),
        required=True)

    lastname = schema.TextLine(
        title=_(u'Last Name'),
        description=_(u'Your last name as it appears on your syllabus.'),
        required=True)

    jobtitle = schema.TextLine(
        title=_(u'Job Title'),
        description=_(u'Your job title (e.g. Professor).'),
        required=False)

    college = schema.Choice(
        title=_(u'College'),
        description=_(u'Your primary college affiliation (select one).'),
        vocabulary=COLLEGE_VOCAB,
        required=True)

    department = schema.TextLine(
        title=_(u'Department(s)'),
        description=_(u'All departments for which you currently teach.'),
        required=False)

    email = schema.ASCIILine(
        title=_('E-mail'),
        description=_(
            'Your college e-mail address. This will be used to '
            'authenticate your registration and generate your login name '
            'for this site.'),
        required=True)

    phone = schema.TextLine(
        title=_(u'Phone'),
        description=_("Your college phone number (use your department's "
                      "number if you haven't been assigned one)."),
        required=False)

    campus = schema.TextLine(
        title=_(u'Office/Campus'),
        description=_(u'Your office number or primary campus.'),
        required=False)
    
    #portrait = FileUpload(
    #    title=_(u'Portrait'),
    #    description=_('A current photograph for use on your home page - '
    #                  'recommended image size is 120 pixels wide by 160 pixels tall '
    #                  'with a resolution of 72 dpi.'),
    #    required=False)
    
    #curriculum_vitae = FileUpload(
    #    title=_(u'Curriculum Vitae'),
    #    description=_('Upload a copy of your current CV, preferably as a '
    #                  'PDF document.'),
    #    required=False)
    
    #subjectAreas = schema.Set(
    #    title=_(u'Subject Areas'),
    #    description=_(u'Select the subject areas in which you teach.'),
    #    required=True,
    #    value_type=schema.Choice(
    #        source=SubjectAreaSourceBinder()))


class RegistrationForm(form.SubForm):
    config.adapts(None, None, users.IRegistrationForm)

    ignoreContext = True
    fields = form.Fields(ILearningWebUserData).omit('firstname', 'lastname')

    def getContent(self):
        return self.parentForm.principal
