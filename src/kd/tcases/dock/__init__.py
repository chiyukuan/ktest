
''' ------------------------|  Python SOURCE FILE  |------------------------
'''

from kd.tfwk.test_folder import TestFolder

class All(TestFolder):
    def __init__(self): super(All, self).__init__(self)


__all__ =  All().attrs[All.__module__][1]
