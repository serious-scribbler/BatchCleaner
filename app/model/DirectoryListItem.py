

class DirectoryListItem():

    def __init__(self, id: str, parent: dict, path: str, recursive:bool = False):
        self.parent = parent
        self.path = path
        self.recursive = recursive

    def delete(self):
        self.parent