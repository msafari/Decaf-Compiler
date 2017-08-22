class BlockStmt(Stmt):
    def __init__(self, stmtlist, lines):
        self.lines = lines
        self.stmtlist = [s for s in stmtlist if (s != None) and (not isinstance(s, SkipStmt))]
        self.__typecorrect = None

    def printout(self):
        print "Block(["
        if (len(self.stmtlist) > 0):
            self.stmtlist[0].printout()
        for s in self.stmtlist[1:]:
            print ", ",
            s.printout()
        print "])"

    def typecheck(self):
        if (self.__typecorrect == None):
            self.__typecorrect = all([s.typecheck() for s in self.stmtlist])
        return self.__typecorrect

    def has_return(self):
        rs = [s.has_return() for s in self.stmtlist]
        if (2 in rs):
            return 2
        elif (1 in rs):
            return 1
        else:
            return 0