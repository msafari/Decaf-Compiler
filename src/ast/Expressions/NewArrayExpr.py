from Expr import *
from ast.ast_helpers import *
from ast.Type import *

class NewArrayExpr(Expr):
    def __init__(self, basetype, args, lines):
        self.lines = lines
        self.basetype = basetype
        self.args = args
        self.__typeof = None
    def __repr__(self):
        return "New-array({0}, {1})".format(self.basetype, self.args)

    def typeof(self):
        if (self.__typeof == None):
            mytype = Type(self.basetype, len(self.args))
            for a in self.args:
                if (not a.typeof().isok()):
                    # previous error, so mark and pass
                    mytype = Type('error')
                    break
                if (not a.typeof().isint()):
                    # int arg type expected
                    signal_type_error("Type error in argument to New Array expression: int expected, found {0}".format(str(a.typeof())), a.lines)
                    mytype = Type('error')
                    break
            self.__typeof = mytype
        return self.__typeof