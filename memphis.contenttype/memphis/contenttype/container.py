from memphis import container, storage, view, config


from interfaces import IContentContainer


class ContentContainer(container.SimpleContainer):
    storage.behavior('content.container', IContentContainer)
