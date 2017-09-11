class SuperExpr(Expr):
    global current_class
    def __init__(self, lines):
        self.lines = lines
        self.__typeof = None
        self.current_class = None
    def __repr__(self):
        return "Super"

    def typeof(self):
        if (self.__typeof == None):
            if (current_class.superclass != None):
                self.__typeof = Type(current_class.superclass)
                self.current_class = current_class
            else:
                self.__typeof = Type('error')
                signal_type_error("Type error in Super expression: class {0} has no superclass".format(str(current_class)), self.lines)
        return self.__typeof