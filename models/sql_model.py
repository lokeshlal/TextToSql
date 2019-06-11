class SQLGenerator(object):
    def __init__(self, entities, columns, db_model):
        self.columns = columns
        self.entities = entities
        self.db_model = db_model
        self.entity_column_mapping = []
        self.joins = []
        self.entities_parsed = []
    
    def find_relationships(self):
        i = 0
        j = 0

        while i < len(self.entity_column_mapping):
            j = i + 1
            
            while j < len(self.entity_column_mapping):
                print("building")

                j = j + 1
            
            i = i + 1
                


    def get_sql(self):
        for column in self.columns:
            # reset the entities_parsed array for new column
            self.entities_parsed = []
            column_parent_entity_found, model_name, columnName = self.find_entity(column)
            if column_parent_entity_found == True:
                if len([ecm for ecm in self.entity_column_mapping if ecm[0] == model_name]) == 1:
                    ecm = next(ecm for ecm in self.entity_column_mapping if ecm[0] == model_name)
                    ecm[1].append(columnName)
                else:
                    self.entity_column_mapping.append((model_name, [columnName]))
            else:
                print("Column " + column.name + " not found.. ignoring column")
        # build the sql
        self.find_relationships()


    def find_column(self, column, entityName):
        column_parent_entity_found = False
        # get the db model for entity
        db_model_entity = next(model_entity for model_entity in self.db_model.entities if model_entity.name == entityName.lower())

        # add entity into parsed collection
        self.entities_parsed.append(entityName)

        # check if the column exists in the db_model
        if column.name.lower() in [db_model_column.name for db_model_column in db_model_entity.columns]:
            # column parent found, break the loop
            column_parent_entity_found = True
            return (column_parent_entity_found, db_model_entity.name, column)

        # if column does not exists in db_model_entity
        # then look for the related entities
        if column_parent_entity_found == False:
            # look for related entities
            for model_entity in [model_entity for model_entities in self.db_model.entity_graph if model_entities[0].lower() == entityName.lower() for model_entity in model_entities[1]]:

                # only process, if not processed before
                if len([ep for ep in self.entities_parsed if ep.lower() == model_entity]) == 0:
                    column_parent_entity_found, model_name, columnName = self.find_column(column, model_entity)
                    # column found, return entity with column
                    if column_parent_entity_found == True:
                        return (column_parent_entity_found, model_name, columnName)

        # column not found
        return (column_parent_entity_found, None, None)

    def find_entity(self, column):
        column_parent_entity_found = False
        for entity in self.entities:
            column_parent_entity_found, model_name, columnName =  self.find_column(column, entity.name)
            # column found, return entity with column
            if column_parent_entity_found == True:
                return (column_parent_entity_found, model_name, columnName)

        return (column_parent_entity_found, None, None)
