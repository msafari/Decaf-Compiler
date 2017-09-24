import ast
import codegen 

class abstract_machine:

	def __init__(self):
		self.availableRegNum = 0
		self.argumentRegNum = 0
		self.uniqueLabelNum = 0 # Use this number to create unique label names
		self.staticFieldOffset = {}	#A dict with keys: <field id> and values: <static area offset>
		self.loopLabelStack = []
		self.loopEndLabelStack = []

	def getNewReg(self):
		reg = "t" + str(self.availableRegNum)
		self.availableRegNum += 1
		return reg

	def getNewArgReg(self):
		reg = "a" + str(self.argumentRegNum)
		self.argumentRegNum += 1
		return reg

	def getUniqueLabelNum(self):
		temp = self.uniqueLabelNum
		self.uniqueLabelNum += 1
		return temp

	#Generate the machine directive to allocate static field space
	#Fill dictionary with offsets for each class field
	def allocateStaticFields(self):
		numFields = 0
		offset = 0

		#Iterate over each class
		for key in ast.classtable:
			dClass = ast.classtable[key]
			numFields += len(dClass.fields)
			#Iterate over each field
			for fieldname in dClass.fields:
				fieldID = dClass.fields[fieldname].id
				self.staticFieldOffset[fieldID] = offset 	#Assign the offset
				offset += 1

		code = ".static_data {0}\n".format(numFields)
		codegen.outputFile.write(code)