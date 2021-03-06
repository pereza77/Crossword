import json, re
from classes import *
from util import *
from grid import *
from ast import literal_eval as make_tuple

# General code for representing a weighted CSP (Constraint Satisfaction Problem).
# All variables are being referenced by their index instead of their original
# names.
class CSP(object):
	def __init__(self):
		# Total number of variables in the CSP.
		self.numVars = 0

		# The list of variable names in the same order as they are added. A
		# variable name can be any hashable objects, for example: int, str,
		# or any tuple with hashtable objects.
		self.variables = []

		# Each key K in this dictionary is a variable name.
		# domain[K] is the list of domain values that variable K can take on.
		self.values = {}

		# Each entry is a unary factor table for the corresponding variable.
		# The factor table corresponds to the weight distribution of a variable
		# for all added unary factor functions. If there's no unary function for		# a variable K, there will be no entry for K in unaryFactors.
		# E.g. if B \in ['a', 'b'] is a variable, and we added two
		# unary factor functions f1, f2 for B,
		# then unaryFactors[B]['a'] == f1('a') * f2('a')
		self.unaryFactors = {}

		# Each entry is a dictionary keyed by the name of the other variable
		# involved. The value is a binary factor table, where each table
		# stores the factor value for all possible combinations of
		# the domains of the two variables for all added binary factor
		# functions. The table is represented as a dictionary of dictionary.
		#
		# As an example, if we only have two variables
		# A \in ['b', 'c'],  B \in ['a', 'b']
		# and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
		# then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
		# binaryFactors[A][A] should return a key error since a variable
		# shouldn't have a binary factor table with itself.

		self.binaryFactors = {}

	def add_variable(self, var, domain):
		"""
		Add a new variable to the CSP.
		"""
		if var in self.variables:
			raise Exception("Variable name already exists: %s" % str(var))

		self.numVars += 1
		self.variables.append(var)
		self.values[var] = domain
		self.unaryFactors[var] = None
		self.binaryFactors[var] = dict()

	def get_neighbor_vars(self, var):
		return self.binaryFactors[var].keys()

	def add_unary_factor(self, var, factorFunc):
		"""
		Add a unary factor function for a variable. Its factor
		value across the domain will be *merged* with any previously added
		unary factor functions through elementwise multiplication.

		How to get unary factor value given a variable |var| and
		value |val|?
		=> csp.unaryFactors[var][val]
		"""
		factor = {val:float(factorFunc(val)) for val in self.values[var]}
		if self.unaryFactors[var] is not None:
			assert len(self.unaryFactors[var]) == len(factor)
			self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
				factor[val] for val in factor}
		else:
			self.unaryFactors[var] = factor

	def add_binary_factor(self, var1, var2, factor_func):
		"""
		Takes two variable names and a binary factor function
		|factorFunc|, add to binaryFactors. If the two variables already
		had binaryFactors added earlier, they will be *merged* through element
		wise multiplication.
		"""
		# never shall a binary factor be added over a single variable
		try:
			assert var1 != var2
		except:
			print 'You can\'t add a binary Factor on the same variable.'

		self.update_binary_factor_table(var1, var2,
			{val1: {val2: float(factor_func(val1, val2)) \
				for val2 in self.values[var2]} for val1 in self.values[var1]})
		self.update_binary_factor_table(var2, var1, \
			{val2: {val1: float(factor_func(val1, val2)) \
				for val1 in self.values[var1]} for val2 in self.values[var2]})

	def update_binary_factor_table(self, var1, var2, table):
		"""
		If used, element-wise multiplications will be performed to merge
		them together.
		"""
		if var2 not in self.binaryFactors[var1]:
			self.binaryFactors[var1][var2] = table
		else:
			currentTable = self.binaryFactors[var1][var2]
			for i in table:
				for j in table[i]:
					assert i in currentTable and j in currentTable[i]
					currentTable[i][j] *= table[i][j]

class CrosswordCSP(CSP):

	def __init__(self, cw):
		CSP.__init__(self)
		self.cw = cw

def createCrosswordCSP(cw):

	csp = CrosswordCSP(cw)

	# Add Letter Variables
	for key in cw.letters.keys():
		csp.add_variable(str(key), cw.letters[key].domain)

	# Add Word Variables & Constraints
	# Word and Arity constraints satisfied by domain construction
	for i,key1 in enumerate(cw.words.keys()):

		word = cw.words[key1]
		csp.add_variable(str(key1), word.domain)

		# Intersection Constraint
		for idx in range(word.length):
			letterKey = (key1[0]+idx, key1[1])
			if key1[2] == 1:
				letterKey = (key1[0], key1[1]+idx)
			if letterKey not in cw.blanks:
				csp.add_binary_factor(str(key1), str(letterKey), lambda x,y: x[idx] == y)

		for j, key2 in enumerate(cw.words.keys()):
			if i < j:
				# Repetition Constraint
				# csp.add_binary_factor(str(key1), str(key2), lambda x,y: x != y)
				pass
	return csp

	# Intersection Constraint Functions
	'''def intersectionFactorFunc(wordKey, letterKey):
		acrossWordKey = key1 if key1[2] == 1 else key2
		downWordKey = key1 if key1[2] == 0 else key2
		acrossWord = self.cw.words[acrossWordKey]
		downWord = self.cw.words[downWordKey]
		if

	# Returns true if two words intersect
	def wordsIntersect(key1, key2)
		if key1[2] == key2[2]:	return False
		acrossWordKey = key1 if key1[2] == 1 else key2
		downWordKey = key1 if key1[2] == 0 else key2
		acrossWord = self.cw.words[acrossWordKey]
		downWord = self.cw.words[downWordKey]
		if downWord.startLoc[1] >= acrossWordKey[1] and downWord.startLoc[1] < acrossWordKey[1]+acrossWord.length:
			return True
		return False
	'''
