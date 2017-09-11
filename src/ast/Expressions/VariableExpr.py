class VarExpr(Expr):
    def __init__(self, var, lines):
        self.lines = lines
        self.var = var
        self.__typeof = None
        self.objID = None
    def __repr__(self):
        return "Variable(%d)"%self.var.id

    def typeof(self):
        if (self.__typeof == None):
            self.__typeof = self.var.type
        return self.__typeof