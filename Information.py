from uuid import uuid4


class InfoBox:

    def __init__(self):
        self.id = uuid4()


class Link(InfoBox):

    def __init__(self, link: str, objectives: dict):
        super().__init__()
        self.link = link
        self.objectives = objectives

    def __call__(self, *args, **kwargs):
        objective = kwargs.get('objective')
        if objective is None:
            raise ValueError('Calling Link without specific objective')

        # Like this:
        return self.objectives[objective](self.link)

