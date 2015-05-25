'''
	Output for console view
'''

import builtins


def tableOutput(data):
    if data == None or len(data) == 0:
        # TODO: Add this exception to base
        raise "Data contain zero elements"
    print('ELEMENTS: ')
    for value in data:
        print('  '.join(map(lambda x: str(x), value)))
    print('End of elements', ...)


def infoOutput(data):
    '''
            Outout for some statistical information
    '''
    pass
