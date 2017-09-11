class ConstantExpr(Expr):
	def __init__(self, kind, arg=None, lines=None):
		self.lines = lines
		self.kind = kind
		if (kind == 'int'):
			self.int = arg
		elif (kind == 'float'):
			self.floar = arg
		elif (kind == 'string'):
			self.string = arg
		self.__typeof = None

	def __repr__(self):
		s = 'Unknown'
		if (self.kind == 'int'):
			s = 'Integer-constant(%d)'%self.int
		elif (self.kind == 'float'):
            s = "Float-constant(%g)"%self.float
        elif (self.kind == 'string'):
            s = "String-constant(%s)"%self.string
        elif (self.kind == 'Null'):
            s = "Null"
        elif (self.kind == 'True'):
            s = "True"
        elif (self.kind == 'False'):
            s = "False"
        return "Constant({0})".format(s)

    def typeof(self):
        if (self.__typeof == None):
            if (self.kind == 'int'):
                self.__typeof = Type('int')
            elif (self.kind == 'float'):
                self.__typeof = Type('float')
            elif (self.kind == 'string'):
                self.__typeof = Type('string')
            elif (self.kind == 'Null'):
                self.__typeof = Type('null')
            elif (self.kind == 'True'):
                self.__typeof = Type('boolean')
            elif (self.kind == 'False'):
                self.__typeof = Type('boolean')
        return self.__typeof
