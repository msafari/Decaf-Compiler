from Expr import *
from ast.ast_helpers import *
from ast.Type import *
class UnaryExpr(Expr):
    def __init__(self, uop, expr, lines):
        self.lines = lines
        self.uop = uop
        self.arg = expr
        self.__typeof = None
    def __repr__(self):
        return "Unary({0}, {1})".format(self.uop, self.arg)

    def typeof(self):
        if (self.__typeof == None):
            argtype = self.arg.typeof()
            self.__typeof = Type('error')
            if (self.uop == 'uminus'):
                if (argtype.isnumeric()):
                    self.__typeof = argtype
                elif (argtype.kind != 'error'):
                    # not already in error
                    signal_type_error("Type error in unary minus expression: int/float expected, found {0}".format(str(argtype)), self.arg.lines)
            elif (self.uop == 'neg'):
                if (argtype.isboolean()):
                    self.__typeof = argtype
                elif (argtype.kind != 'error'):
                    # not already in error
                    signal_type_error("Type error in unary negation expression: boolean expected, found {0}".format(str(argtype)), self.arg.lines)
        return self.__typeof