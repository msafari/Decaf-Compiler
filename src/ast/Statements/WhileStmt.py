from Stmt import *
from ast.ast_helpers import *

class WhileStmt(Stmt):
    def __init__(self, cond, body, lines):
        self.lines = lines
        self.cond = cond
        self.body = body
        self.__typecorrect = None

    def printout(self):
        print "While(",
        self.cond.printout()
        print ", ",
        self.body.printout()
        print ")"

    def typecheck(self):
        if (self.__typecorrect == None):
            b = self.cond.typeof()
            if (not b.isboolean()):
                signal_type_error("Type error in While statement's condition: boolean expected, found {0}".format(str(b)), self.lines)
                self.__typecorrect = False
            self.__typecorrect = b.isboolean() and self.body.typecheck()
        return self.__typecorrect

    def has_return(self):
        # 0 if none, 1 if at least one path has a return, 2 if all paths have a return
        if (self.body.has_return() > 0):
            return 1
        else:
            return 0