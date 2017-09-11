class ForStmt(Stmt):
    def __init__(self, init, cond, update, body, lines):
        self.lines = lines
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body
        self.__typecorrect = None

    def printout(self):
        print "For(",
        if (self.init != None):
            self.init.printout()
        print ", ",
        if (self.cond != None):
            self.cond.printout()
        print ", ",
        if (self.update != None):
            self.update.printout()
        print ", ",
        self.body.printout()
        print ")"

    def typecheck(self):
        if (self.__typecorrect == None):
            a = True
            if (self.init != None):
                a = a and self.init.typeof().isok()
            if (self.update != None):
                a = a and self.update.typeof().isok()
            if (self.cond != None):
                b = self.cond.typeof()
                if (not b.isboolean()):
                    signal_type_error("Type error in For statement's condition: boolean expected, found {0}".format(str(b)), self.lines)
                    a = False
            a = a and self.body.typecheck()
            self.__typecorrect = a
        return self.__typecorrect
        
    def has_return(self):
        # 0 if none, 1 if at least one path has a return, 2 if all paths have a return
        if (self.body.has_return() > 0):
            return 1
        else:
            return 0