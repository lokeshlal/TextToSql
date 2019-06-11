class Entities(object):
    def __init__(self, name=None, isAverage=None, isMax=None, isMin=None, isCount=None, columns=None, defaultColumn=None, primaryKey=None):
        self.name = name
        self.isAverage = isAverage
        self.isMax = isMax
        self.isMin = isMin
        self.isCount = isCount
        self.columns = []
        self.defaultColumn = defaultColumn
        self.primaryKey = primaryKey