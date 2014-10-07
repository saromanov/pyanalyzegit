from collections import Counter

import pbs
#https://github.com/kachayev/fn.py
from fn import _, F, underscore
from abc import ABCMeta, abstractmethod
from sourceanalysis.pysourceanalyzer import PySourceAnalyzer
from sourceanalysis.javascriptsourceanalyzer import JavaScriptSourceAnalyzer
import fn
import numpy
import math
import argparse

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

	def githubClone(self, repo):
		'''
			Clone from github with just a repo name.
			Looks like a alias
		'''
		self.git("clone", "https://github.com/{0}".format(repo))

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
			lang = kwargs.get('lang')
			if lang =='py':
				af.set('bin', PySourceAnalyzer)
			if lang == 'js':
				af.set('bin', JavaScriptSourceAnalyzer)
		data = self.git("log", (opt)).split('\n')
		return af.get(data)

	def getArchiveFromRepo(self, form, path):
		self.git("archive","master","--format={0}".format(form), "--output={0}".format(path))

class GitLog:
	def __init__(self, *args,**kwargs):
		self.git = pbs.git

	def _getGitData(self, keys):
		return self.git("log" ,"--pretty=format:'%{0}'".format(keys)).split('\n')

	def getAuthors(self):
		data = self._getGitData('an')
		return Counter(data).most_common()

	def getComments(self):
		return self._getGitData('s')

	def countWords(self):
		return Counter(''.join(self.getComments()).split()).most_common()

	def showChangingFiles(self):
		pass

class GitLogParsing:
	'''
		Parsing output of git log
		Maybe, re-implement it with some keys
	'''
	def __init__(self, data):
		self._data = data

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

	def result(self):
		return self._parseResult(self._data)

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
		self.glog = GitLog()
		self._result = GitLogParsing(data).result()
		self.s = show.Show()

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
		'''
			Most change in files
		'''
		result = []
		for s in self._result:
			for f in s['Files']:
				add = f[0]
				rem = f[1]
				zdata = (add + rem)
				if zdata != 0:
					result.append((f[2], (add-rem)/(add+rem)))
		return result



	def getFunctionNames(self, lang):
		if lang == 'python':
			return PySourceAnalyzer(self._result)
		if lang == 'js':
			return JavaScriptSourceAnalyzer(self._result)
		raise Exception("This language is not supported")

	def getAuthors(self):
		'''
			Return tuple (author, number of commits)
		'''
		return self.glog.getAuthors()

	def checkBug(self):
		'''
			Get author of bug
		'''
		return None

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

	def commentsFromCommit(self):
		return self.glog.getComments()


def getLogData(git):
	numstat = git.log(opt='--numstat').wordsAddRemInfo()
	return numstat

def getZipData(git):
	git.getArchiveFromRepo('zip', 'test.zip')
	print("Complete. Archive from repo was zipped")

def getAuthorsData(git):
	return git.log().getAuthors()

def plotCommitsByDate(git):
	git.log().showCommitsByDate()

def cloneFromGithub(git, repo):
	git.githubClone(repo)

def parse():
	parser = argparse.ArgumentParser(description="Parsing arguments")
	parser.add_argument('--log', nargs='?', help='Show log data')
	parser.add_argument('--zip', nargs='?', help='zipp current repo')
	parser.add_argument('--authors', nargs='?', help='Show all authors in this repo')
	parser.add_argument('--show-commits', nargs='?', help='Plot commits by date')
	parser.add_argument('--plot-files', nargs='?', help='Plot changing files')
	parser.add_argument('--often-funcs', nargs='?', help='Get list of most often calls functions in code')
	parser.add_argument('--gclone', nargs='?', help='Clone repo from github')
	parser.add_argument('--gclonei', nargs='?', help='Clone repo from git and install')
	parser.print_help()
	args = parser.parse_args()
	git = ExtendGit()
	if args.log != None:
		from consoleout import tableOutput
		tableOutput(getLogData(git))
	if args.zip != None:
		getZipData(git)
	if args.authors != None:
		from consoleout import tableOutput
		tableOutput(getAuthorsData(git))
	if args.show_commits != None:
		plotCommitsByDate(git)
	if args.gclone != None:
		cloneFromGithub(git, args.gclone)
	if args.often_funcs != None:
		#Now only for python
		from consoleout import tableOutput
		binary = git.log(opt='binary', lang='py')
		tableOutput(binary.mostOftenFunctions())

if __name__ == '__main__':
	parse()
	#git = ExtendGit()
	#binary = git.log(opt='binary', lang='py')
	#print(binary.mostOftenFunctions())
	#print(list(, ...)
	'''for comm in  git.log().getCommits():
		print(comm['CommitTitle'])'''
