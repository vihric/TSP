class PseudoItem:
    def __init__(self, name="DEFAULT", uid=0, tags=None):
        self.name = name
        self.id = uid
        if tags is None:
            self.tags = {}
        else:
            self.tags = tags

class PseudoTag:
    def __init__(self, name="DEFAULT", uid=0):
        self.name = name
        self.id = uid
