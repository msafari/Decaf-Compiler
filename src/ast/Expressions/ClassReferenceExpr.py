from Expr import *
from ast.Type import *

class ClassReferenceExpr(Expr):
    def __init__(self, cref, lines):
        self.lines = lines
        self.classref = cref
        self.__typeof = None
    def __repr__(self):
        return "ClassReference({0})".format(self.classref.name)

    def typeof(self):
        if (self.__typeof == None):
            self.__typeof = Type(self.classref, literal=True)
        return self.__typeof