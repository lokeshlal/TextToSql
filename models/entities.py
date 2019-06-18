class Entities(object):
    def __init__(self, name=None, defaultColumn=None, primaryKey=None, isAverage=None, isMax=None, isMin=None, isCount=None, columns=None, condition=None, value_=None, isSum=None):
        self.name = name
        self.isAverage = isAverage
        self.isMax = isMax
        self.isMin = isMin
        self.isCount = isCount
        self.columns = []
        self.value_ = value_
        self.condition = condition
        self.defaultColumn = defaultColumn
        self.primaryKey = primaryKey
        self.isSum = isSum
