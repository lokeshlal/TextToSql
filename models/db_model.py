from models.entities import Entities
from models.columns import Columns
from models.relationships import Relationship
from models.synonyms import Synonyms
class DBModel(object):
    def __init__(self):
        self.entities = []
        self.columns = []
        self.relationships = []
        self.synonyms_col = []
        self.synonyms_tab = []
        self.entity_graph = []
        self.load_db_model()

    def load_db_model(self):
        # load schema from database
        entity_student = Entities("student", "name", "id")
        entity_student.columns.append(Columns("id", "int"))
        entity_student.columns.append(Columns("name", "string"))
        entity_student.columns.append(Columns("age", "int"))
        entity_student.columns.append(Columns("class", "int"))

        self.entities.append(entity_student)

        entity_subject = Entities("subject", "name", "id")
        entity_subject.columns.append(Columns("id", "int"))
        entity_subject.columns.append(Columns("subject", "string"))
        entity_subject.columns.append(Columns("class", "int"))

        self.entities.append(entity_subject)

        entity_student_mark = Entities("student_mark", "id", "id")
        entity_student_mark.columns.append(Columns("id", "int"))
        entity_student_mark.columns.append(Columns("student_id", "int"))
        entity_student_mark.columns.append(Columns("subject_id", "int"))
        entity_student_mark.columns.append(Columns("mark", "int"))
        entity_student_mark.columns.append(Columns("year", "int"))

        self.entities.append(entity_student_mark)

        self.relationships.append(Relationship("student", "student_mark", "id", "student_id"))

        self.relationships.append(Relationship("subject", "student_mark", "id", "subject_id"))

        self.entity_graph.append(("student", ["student_mark"]))
        self.entity_graph.append(("student_mark", ["student", "subject"]))
        self.entity_graph.append(("subject", ["student_mark"]))
        
        # load synonyms from declarative file
        # column sysnonyms
        self.synonyms_col.append(Synonyms("class", "standard"))
        # table sysnonyms
        self.synonyms_tab.append(Synonyms("student", "children"))

        # make a single array
        self.columns = [column for entity in self.entities for column in entity.columns]
        

    # build the matcher based upon the original value and domain synonyms defined
    def get_matcher(self, matcher, nlp):
        for entity in self.entities:
            matcher.add(entity.name.upper() + "_TABLE", None, nlp(entity.name.lower()))    
            for column in entity.columns:
                matcher.add(column.name.upper() + "_COLUMN", None, nlp(column.name.lower()))        

        # add table synonyms to matcher
        for synonym in self.synonyms_tab:
            for entity in self.entities:
                if synonym.column == entity.name:
                    matcher.add(entity.name.upper() + "_TABLE", None, nlp(synonym.synonym.lower()))        

        # add column synonyms to matcher
        for synonym in self.synonyms_col:
            for column in self.columns:
                if synonym.column == column.name:
                    matcher.add(column.name.upper() + "_COLUMN", None, nlp(synonym.synonym.lower()))        
                    

        return matcher

        