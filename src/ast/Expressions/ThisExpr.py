class ThisExpr(Expr):
    global current_class
    def __init__(self, lines):
        self.lines = lines
        self.current_class = None
        self.__typeof = None
    def __repr__(self):
        return "This"
    def typeof(self):
        if (self.__typeof == None):
            self.__typeof = Type(current_class)
            self.current_class = current_class
        return self.__typeof