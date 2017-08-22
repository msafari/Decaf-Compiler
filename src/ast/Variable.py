class Variable:
    """ Record for a single variable"""
    def __init__(self, vname, id, vkind, vtype):
        self.name = vname
        self.id = id
        self.kind = vkind
        self.type = vtype

    def printout(self):
        print "VARIABLE {0}, {1}, {2}, {3}".format(self.id, self.name, self.kind, self.type)