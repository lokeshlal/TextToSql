# TextToSql
An attempt to convert natural language to sql statement


### Approach
```
Input text -> Text processing will entirely depends upon the targeted domain or customer 
    Replace key words, such as total number with count or total with sum etc. 
    Remove stop words
    Identify the text from pre-loaded entites
    Input string processing using spacy
        Identify noun chunks
        Identify named entities
    Create lemmatized string
    Match the processed sentence with the existing columns and tables as well as synonyms defined in the configuration
    Split the processed string using phrase splitter configuration (this again has to be domain specific)
        Create spacy nlp documents for the splitted phrases
        Find entities and columns
        Find if any aggregation requires to be run on the entities and columns
        Use Named entities identified earlier to correct the values
    Buid the dictionary and pass the dictionary to SQL Generator
    SQL generator (as of now is for SQL server only) will generate the query based on the entity-column dictionary
    Push the query to database and fetch the result
```

### Configuration
Important part to focus here is configuration

```
{
    "sql": {
        "connection_string":""
    },
    "phrase_splitter": " in |in | in| and |and | and| with |with | with",
    "default_columns": {
        "entities": {
            "student":"name",
            "subject":"name",
            "student_mark":"id"
        }
    },
    "entities_to_load": [
        {
            "entity": "subject",
            "column": "name" 
        },
        {
            "entity": "student",
            "column": "name" 
        }
    ],
    "synonyms": {
        "column": [
            {
                "original": "class",
                "synonyms": [ "standard" ]
            }
        ],
        "table": [
            {
                "original": "student",
                "synonyms": [ "children", "child" ]
            }
        ]
    }
}
```
**connection_string**: connection string for the sql server
**phrase_splitter**: phrase splitter for the domain. Customer should know what sort of queries user generally ask and how these can be splitted
**default_columns**: define default columns for the tables. this will be helpful to identify the default column to select when entity is mentioned in the question
**entities_to_load**: which all entities to pre-load. These entities should refer to the master data or data which needs to be looked up without any context
**synonyms**: synonyms for table names and column names

### What all is supported as of now
Following SQL functions - min, max, avg, sum, count

### How to run

```
python -B maini.py
```

Go to browser and launch http://127.0.0.1:5000/
