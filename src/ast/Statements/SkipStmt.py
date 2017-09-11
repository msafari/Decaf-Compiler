class SkipStmt(Stmt):
    def __init__(self, lines):
        self.lines = lines
        self.__typecorrect = True

    def printout(self):
        print "Skip"

    def typecheck(self):
        return self.__typecorrect

    def has_return(self):
        return 0