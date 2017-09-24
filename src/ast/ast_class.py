import ast
import ast_helpers
from Statements.BlockStmt import *
from Statements.SkipStmt import *
from Statements.ReturnStmt import *
from Constructor import *
from Type import *
import Config

class Class:
	"""A class encoding Classes in Decaf"""
	def __init__(self, classname, superclass):
		self.name = classname
		self.superclass = superclass
		self.fields = {}  # dictionary, keyed by field name
		self.fieldList = []
		self.constructors = []
		self.methods = []
		self.builtin = False

	def printout(self):
		if (self.builtin):
			return     # Do not print builtin classes
		
		print "-----------------------------------------------------------------------------"
		print "Class Name: {0}".format(self.name)
		sc = self.superclass
		if (sc == None):
			scname = ""
		else:
			scname = sc.name
		print "Superclass Name: {0}".format(scname)
		print "Fields:"
		for f in self.fields:
			(self.fields[f]).printout()
		print "Constructors:"
		for k in self.constructors:
			k.printout()
		print "Methods:"
		for m in self.methods:
			m.printout()

	def typecheck(self):
		if (self.builtin):
			return     # Do not type check builtin classes
		Config.current_class = self

		# First check if there are overlapping overloaded constructors and methods
		n = len(self.constructors)
		for i in range(0,n):
			for j in range(i+1, n):
				at1 = self.constructors[i].argtypes()
				at2 = self.constructors[j].argtypes()
				if (not subtype_or_incompatible(at1, at2)):
					t1 = ",".join([str(t) for t in at1])
					t2 = ",".join([str(t) for t in at2])
					signal_type_error("Overlapping types in overloaded constructors: `{0}' (line {2}) and `{1}'".format(t1,t2, self.constructors[i].body.lines), self.constructors[j].body.lines)

		n = len(self.methods)
		for i in range(0,n):
			for j in range(i+1, n):
				if (self.methods[i].name != self.methods[j].name):
					# Check only overloaded methods
					break
				at1 = self.methods[i].argtypes()
				at2 = self.methods[j].argtypes()
				if (not subtype_or_incompatible(at1, at2)):
					t1 = ",".join([str(t) for t in at1])
					t2 = ",".join([str(t) for t in at2])
					signal_type_error("Overlapping types in overloaded methods: `{0}' (line {2}) and `{1}'".format(t1,t2, self.methods[i].body.lines), self.methods[j].body.lines)

		for k in self.constructors:
			k.typecheck()
			# ensure it does not have a return statement
			if (k.body.has_return() > 0):
				signal_type_error("Constructor cannot have a return statement", k.body.lines)
		for m in self.methods:
			m.typecheck()
			# ensure that non-void methods have a return statement on every path
			if (m.rtype.is_subtype_of(Type('void'))): 
				if (isinstance(m.body, BlockStmt)):
					m.body.stmtlist.append(ReturnStmt(None,m.body.lines))
				else:
					m.body = BlockStmt([m.body, ReturnStmt(None,m.body.lines)], mbody.lines)
			else:
				if (m.body.has_return() < 2):
					ast_helpers.signal_type_error("Method needs a return statement on every control flow path", m.body.lines)

	def add_field(self, fname, field):
		self.fields[fname] = field
		self.fieldList.append(field)
	def add_constructor(self, constr):
		self.constructors.append(constr)
	def add_method(self, method):
		self.methods.append(method)

	def add_default_constructor(self):
		# check if a parameterless constructor already exists
		exists = False
		for c in self.constructors:
			if (len(c.vars.get_params()) == 0):
				exists = True
				break
		if (not exists):
			c = Constructor(self.name, 'public')
			c.update_body(SkipStmt(None))
			self.constructors.append(c)            

	def lookup_field(self, fname):
		return ast.lookup(self.fields, fname)

	def lookup_field_index(self, field):
		try:
			fieldIndex = self.fieldList.index(field)
		except ValueError:
			if self.superclass:
				return self.superclass.lookup_field_index(field)
		return fieldIndex

	def is_subclass_of(self, other):
		if (self.name == other.name):
			return True
		elif (self.superclass != None):
			 if (self.superclass == other):
				 return True
			 else:
				 return self.superclass.is_subclass_of(other)
		return False