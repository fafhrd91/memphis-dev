""" vocabularies """
from zope import interface
from zope.component import getUtilitiesFor
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from interfaces import IRenderer


def getRenderers():
    renderers = [(renderer.title, name)
                 for name, renderer in getUtilitiesFor(IRenderer)]
    renderers.sort()

    return SimpleVocabulary([
            SimpleTerm(name, name, title) for title, name in renderers])
