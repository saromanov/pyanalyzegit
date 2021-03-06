import numpy as np
import matplotlib.pyplot as plt
import datetime


class Show:

    def __init__(self):
        pass

    def barplot_commits(self, valuesa, valuesr, groups):
        '''
                Show append and removed lines in commit for each file
                Based: http://matplotlib.org/examples/pylab_examples/bar_stacked.html
        '''
        '''fig, ax = plt.subplots()
		index = np.arange(len(groups))
		bar_width = 0.50
		opacity = 0.4
		error_config = {'ecolor': '0.3'}
		rects1 = plt.bar(index, valuesa, bar_width,
                 alpha=opacity,
                 color='b',
                 error_kw=error_config,
                 label='Append')
		rects2 = plt.bar(index + bar_width, valuesr, bar_width,
                 alpha=opacity,
                 color='r',
                 error_kw=error_config,
                 label='Remove')
		plt.xlabel('File', fontsize=8)
		plt.ylabel('Scores')
		plt.title('Scores for append and removed lines')
		plt.xticks(index + bar_width, groups)
		plt.legend()
		plt.tight_layout()
		plt.show()'''
        ind = np.arange(len(groups))
        width = 0.35       # the width of the bars: can also be len(x) sequence

        p1 = plt.bar(ind, valuesa,   width, color='r')
        p2 = plt.bar(ind, valuesr, width, color='y',
                     bottom=valuesa)

        plt.ylabel('Scores')
        plt.title('Show append and removed lines')
        plt.xticks(ind + width / 2., groups)
        plt.yticks(np.arange(0, 500, 50))
        plt.legend((p1[0], p2[0]), ('Append', 'Remove'))

        plt.show()

    def showByDate(self, dts, commits):
        '''
                Show information about date of commits,
                for example count of commits by day, etc
        '''
        from matplotlib.dates import YearLocator, MonthLocator, DateFormatter, DayLocator
        import datetime

        result = list(
            map(lambda x: datetime.datetime(year=x[2], month=x[1], day=x[0]), dts))
        value = list(zip(result, commits))
        sorteddates = sorted(zip(result, commits), key=lambda x: x[0])
        plt.xticks()
        plt.subplots_adjust(bottom=0.2)
        plt.plot_date(*zip(*sorteddates), linestyle='dashed', linewidth=2.0)
        plt.gcf().autofmt_xdate()
        plt.show()
