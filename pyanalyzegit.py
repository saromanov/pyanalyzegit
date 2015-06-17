from collections import Counter
from abc import ABCMeta, abstractmethod
from sourceanalysis.pysourceanalyzer import PySourceAnalyzer
from sourceanalysis.javascriptsourceanalyzer import JavaScriptSourceAnalyzer
from gitloganalyzer import GitLogAnalyzer
import numpy
import math
import argparse
import git

import show
from utils import clearDates, countCommitsByDate, Snippets

# Celery?

# https://pypi.python.org/pypi/pbs

AUTHOR = 'Author'
DATE = 'Date'
COMMIT = 'commit'


class GitAnalyzer:
    def __init__(self):
        self.repos = []

    def getCommitsInfo(self, repopath):
        repo = git.Repo(repopath)
        return list(repo.iter_commits())


class ExtendGit:

    def __init__(self):
        #self.git = pbs.git
        self.gitdata = GitAnalyzer()

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

    def commitsInfo(self, repopath):
        return self.gitdata.getCommitsInfo(repopath)

    def showCommitsInfo(self, repopath):
        commits = self.commitsInfo(repopath)
        for commit in commits:
            print(dir(commit))
            print(commit.committed_date, commit.committer, commit.message)

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



def getLogData(git):
    numstat = git.log(opt='--numstat').wordsAddRemInfo()
    return numstat


def getZipData(git):
    git.getArchiveFromRepo('zip', 'test.zip')
    print("Complete. Archive from repo was zipped")


def showAuthorsData(repo):
    ex = ExtendGit()
    commits = ex.commitsInfo(repo)
    an = GitLogAnalyzer(commits)
    result = an.getAuthorsStat()
    print("Contributor statistics:")
    print("Contributor  Number of commits\n")
    for author, commits in result.items():
        print('{0}  {1}'.format(author, commits))

def showPopularWords(repo):
    assert repo != None
    ex = ExtendGit()
    commits = ex.commitsInfo(repo)
    an = GitLogAnalyzer(commits)
    result = an.getPopularWords()
    print("popular words from commits")
    for word in result:
        print(word)

def showAll(repo):
    """
    Show all of stat methods
    """
    print("Repo: {0}".format(repo))
    showAuthorsData(repo)
    showPopularWords(repo)



def plotCommitsByDate(git):
    git.log().showCommitsByDate()


def cloneFromGithub(git, repo):
    git.githubClone(repo)


def parse():
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument('--repo', nargs='?', help='Repository for analysis')
    parser.add_argument('--log', action='store_true', help='Show log data')
    parser.add_argument('--popular-words', action='store_true', help='Get popular words from commits')
    parser.add_argument('--authors-stat', action='store_true', help='Show author statistics by format author:number of commits')
    parser.add_argument('--all', action='store_true', help='Show all of stat methods')
    args = parser.parse_args()
    git = ExtendGit()
    repo = args.repo
    if repo == None:
        print("Parameter repo is empty")
        return
    if args.all != None:
        showAll(repo)
        return
    if args.authors_stat != None:
        showAuthorsData(repo)
    if args.popular_words != None:
        showPopularWords(repo)
    else:
        parser.print_help()
    '''if args.log != None:
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
        tableOutput(binary.mostOftenFunctions())'''


# Check example with algebird
if __name__ == '__main__':
    parse()
    #git = ExtendGit()
    #binary = git.log(opt='binary', lang='py')
    # print(binary.mostOftenFunctions())
    # print(list(, ...)
    '''for comm in  git.log().getCommits():
		print(comm['CommitTitle'])'''
