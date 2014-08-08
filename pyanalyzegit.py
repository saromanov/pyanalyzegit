import pbs

#https://github.com/kachayev/fn.py
from fn import _, F, underscore
from abc import ABCMeta, abstractmethod
import fn

import numpy
import math

import show
from utils import clearDates, countCommitsByDate, Snippets

#Celery?

#https://pypi.python.org/pypi/pbs

AUTHOR = 'Author'
DATE = 'Date'
COMMIT = 'commit'

class ExtendGit:
	def __init__(self):
		self.git = pbs.git

	def branch(self):
		''' get a current branch'''
		return self.git("branch").split()[1]

	def commit(self, value):
		self.git("commit" + value)

	#Use infromation from basic git log command
	def log(self, *args, **kwargs):
		#Append git log patch
		opt = kwargs.get('opt', '--numstat')
		af = AnalyzeFactory()
		if opt.find('--') == -1:
			opt = '--' + opt
		if opt == '--numstat':
			af.set('gla', GitLogAnalyzer)
		if opt == '--binary':
			af.set('bin', PySourceAnalyzer)
		data = self.git("log", (opt)).split('\n')
		return af.get(data)
		#return GitLogAnalyzer(data)

class AbstractAnalyze(metaclass=ABCMeta):

	@abstractmethod
	def analyze(self, func):
		'''
			User analyze method with data
		'''
		pass


class AnalyzeFactory:
	def __init__(self, *args, **kwargs):
		self._cleardata = {}

	def set(self, name, classdata):
		self._cleardata[name] = classdata

	def get(self, name, data):
		if name in self._cleardata:
			return self._cleardata[name](data)

	def get(self, data):
		'''
			Get all from store
		'''
		for func in self._cleardata.keys():
			return self._cleardata[func](data)

class ChangedFiles:
	def __init__(self, count, app, rems):
		self.count = count
		self.app = app
		self.rems = rems

#http://git-scm.com/docs/git-log
#dirstat = pbs.git("log", ("--dirstat"))
#Show source --ignore-all-space 
#binary = pbs.git("log", ("--binary"))

#This is inner class, not in API
class GitLogAnalyzer(AbstractAnalyze):
	def __init__(self, data):
		'''
			Parse results from pbs call
			For example: GitLogAnalyzer(self.git("log", ("--numstat")).split('\n'))
		'''
		self._result = self._parseResult(data)
		self.s = show.Show()

	def _parseResult(self, data):
		''' 
			Get some ordered data from pbs
		'''
		result = []
		commits = {}
		cleardata = self._cleardata
		for d in data:
			cands = d.split('\n')
			for cand in cands:
				if cand.startswith(AUTHOR) and AUTHOR not in commits:
					commits[AUTHOR] = cleardata(cand, AUTHOR)
				elif cand.startswith(DATE) and DATE not in commits:
					commits[DATE] = cleardata(cand, DATE)
				elif cand.startswith(COMMIT):
					if len(commits) > 0:
						result.append(commits)
					commits = {}
					commits['Commit'] = cleardata(cand, COMMIT)
				elif len(cand) > 0:
					if cand.startswith(' '):
						commits['CommitTitle'] = cand.replace('  ','')
					else:
						if 'Files' not in commits:
							commits['Files'] = []
						commits['Files'].append(self._prepareFiles(cand))
		return result

	def _cleardata(self, data, param):
		return data.split(param)[1:][0]

	def _prepareFiles(self, value):
		'''
		  Convert append and removed lines in int type
		  And output with filename
		'''
		#return list(map(_ if not _.isdigit() else int(_), value.split()))
		return list(map(lambda x: x if not x.isdigit() else int(x), value.split()))

	def analyze(self, func):
		'''
			User function for filter target results
		'''
		return list(filter(func, self.result))

	def _parseIntData(self, add, rem):
		try:
			add = int(add)
			rem = int(rem)
			return add, rem
		except Exception:
			return 0,0

	def mostChangingFiles(self, limit=1):
		'''
			Get most modified files in project
		'''
		files = {}
		for commit in self._result:
			f = commit['Files']
			for subfile in f:
				add, rem = self._parseIntData(subfile[0], subfile[1])
				cfile = subfile[2]
				if cfile not in files:
					files[cfile] = ChangedFiles(1, add, rem)
				else:
					cf = files[cfile]
					files[cfile] = ChangedFiles(cf.count+1, cf.app+add, cf.rems+rem)
		filessorted = sorted(files.items(), key=_[1].count, reverse=True)
		result = map(lambda data: (data[0], {'count':data[1].count,\
			'append':data[1].app, 'remove': data[1].rems}), filessorted)
		return list(result)


	def getCommits(self):
		return self._result

	def _collectData(self, func=None):
		files = {}
		for data in self._result:
			##TODO: Need to optimize
			for f in data['Files']:

				if f[0] < 1000:
					name = self._getFileName(f[2])
					if name not in files:
						files[name] = {'a':f[0], 'r':f[1]}
					else:
						value = files[name]
						files[name] = {'a': value['a'] + f[0], 'r': value['r'] + f[1]}
		return files

	def _getFileName(self, path):
		nums = path.split('/')
		return nums[len(nums)-1]


	def wordsAddRemInfo(self):
		words = self._collectWords(self._result)
		result = []
		for s in self._result:
			for f in s['Files']:
				add = f[0]
				rem = f[1]
				result.append((f[2], (add-rem)/(add+rem)))
		return result

	def getFunctionNames(self, lang):
		if lang != 'python':
			raise Exception("This language is not supported")
		return PySourceAnalyzer()

	def _collectWords(self, data):
		words = {}
		for d in data:
			for w in d['CommitTitle'].split():
				if not(w in words):
					words[w] = 0
				else:
					words[w] += 1
		return words

	def showChangingFiles(self, func=None):
		'''
		  Plot data about append and removed lines
		'''
		data = self._collectData(func)
		keys = data.keys()
		a = list(map(data[_]['a'], keys))
		r = list(map(data[_]['r'], keys))
		self.s.barplot_commits(a, r, list(data.keys()))

	def showCommitsByDate(self, func=None):
		'''
			Plot data about commits
		'''
		from time import mktime, time, strptime
		import datetime
		dates = list(map(lambda x: x['Date'], self.getCommits()))
		cd = clearDates(dates)

		result = map(lambda x: 
			datetime.datetime.fromtimestamp(mktime(strptime(x, '%a %b %d %H:%M:%S %Y '))),cd)
		d,c = countCommitsByDate(result)
		self.s.showByDate(d,c)


class PySourceAnalyzer:
	'''
		Analyze append and removed from source
	'''
	def __init__(self, data):
		self._result = self._parseResult(data)

	def _parseResult(self, data):
		return [value.split() for value in data]

	def getFunctions(self, objfunc=None):
		'''
			objfunc - target function
		'''
		FUNCSTART = 'def'
		PLUS = '+'
		REM = '-'
		if objfunc == None:
			''' Get default function '''
			def getFunc(line):
				#func = _, line[2].split('(')[0]
				if len(line) > 1:
					if line[0] == PLUS:
						if line[1] == FUNCSTART:
							return [PLUS, line[2].split('(')[0]]
					if line[1] == REM:
						if line[1] == FUNCSTART:
							return [REM, line[2].split('(')[0]]
			objfunc = getFunc

		for line in self._result:
			result = objfunc(line)
			if result != None:
				yield result

	def getCountLinesFuncs(self):
		#Only functions with return 
		def getFunc(line):
			if 'def' in line:
				return 0
			if 'return' in line:
				return 1
		objfunc = getFunc
		count = 0
		for line in self._result:
			print(line)
			result = objfunc(line)
			if result == 0:
				count = 0
			if result == 1:
				yield count
			else:
				count += 1

	def analyze(self, func):
		return list(filter(func, self._result))


class JavaScriptSourceAnalyzer:
	''' Working with source in JS '''
	def __init__(self, data):
		self._result = self._parseResult(data)

	def _parseResult(self, data):
		pass