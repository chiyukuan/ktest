
from kd.util.package import Package

class All(Package):
    def __init__(self): super(All, self).__init__(self)

__all__ = All().attrs[All.__module__][1]

