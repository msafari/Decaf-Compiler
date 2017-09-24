from Expr import *
from ast.Type import *
from ast.Class import *
import ast.Config as Config

class ThisExpr(Expr):
	def __init__(self, lines):
		self.lines = lines
		self.current_class = None
		self.__typeof = None
	def __repr__(self):
		return "This"
	def typeof(self):
		if (self.__typeof == None):
			self.current_class = Config.current_class
			self.__typeof = Type(self.current_class)

		return self.__typeof