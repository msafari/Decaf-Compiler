from Expr import *
from ast.ast_helpers import *
from ast.Type import *
from ast.Class import *
import ast.Config as Config

class SuperExpr(Expr):
	def __init__(self, lines):
		self.lines = lines
		self.__typeof = None
		self.current_class = None
	def __repr__(self):
		return "Super"

	def typeof(self):
		if (self.__typeof == None):
			if (Config.current_class.superclass != None):
				self.current_class = Config.current_class
				self.__typeof = Type(self.current_class.superclass)
			else:
				self.__typeof = Type('error')
				signal_type_error("Type error in Super expression: class {0} has no superclass".format(str(self.current_class)), self.lines)
		return self.__typeof