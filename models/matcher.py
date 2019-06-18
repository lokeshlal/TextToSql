import copy

class Matcher(object):
    def __init__(self):
        self.matcher = []
        return super().__init__()
    
    def add(self, key, value):
        self.matcher.append((key, value))
    
    def find(self, phrase):
        matches = []
        for match in self.matcher:
            if " " + str(match[1]) + " " in phrase \
                or phrase.startswith(str(match[1]) + " ") \
                or phrase.endswith(" " + str(match[1])):
                matches.append(copy.copy(match))
        return matches
    
