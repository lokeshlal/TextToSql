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

### How to make this library works
Important part to focus here is configuration

### What all this library supports as of now


### References


### Connect

