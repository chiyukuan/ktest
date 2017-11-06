#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

def enum(*nameEntries):
    # assert names, "Empty enums are not supported" # <- Don't like empty
    # enums?
    if isinstance(nameEntries[0], basestring):
        names  = nameEntries
        values = range(len(nameEntries))
    else:
        names  = [ pair[0] for pair in nameEntries ]
        values = [ pair[1] for pair in nameEntries ]

    class EnumClass(object):
        __slots__ = names

        def getEnum(self, key):
            if isinstance(key, basestring):
                for ii, name in enumerate(names):
                    if name == key:
                        return constants[ ii ]
            else:
                for ii, value in enumerate(values):
                    if value == key:
                        return constants[ ii ]
            return None

        def __iter__(self):
            return iter(constants)

        def __len__(self):
            return len(constants)

        def __getitem__(self, i):
            return constants[i]

        def __repr__(self):
            return 'Enum' + str(names)

        def __str__(self):
            return 'enum ' + str(constants)

    class EnumValue(object):
        __slots__ = ('__value', '__index')

        def __init__(self, value, index):
            self.__value = value
            self.__index = index
        Value = property(lambda self: self.__value)
        EnumType = property(lambda self: EnumType)

        def getVal(self):
            return self.__value

        def __hash__(self):
            return hash(self.__value)

        def __cmp__(self, other):
            # C fans might want to remove the following assertion
            # to make all enums comparable by ordinal value {;))
            assert self.EnumType is other.EnumType, "Only values from the same enum are comparable"
            return cmp(self.__value, other.__value)

        def __invert__(self):
            return constants[maximum - self.__index]

        def __nonzero__(self):
            return bool(self.__value)

        def __repr__(self):
            return names[self.__index]

        __str__ = __repr__

    maximum = len(names) - 1
    constants = [None] * len(names)
    for ii, each in enumerate(names):
        val = EnumValue(values[ii], ii)
        setattr(EnumClass, each, val)
        constants[ii] = val

    constants = tuple(constants)
    EnumType = EnumClass()
    return EnumType


if __name__ == '__main__':
    print '\n*** Enum Demo ***'
    print '--- Days of week ---'
    #Days = enum('Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su')
    Days = enum(['Mo', 12], ['Tu', 15], ['We', 14], ['Th',11], ['Fr',9], ['Sa',7], ['Su', 2])
    print Days
    print Days.Mo.getVal()
    print Days.Fr
    print Days.Mo < Days.Fr
    print list(Days)
    day15 = Days.getEnum(15)
    print "day15 %s %d" % (day15, day15.getVal())
    daySu = Days.getEnum('Su')
    print "daySu %s %d" % (daySu, daySu.getVal())
    for each in Days:
        print 'Day:%s, val:%d' % (each, each.getVal())
    print '--- Yes/No ---'
    Confirmation = enum('No', 'Yes')
    answer = Confirmation.No
    print 'Your answer is not', ~answer

    C1 = enum('No', 'Yes')
    C2 = enum('Yes', 'No')

    assert C1.No != C2.No  # Kind of okay I guess
    assert C1.No == C2.Yes  # Yikes!
