from VarTable import *

lastconstructor = 0

class Constructor:
    """A class encoding constructors and their attributes in Decaf"""
    def __init__(self, cname, visibility):
        global lastconstructor
        self.name = cname
        lastconstructor += 1
        self.id = lastconstructor
        self.visibility = visibility
        self.vars = VarTable()
        
    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def printout(self):
        print "CONSTRUCTOR: {0}, {1}".format(self.id, self.visibility)
        print "Constructor Parameters:",
        print ', '.join(["%d"%v.id for v in self.vars.get_params()])
        self.vars.printout()
        print "Constructor Body:"
        self.body.printout()

    def argtypes(self):
        return [v.type for v in self.vars.get_params()]
        
    def typecheck(self):
        self.body.typecheck()