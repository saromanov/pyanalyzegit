from sourceanalysis.mainsourceanalyzer import MainSourceAnalyzer

class PySourceAnalyzer:
	'''
		Analyze append and removed from source
	'''
	def __init__(self, data):
		self._dataobj = MainSourceAnalyzer(data)

	def getFunctions(self, objfunc=None):
		return self._dataobj.getFunctions('def')

	def getCountLinesFuncs(self):
		return self._dataobj.getCountLinesFuncs('def', 'return')

	def analyze(self, func):
		return self._dataobj.analyze(func)
