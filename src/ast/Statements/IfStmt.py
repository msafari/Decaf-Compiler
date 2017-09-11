class IfStmt(Stmt):
    def __init__(self, condition, thenpart, elsepart, lines):
        self.lines = lines
        self.condition = condition
        self.thenpart = thenpart
        self.elsepart = elsepart
        self.__typecorrect = None

    def printout(self):
        print "If(",
        self.condition.printout()
        print ", ",
        self.thenpart.printout()
        print ", ",
        self.elsepart.printout()
        print ")"

    def typecheck(self):
        if (self.__typecorrect == None):
            b = self.condition.typeof()
            if (not b.isboolean()):
                signal_type_error("Type error in If statement's condition: boolean expected, found {0}".format(str(b)), self.lines)
                self.__typecorrect = False
            self.__typecorrect = b.isboolean() and self.thenpart.typecheck() and self.elsepart.typecheck()
        return self.__typecorrect

    def has_return(self):
        # 0 if none, 1 if at least one path has a return, 2 if all paths have a return
        r = self.thenpart.has_return() + self.elsepart.has_return()
        if (r == 4):
            return 2
        elif (r > 0):
            return 1
        else:
            return 0