from collections import Counter

import pbs
# https://github.com/kachayev/fn.py
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

# Celery?

# https://pypi.python.org/pypi/pbs

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

    # Use infromation from basic git log command
    def log(self, *args, **kwargs):
        # Append git log patch
        opt = kwargs.get('opt', '--numstat')
        af = AnalyzeFactory()
        if opt.find('--') == -1:
            opt = '--' + opt
        if opt == '--numstat':
            af.set('gla', GitLogAnalyzer)
        if opt == '--binary':
            lang = kwargs.get('lang')
            if lang == 'py':
                af.set('bin', PySourceAnalyzer)
            if lang == 'js':
                af.set('bin', JavaScriptSourceAnalyzer)
        data = self.git("log", (opt)).split('\n')
        return af.get(data)

    def getArchiveFromRepo(self, form, path):
        self.git(
            "archive", "master", "--format={0}".format(form), "--output={0}".format(path))


class GitLog:

    def __init__(self, *args, **kwargs):
        self.git = pbs.git

    def _getGitData(self, keys):
        return self.git("log", "--pretty=format:'%{0}'".format(keys)).split('\n')

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
                        commits['CommitTitle'] = cand.replace('  ', '')
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
        # return list(map(_ if not _.isdigit() else int(_), value.split()))
        return list(map(lambda x: x if not x.isdigit() else int(x), value.split()))

    def result(self):
        return self._parseResult(self._data)


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
    parser.add_argument(
        '--authors', nargs='?', help='Show all authors in this repo')
    parser.add_argument(
        '--show-commits', nargs='?', help='Plot commits by date')
    parser.add_argument('--plot-files', nargs='?', help='Plot changing files')
    parser.add_argument('--often-funcs', nargs='?',
                        help='Get list of most often calls functions in code')
    parser.add_argument('--gclone', nargs='?', help='Clone repo from github')
    parser.add_argument(
        '--gclonei', nargs='?', help='Clone repo from git and install')
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
        # Now only for python
        from consoleout import tableOutput
        binary = git.log(opt='binary', lang='py')
        tableOutput(binary.mostOftenFunctions())


# Check example with algebird
if __name__ == '__main__':
    parse()
    #git = ExtendGit()
    #binary = git.log(opt='binary', lang='py')
    # print(binary.mostOftenFunctions())
    # print(list(, ...)
    '''for comm in  git.log().getCommits():
		print(comm['CommitTitle'])'''
