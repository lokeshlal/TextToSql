import copy 
import pyodbc

from configuration.config import Configuration
from models.columns import Columns


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
        self.isMaxRequired = ""
        self.isMaxRequiredEntity = ""
        self.isMinRequired = ""
        self.isMinRequiredEntity = ""
        self.isAverage = ""
        self.isAverageEntity = ""
        self.isCount = ""
        self.isCountEntity = ""
        self.isSum = ""
        self.isSumEntity = ""
        self.config = Configuration()
        self.conn = pyodbc.connect(self.config.get_sql_connection_string())

    def run_query(self):
        cursor = self.conn.cursor()
        cursor.execute(self.query)
        result = []
        columns = []
        for row in cursor:
            result.append([col for col in row])

        columns = [column[0] for column in cursor.description]
        return [result, columns]


    def sortSecond(self, join_comb): 
        return join_comb[0] 

    def get_from_clause(self, level):
        # build the from_clause
        from_clause = ""
        if len(self.entity_column_mapping) == 1:
            from_clause = self.entity_column_mapping[0][0] + " " + self.entity_column_mapping[0][0] + level
        elif len(self.entity_column_mapping) > 1:
            from_clause = ""
            join_index = 0
            entity_included_in_join = []
            for join in self.joins:
                if join_index == 0:
                    from_clause = from_clause + join[0] + " " + join[0] + level + " JOIN " + join[1] + " " + join[1] + level + " ON " + join[0] + level + "." + join[2] + "=" + join[1] + level + "." + join[3]
                    entity_included_in_join.append(join[0])
                    entity_included_in_join.append(join[1])
                else:
                    if join[0] in entity_included_in_join:
                        from_clause = from_clause + " " + " JOIN " + join[1] + " " + join[1] + level + " ON " + join[0]+ level + "." + join[2] + " = " + join[1] + level + "." + join[3]
                    else:
                        from_clause = from_clause + " JOIN " + join[0] + " " + join[0] + level + " ON " + join[0] + level + "." + join[2] + " = " + join[1] + level + "." + join[3]
                join_index = join_index + 1 
        return from_clause

    def get_where_clause(self, level):
        return " and ".join([cond[0] + level + "." + cond[1] + " " + cond[2] + " " + cond[3] for cond in self.conditions])

    def get_select_clause(self, level):
        return ", ".join([col[0] + level + "." + col[1] for col in self.select])

    def correlated_sub_query_in_where(self, 
        column,
        entity,
        type_): # type = min, max
        # from clause
        from_clause = self.get_from_clause("1")
        # select clause
        select_clause = self.get_select_clause("1")
        # where clause
        where_clause = self.get_where_clause("1")

        type_sub_query_where_clause = self.get_where_clause("2")
        type_sub_query_from_clause = self.get_from_clause("2")

        if type_sub_query_where_clause != "":
            type_sub_query_where_clause = " Where " + type_sub_query_where_clause

        typeQuery = "SELECT " + \
            type_ + "(" + entity + "2." + column + ") " + \
            " From " + \
            type_sub_query_from_clause + \
            type_sub_query_where_clause
        if select_clause != "":
            select_clause = select_clause + ", "
        if where_clause != "":
            where_clause = where_clause + " and "
        self.query = "SELECT " + \
            select_clause + entity + "1." + column + " " + \
            " From " + \
            from_clause + \
            " Where " + \
            where_clause + \
            entity + "1." + column + " = (" + typeQuery + ")"

    def correlated_sub_query_in_select(self, 
        column,
        entity,
        type_): # type = avg, sum, count
        # from clause
        from_clause = self.get_from_clause("1")
        # select clause
        select_clause = self.get_select_clause("1")
        # where clause
        where_clause = self.get_where_clause("1")

        type_sub_query_where_clause = self.get_where_clause("2")
        type_sub_query_from_clause = self.get_from_clause("2")

        # find the identifier column of the entity in parameter
        db_model_ent = next(e for e in self.db_model.entities if e.name.lower() == entity.lower())
        # db_model_ent.primaryKey
        # correlation

        # find where this table is being referenced
        entity_relationships = [(rel.entity1, rel.column1) for rel in self.db_model.relationships if (rel.entity2 == entity)]

        correlation_entity = entity
        correlation_entity_column = db_model_ent.primaryKey
        parent_entity_exists = False
        parent_entries = []
        if len(self.entity_column_mapping) > 1:
            for ecm in self.entity_column_mapping:
                if ecm[0] != entity:
                    if ecm[0] in [ent[0] for ent in entity_relationships]:
                        parent_entry = next(ent for ent in entity_relationships if ent[0] == ecm[0])
                        parent_entity_exists = True
                        parent_entries.append(parent_entry)
        elif len(self.entity_column_mapping) == 1:
            # only one entity, use where filters
            correlation = " and ".join([cond[0] + "1" + "." + cond[1] + " = " + cond[0] + "2" + "." + cond[1] for cond in self.conditions])
        
        if len(self.entity_column_mapping) > 1:              
            if parent_entity_exists == True and len(parent_entry) > 0:
                correlations = []
                for parent_entry in parent_entries:
                    correlations.append(parent_entry[0] + "2." + parent_entry[1] + "=" + parent_entry[0] + "1." + parent_entry[1])
                correlation = " and ".join(correlations)
            else:
                correlation = entity + "2." + db_model_ent.primaryKey + "=" + entity + "1." + db_model_ent.primaryKey
        
        if type_sub_query_where_clause == "":
            type_sub_query_where_clause = correlation
        else:
            type_sub_query_where_clause = type_sub_query_where_clause + " and " + correlation

        if type_sub_query_where_clause != "":
            type_sub_query_where_clause = " Where " + type_sub_query_where_clause

        type_sub_query = "SELECT " + \
            type_ + "(" + entity + "2." + column + ") " + \
            " From " + \
            type_sub_query_from_clause + \
            type_sub_query_where_clause

        if select_clause != "":
            select_clause = select_clause + ", "

        if where_clause != "":
            where_clause = " Where " + where_clause

        self.query = "SELECT distinct " + \
            select_clause + "(" + type_sub_query + ") as " + type_ + "_" + column + " " + \
            " From " + \
            from_clause + \
            where_clause


    def build_query(self):

        # maximum case
        if self.isMaxRequired != "":
            self.correlated_sub_query_in_where(self.isMaxRequired, self.isMaxRequiredEntity,"max")
        # minimum case
        elif self.isMinRequired != "":
            self.correlated_sub_query_in_where(self.isMinRequired, self.isMinRequiredEntity,"min")
        # average case
        elif self.isAverage != "":
            self.correlated_sub_query_in_select(self.isAverage, self.isAverageEntity, "avg")
        # count
        elif self.isCount != "":
            self.correlated_sub_query_in_select(self.isCount, self.isCountEntity, "count")
        # sum
        elif self.isSum != "":
            self.correlated_sub_query_in_select(self.isSum, self.isSumEntity, "sum")
        # regular
        else:
            # from clause
            from_clause = self.get_from_clause("1")
            # select clause
            select_clause = self.get_select_clause("1")
            # where clause
            where_clause = self.get_where_clause("1")

            if where_clause != "":
                where_clause = " Where " + where_clause
            self.query = "SELECT distinct " + \
                select_clause + " " + \
                " From " + \
                from_clause + \
                where_clause

    def find_select(self):
        for ecm in self.entity_column_mapping:
            # column mapping within entity
            for cm in ecm[1]:
                # if cm.condition is None and cm.value_ is None:
                if cm.value_ is None or cm.value_ == "NoValue":
                    # entity, column name, [Avg, Min, Max, Sum, Count]
                    # add the where clause here for min, max and sum conditions
                    if cm.isMax == True:
                        self.isMaxRequired = cm.name.lower()
                        self.isMaxRequiredEntity = ecm[0]
                    elif cm.isMin == True:
                        self.isMinRequired = cm.name.lower()
                        self.isMinRequiredEntity = ecm[0]
                    elif cm.isAverage == True:
                        self.isAverage = cm.name.lower()
                        self.isAverageEntity = ecm[0]
                    elif cm.isCount == True:
                        self.isCount = cm.name.lower()
                        self.isCountEntity = ecm[0]
                    elif cm.isSum == True:
                        self.isSum = cm.name.lower()
                        self.isSumEntity = ecm[0]
                    else:
                        # check for duplicates
                        if len([sel for sel in self.select if sel[0].lower() == ecm[0].lower() and sel[1].lower() == cm.name.lower()]) == 0:
                            self.select.append((ecm[0], cm.name.lower(), None))
                    


        for ent in self.entities:
            # TODO... add max, min..etc case
            # get default column from db_model
            db_model_ent = next(e for e in self.db_model.entities if e.name.lower() == ent.name.lower())
            # check for duplicates
            if len([sel for sel in self.select if sel[0].lower() == ent.name.lower() and sel[1].lower() == db_model_ent.defaultColumn.lower()]) == 0:
                self.select.append((ent.name.lower(), db_model_ent.defaultColumn, None))

    def find_conditions(self):
        # entity column mapping
        for ecm in self.entity_column_mapping:
            # column mapping within entity
            for cm in ecm[1]:
                if cm.condition is not None and cm.value_ is not None and cm.value_ != "NoValue":
                    val = cm.value_
                    if cm.type_ == "string":
                        val = "'" + val + "'"
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
        
        if len(self.joins) == 0 and len(self.entity_column_mapping) > 1:
            # try to find the relationship using db model's entity_graph
            i = 0
            entities_mapped = []
            while i < (len(self.entity_column_mapping) - 1):
                base_entity = self.entity_column_mapping[i]
                join_entity = self.entity_column_mapping[i + 1]
                if base_entity[0] not in entities_mapped:
                    entities_mapped.append(entities_mapped)
                found, entities_mapped = self.find_entities_relationship(base_entity, join_entity, entities_mapped)
                i = i + 1

            i = 0
            j = 0
            while i < len(entities_mapped):
                j = i + 1
                base_entity = entities_mapped[i]
                while j < len(entities_mapped):
                    join_entity = entities_mapped[j]
                    if len([rel for rel in self.db_model.relationships if ((rel.entity1 == base_entity and rel.entity2 == join_entity) or (rel.entity2 == base_entity and rel.entity1 == join_entity))]) == 1:
                        rel = next(rel for rel in self.db_model.relationships if ((rel.entity1 == base_entity and rel.entity2 == join_entity) or (rel.entity2 == base_entity and rel.entity1 == join_entity)))

                        if rel.entity1 == base_entity:
                            self.joins.append((base_entity, join_entity, rel.column1, rel.column2))
                        else:
                            self.joins.append((join_entity, base_entity, rel.column1, rel.column2))
                    j = j + 1
                i = i + 1

    def find_entities_relationship(self, base_entity, join_entity, entities_mapped):
        
        entities_to_be_included = copy.copy(entities_mapped)
        found = False
        base_entity_graph = next(eg for eg in self.db_model.entity_graph if eg[0].lower() == base_entity[0].lower())
        for child_entity_in_graph in base_entity_graph[1]:
            if child_entity_in_graph == join_entity[0]:
                entities_to_be_included.append(child_entity_in_graph)
                found = True
                break;
            child_entity_graph = next(eg for eg in self.db_model.entity_graph if eg[0].lower() == child_entity_in_graph.lower())
            entities_to_be_included_temp = copy.copy(entities_to_be_included)
            if child_entity_in_graph not in entities_to_be_included_temp:
                entities_to_be_included_temp.append(child_entity_in_graph)
                found, entities_to_be_included = self.find_entities_relationship(child_entity_graph, join_entity, entities_to_be_included_temp)
            if found:
                break;
            
        if found:
            for entity_to_be_included in entities_to_be_included:
                if entity_to_be_included not in entities_mapped:
                    entities_mapped.append(entity_to_be_included)
        
        return (found, entities_to_be_included)


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


    def get_sql(self):
        if len(self.entities) > 0:
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
            
            for entity in self.entities:
                if entity.condition is not None and entity.value_ is not None:
                    # reset the entities_parsed array for new column
                    model_name = entity.name

                    ent = next(en for en in self.db_model.entities if en.name.lower() == entity.name.lower())
                    default_column = next(col for col in ent.columns if col.name.lower() == ent.defaultColumn.lower())
                    copy_default_column = copy.copy(default_column)  
                    copy_default_column.condition = entity.condition
                    copy_default_column.value_ = entity.value_                    
                    copy_default_column.isSum = entity.isSum                    
                    copy_default_column.isAverage = entity.isAverage                    
                    copy_default_column.isCount = entity.isCount                    
                    copy_default_column.isMin = entity.isMin                    
                    copy_default_column.isMax = entity.isMax                    

                    if len([ecm for ecm in self.entity_column_mapping if ecm[0].lower() == model_name.lower()]) == 1:
                        ecm = next(ecm for ecm in self.entity_column_mapping if ecm[0].lower() == model_name.lower())
                        ecm[1].append(copy_default_column)
                    else:
                        self.entity_column_mapping.append((model_name.lower(), [copy_default_column]))
                else:
                    if len([ecm for ecm in self.entity_column_mapping if ecm[0].lower() == entity.name.lower()]) == 0:
                        self.entity_column_mapping.append((entity.name.lower(), []))
                    else:
                        ecm = next(ecm for ecm in self.entity_column_mapping if ecm[0].lower() == entity.name.lower())

                        ent = next(en for en in self.db_model.entities if en.name.lower() == entity.name.lower())
                        default_column = next(col for col in ent.columns if col.name.lower() == ent.defaultColumn.lower())
                        copy_default_column = copy.copy(default_column)  
                        copy_default_column.condition = entity.condition
                        copy_default_column.value_ = entity.value_                    
                        copy_default_column.isSum = entity.isSum                    
                        copy_default_column.isAverage = entity.isAverage                    
                        copy_default_column.isCount = entity.isCount                    
                        copy_default_column.isMin = entity.isMin                    
                        copy_default_column.isMax = entity.isMax 
                        ecm[1].append(copy_default_column)                   
                        
        elif len(self.columns) > 0:
            # No entities identified in the phrase
            # Finding...entities as per the columns identified in the phrase
            for col in self.columns:
                max_col_found_count = 0
                max_col_found_count_entity = ""
                # look for columns and find max column in an entity and related entities"
                for entity in self.db_model.entities:
                    column_found_count = 0
                    if col.name.lower() in [col.name.lower() for col in entity.columns]:
                        column_found_count = column_found_count + 1
                if max_col_found_count <  column_found_count:
                    max_col_found_count = column_found_count
                    max_col_found_count_entity = entity.name

                if max_col_found_count_entity != "":
                    if len([ecm for ecm in self.entity_column_mapping if ecm[0] == max_col_found_count_entity]) == 1:
                        ecm = next(ecm for ecm in self.entity_column_mapping if ecm[0] == max_col_found_count_entity)
                        ecm[1].append(col)
                    else:
                        self.entity_column_mapping.append((max_col_found_count_entity, [col]))
        else:
            # no column and entity identified
            return []

        # print([(e[0], [ec.name for ec in e[1]]) for e in self.entity_column_mapping])
        # build the sql
        self.find_relationships()
        self.find_conditions()
        self.find_select()
        self.build_query()
        print(self.query)
        return self.run_query()

