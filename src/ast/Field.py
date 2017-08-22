class Field:
    """A class encoding fields and their attributes in Decaf"""
    lastfield = 0
    def __init__(self, fname, fclass, visibility, storage, ftype):
        Field.lastfield += 1
        self.name = fname
        self.id = Field.lastfield
        self.inclass = fclass
        self.visibility = visibility
        self.storage = storage
        self.type = ftype

    def printout(self):
        print "FIELD {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.type)