from Expr import *
from ast.ast_helpers import *
from ast.Type import *

class ArrayAccessExpr(Expr):
    def __init__(self, base, index, lines):
        self.lines = lines
        self.base = base
        self.index = index
        self.__typeof = None
    def __repr__(self):
        return "Array-access({0}, {1})".format(self.base, self.index)

    def typeof(self):
        if (self.__typeof == None):
            if (not self.index.typeof().isint()):
                signal_type_error("Type error in index of Array Index expression: integer expected, found {0}".format(str(self.index.typeof())), self.index.lines)
                mytype = Type('error')
            if (self.base.typeof().kind != 'array'):
                signal_type_error("Type error in base of Array Index expression: array type expected, found {0}".format(str(self.base.typeof())), self.base.lines)
                mytype = Type('error')
            else:
                mytype = self.base.typeof().basetype
            self.__typeof = mytype
        return self.__typeof