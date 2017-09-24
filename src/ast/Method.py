from VarTable import *
import Config
lastmethod = 0

class Method:
    """A class encoding methods and their attributes in Decaf"""
    def __init__(self, mname, mclass, visibility, storage, rtype):
        global lastmethod
        self.name = mname
        lastmethod += 1
        self.id = lastmethod
        self.inclass = mclass
        self.visibility = visibility
        self.storage = storage
        self.rtype = rtype
        self.vars = VarTable()
        
    def update_body(self, body):
        self.body = body

    def add_var(self, vname, vkind, vtype):
        self.vars.add_var(vname, vkind, vtype)

    def printout(self):
        print "METHOD: {0}, {1}, {2}, {3}, {4}, {5}".format(self.id, self.name, self.inclass.name, self.visibility, self.storage, self.rtype)
        print "Method Parameters:",
        print ', '.join(["%d"%v.id for v in self.vars.get_params()])
        self.vars.printout()
        print "Method Body:"
        self.body.printout()

    def argtypes(self):
        return [v.type for v in self.vars.get_params()]

    def typecheck(self):
        Config.current_method = self
        self.body.typecheck()