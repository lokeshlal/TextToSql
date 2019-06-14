class Columns(object):
    def __init__(self, name=None, type_=None, isAverage=None, isMax=None, isMin=None, isCount=None, value_=None, condition=None, isSum=None):
        self.name = name
        self.type_ = type_
        self.isAverage = isAverage
        self.isMax = isMax
        self.isMin = isMin
        self.isCount = isCount
        self.value_ = value_
        self.condition = condition
        self.isSum = isSum