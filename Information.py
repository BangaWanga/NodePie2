from uuid import uuid4
import json


class InfoBox:

    def __init__(self):
        self.id = uuid4()

    @staticmethod
    def load_json(file_path: str) -> json:
        try:
            with open(file_path, 'r') as infile:
                file = json.load(infile)

                return file
        except AssertionError:
            print("Corrupted file")
        except FileNotFoundError:
            print("No file at {}".format(file_path))

    @staticmethod
    def save_json(data: dict, file_path: str) -> bool:
        try:
            with open(file_path, 'w') as outfile:
                outfile.write(json.dumps(data))
                return True
        except:
            raise
            return False

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

