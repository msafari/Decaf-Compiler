from Expr import *
from ast.ast_helpers import *
from ast.Type import *

class AutoExpr(Expr):
    def __init__(self, arg, oper, when, lines):
        self.lines = lines
        self.arg = arg
        self.oper = oper
        self.when = when
        self.__typeof = None
    def __repr__(self):
        return "Auto({0}, {1}, {2})".format(self.arg, self.oper, self.when)

    def typeof(self):
        if (self.__typeof == None):
            argtype = self.arg.typeof()
            if (argtype.isnumeric()):
                self.__typeof = argtype
            else:
                self.__typeof = Type('error')
                if (argtype.isok()):
                    signal_type_error('Type error in auto expression: int/float expected, found {0}'.format(str(argtype)), self.lines)
        return self.__typeof