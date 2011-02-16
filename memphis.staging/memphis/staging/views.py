from memphis import view, config
from memphis.staging.interfaces import IStagingBehavior


config.action(
    view.registerActions,
    ('versions.html', IStagingBehavior, 
     'Versions', 'Content versioning support.', 1000))


class Versions(view.View):
    view.pyramidView(
        'versions.html', IStagingBehavior,
        template = view.template('memphis.staging:templates/versions.pt'))

    def update(self):
        self.staging = IStagingBehavior(self.context)
