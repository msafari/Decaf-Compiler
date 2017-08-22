class ReturnStmt(Stmt):
    def __init__(self, expr, lines):
        self.lines = lines
        self.expr = expr
        self.__typecorrect = None

    def printout(self):
        print "Return(",
        if (self.expr != None):
            self.expr.printout()
        print ")"

    def typecheck(self):
        global current_method
        if (self.__typecorrect == None):
            if (self.expr == None):
                argtype = Type('void')
            else:
                argtype = self.expr.typeof()
            self.__typecorrect = argtype.is_subtype_of(current_method.rtype)
            if (argtype.isok() and (not self.__typecorrect)):
                signal_type_error("Type error in Return statement: {0} expected, found {1}".format(str(current_method.rtype), str(argtype)), self.lines)
        return self.__typecorrect

    def has_return(self):
        return 2