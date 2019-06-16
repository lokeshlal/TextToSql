# TextToSql
An attempt to convert natural language to sql statement


## Approach
```
Input text -> 
    Input string processing using spacy
    Remove stop words
    Lemmatization
    Mactch entities and columns using MatchPhraser
    Split the Lemmatized sentence to contextual phrases using splitters such as and, in
    Find the entity/column-value-operation relationship within each phrase
    Buid the dictionary and pass the dictionary to SQL Generator ->
        Push the query to database and fetch the result
```

### How to make this library works


### What all this library supports as of now


### References


### Connect

