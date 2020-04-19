import json
import os


class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Configuration(metaclass=Singleton):
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'config.json')) as json_configuration:
            self.data = json.load(json_configuration)

    # sql starts
    def get_sql_connection_string(self):
        return self.data["sql"]["connection_string"]

    def get_tables_sql_query(self):
        with open(os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'models', 'sql_scripts', 'tables.sql'))) as query:
            return query.read()

    def get_columns_sql_query(self):
        with open(os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'models', 'sql_scripts', 'columns.sql'))) as query:
            return query.read()

    def get_FK_sql_query(self):
        with open(os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'models', 'sql_scripts', 'foreign_keys.sql'))) as query:
            return query.read()

    def get_PK_sql_query(self):
        with open(os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'models', 'sql_scripts', 'primary_keys.sql'))) as query:
            return query.read()

    def get_synonyms(self):
        return self.data["synonyms"]

    def get_phrase_splitter(self):
        return self.data["phrase_splitter"]

    def get_entitites_to_load(self):
        return self.data["entities_to_load"]

    # sql ends

    def get_default_column(self, table_name):
        return self.data["default_columns"]["entities"][table_name]
