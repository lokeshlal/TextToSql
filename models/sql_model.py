class SQLGenerator(object):
    def __init__(self, entities, columns, db_model):
        self.columns = columns
        self.entities = entities
        self.db_model = db_model
        self.entity_column_mapping = []
        self.joins = []
        self.conditions = []
        self.select = []
        self.query = ""
        self.entities_parsed = []

    def sortSecond(self, join_comb): 
        return join_comb[0] 

    def build_query(self):

        from_clause = ""
        if len(self.entity_column_mapping) == 1:
            from_clause = self.entity_column_mapping[0][0]
        elif len(self.entity_column_mapping) > 1:
            from_clause = ""
            join_index = 0
            entity_included_in_join = []
            for join in self.joins:
                if join_index == 0:
                    from_clause = from_clause + join[0] + " JOIN " + join[1] + " ON " + join[0] + "." + join[2] + "=" + join[1] + "." + join[3]
                    entity_included_in_join.append(join[0])
                    entity_included_in_join.append(join[1])
                else:
                    if join[0] in entity_included_in_join:
                        from_clause = from_clause + " " + " JOIN " + join[1] + " ON " + join[0] + "." + join[2] + " = " + join[1] + "." + join[3]
                    else:
                        from_clause = from_clause + " JOIN " + join[0] + " ON " + join[0] + "." + join[2] + " = " + join[1] + "." + join[3]

                join_index = join_index + 1 

        self.query = "SELECT " + \
            ", ".join([col[0] + "." + col[1] for col in self.select]) + " " + \
            " From " + \
            from_clause + \
            " Where " + \
            " and ".join([cond[0] + "." + cond[1] + " " + cond[2] + " " + cond[3] for cond in self.conditions])
            
            

    def find_select(self):
        for ecm in self.entity_column_mapping:
            # column mapping within entity
            for cm in ecm[1]:
                if cm.condition is None and cm.value_ is None:
                    # entity, column name, [Avg, Min, Max, Sum, Count]
                    self.select.append((ecm[0], cm.name.lower(), None))

        for ent in self.entities:
            # TODO... add max, min..etc case
            # get default column from db_model
            db_model_ent = next(e for e in self.db_model.entities if e.name.lower() == ent.name.lower())
            self.select.append((ent.name.lower(), db_model_ent.defaultColumn, None))

    def find_conditions(self):
        # entity column mapping
        for ecm in self.entity_column_mapping:
            # column mapping within entity
            for cm in ecm[1]:
                if cm.condition is not None and cm.value_ is not None:
                    val = cm.value_
                    if cm.type_ == "string":
                        val = "\"" + val + "\""
                    self.conditions.append((ecm[0], cm.name.lower(), cm.condition, str(val)))

    def find_relationships(self):
        i = 0
        j = 0
        while i < len(self.entity_column_mapping):
            j = i + 1
            base_entity = self.entity_column_mapping[i][0]
            while j < len(self.entity_column_mapping):
                join_entity = self.entity_column_mapping[j][0]
                if len([rel for rel in self.db_model.relationships if ((rel.entity1 == base_entity and rel.entity2 == join_entity) or (rel.entity2 == base_entity and rel.entity1 == join_entity))]) == 1:
                    rel = next(rel for rel in self.db_model.relationships if ((rel.entity1 == base_entity and rel.entity2 == join_entity) or (rel.entity2 == base_entity and rel.entity1 == join_entity)))

                    if rel.entity1 == base_entity:
                        self.joins.append((base_entity, join_entity, rel.column1, rel.column2))
                    else:
                        self.joins.append((join_entity, base_entity, rel.column1, rel.column2))
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
        self.find_conditions()
        self.find_select()
        self.build_query()


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
