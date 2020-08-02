from uuid import uuid4


a= 1
f=5

class User:
    def __init__(self, name):
        self.name = name
        self.id = uuid4()

    def split(self):
        return self.name.split(",")

u = User()