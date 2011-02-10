from memphis import container, storage, view, config


from interfaces import IBehaviorType, IContentContainer


class ContentContainer(container.SimpleContainer):
    storage.behavior('content.container', IContentContainer,
                     relation = container.ISimpleContainerRelation,
                     type = IBehaviorType,
                     title = 'Container',
                     description = 'Allow contain other content types.')
