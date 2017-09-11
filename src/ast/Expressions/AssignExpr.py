class AssignExpr(Expr):
    def __init__(self, lhs, rhs, lines):
        self.lines = lines
        self.lhs = lhs
        self.rhs = rhs
        #If this assign is for creating a new obj, pass the ID to use for getting heap offset
        if isinstance(self.rhs, NewObjectExpr):
            #The left hand side is either FieldAccess or VarExpr
            if isinstance(self.lhs, FieldAccessExpr):
                varID = self.lhs.base.var.id
                self.rhs.objID = varID
                self.lhs.objID = varID
            else:
                varID = self.lhs.var.id
                self.rhs.objID = varID
                self.lhs.objID = varID
        self.__typeof = None
    def __repr__(self):
        return "Assign({0}, {1}, {2}, {3})".format(self.lhs, self.rhs, self.lhs.typeof(), self.rhs.typeof())

    def typeof(self):
        if (self.__typeof == None):
            lhstype = self.lhs.typeof()
            rhstype = self.rhs.typeof()
            if (lhstype.isok() and rhstype.isok()):
                if (rhstype.is_subtype_of(lhstype)):
                    self.__typeof = rhstype
                else:
                    self.__typeof = Type('error')
                    signal_type_error('Type error in assign expression: compatible types expected, found {0} and {1}'.format(str(lhstype), str(rhstype)), self.lines)
            else:
                self.__typeof = Type('error')
        return self.__typeof