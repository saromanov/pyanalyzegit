import numpy as np
import matplotlib.pyplot as plt



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
		plt.xticks(ind+width/2., groups )
		plt.yticks(np.arange(0,500,50))
		plt.legend( (p1[0], p2[0]), ('Append', 'Remove') )

		plt.show()


	def showByDate(self, commits):
		'''
			Show information about date of commits,
			for example count of commits by day, etc
		'''
		from matplotlib.finance import quotes_historical_yahoo
		from matplotlib.dates import YearLocator, MonthLocator, DateFormatter, DayLocator
		import datetime
		date2 = datetime.date( 2014, 4, 12 )
		date3 = datetime.date( 2014, 4, 11 )
		date4 = datetime.date( 2014, 4, 13 )
		date5 = datetime.date( 2014, 4, 14 )
		date6 = datetime.date( 2014, 4, 15 )
		date7 = datetime.date( 2014, 4, 16 )
		date8 = datetime.date( 2014, 4, 17 )

		years    = YearLocator()   # every year
		months   = MonthLocator()  # every month
		days = DayLocator()
		yearsFmt = DateFormatter('%D')

		fig, ax = plt.subplots()
		ax.plot_date([date2, date3, date4, date5, date6, date7, date8], [4,1,2,1,3,5,2], '-')

		# format the ticks
		ax.xaxis.set_major_locator(days)
		ax.xaxis.set_major_formatter(yearsFmt)
		ax.xaxis.set_minor_locator(days)
		ax.autoscale_view()

		# format the coords message box
		ax.grid(True)

		fig.autofmt_xdate()
		plt.show()

