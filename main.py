# import libraries
import spacy
import itertools
import re
from spacy.matcher import PhraseMatcher
from extract_relationshion import extract_currency_relations
from models.columns import Columns
from models.entities import Entities
from models.db_model import DBModel
from models.type_converter import get_value, get_token_child_len, get_neighbour_tokens
from models.sql_model import SQLGenerator

# load the DB Model
db_model = DBModel()

# remove unneccesary words
stan_stop_words = [line.rstrip('\n') for line in open("stopwords.txt")]

# load spacy's english model
nlp = spacy.load('en_core_web_sm')

# exceptions
exceptions = ["between", "more", "than"]
lemma_exceptions = ["greater", "than", "more"]

# creating phrase matcher to get the entities and columns
# build this using above entities and columns list
# also add option to get the synonyms in declarative way
matcher = PhraseMatcher(nlp.vocab)
matcher = db_model.get_matcher(matcher, nlp);

# test sentence
# sentence = u'Show all students whose marks greater than 30'
# sentence = u'students in class 10 and mark 30 in english subject'
sentence = u'students in class 10 and marks less than 30 in english subject in year greater than 2018'
# sentence = u'students in class 10 and marks less than 30 in english subject'
# sentence = u'student with maximum marks in english subject in class 10'
# sentence = u'students in class 10 with 30 marks in english subject'
# sentence = u'students in class 10 and mark in english subject is 30'
# sentence = u'students in class 10 and marks less than 30 in english subject'
# sentence = u'city with employee with maximum average salary'
# sentence = u'city with maximum employees with experience more than 10 years'

# remove the stop words
new_sentence = ""
for word in sentence.split():
    if word not in stan_stop_words:
        new_sentence += word + " "
sentence = new_sentence.lstrip()

# run nlp on sentence
doc = nlp(sentence)

# build the lemma sentence
lemmatizedSentence = ''
for token in doc:
    lemmatizedSentence = lemmatizedSentence + (token.text if token.text in lemma_exceptions else token.lemma_) + " "
lemmatizedSentence = lemmatizedSentence.lstrip()

# stop word removal
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
docLemmatized = nlp(lemmatizedSentence)

# get all tables and columns in the question
matches = matcher(docLemmatized)
matched_entities = []
matched_columns = []
for match_id, start, end in matches:
    rule_id = nlp.vocab.strings[match_id]
    span = docLemmatized[start : end]
    if rule_id.endswith("TABLE"):
        matched_entities.append(Entities(rule_id.replace("_TABLE","")))
    if rule_id.endswith("COLUMN"):
        columnType = [c.type_ for c in db_model.columns if c.name == rule_id.replace("_COLUMN","").lower()]
        if len(columnType) > 0:
            columnType = columnType[0]
        matched_columns.append(Columns(rule_id.replace("_COLUMN",""), columnType))

# get values for the captured columns in the above use case
for token in docLemmatized:

    # check of token matches any of the matched entities
    if token.text.upper() in [m.name for m in matched_entities]:
        matched_entity = next(me for me in matched_entities if me.name == token.text.upper())

        contextual_span = get_neighbour_tokens(token)
        span_ranges = re.split(" in |in | in| and |and | and", contextual_span)
        
        for span in span_ranges:
            if matched_entity.name.lower() in span:
                if "average" in span:
                    matched_entity.isAverage = True
                if "avg" in span:
                    matched_entity.isAverage = True
                if "maximum" in span:
                    matched_entity.isMax = True
                if "max" in span:
                    matched_entity.isMax = True
                if "minimum" in span:
                    matched_entity.isMin = True
                if "min" in span:
                    matched_entity.isMin = True
                if "count" in span:
                    matched_entity.isCount = True
                if "sum" in span:
                    matched_entity.isCount = True
        
    

    # check of token matches any of the matched column
    if token.text.upper() in [m.name for m in matched_columns]:
        matched_column = next(mc for mc in matched_columns if mc.name == token.text.upper())

        contextual_span = get_neighbour_tokens(token)
        span_ranges = re.split(" in |in | in| and |and | and", contextual_span)
        for span in span_ranges:
            matched_column.condition = "="
            if matched_column.name.lower() in span:
                if "average" in span:
                    matched_column.isAverage = True
                if "avg" in span:
                    matched_column.isAverage = True
                if "maximum" in span:
                    matched_column.isMax = True
                if "max" in span:
                    matched_column.isMax = True
                if "minimum" in span:
                    matched_column.isMin = True
                if "min" in span:
                    matched_column.isMin = True
                if "greater than" in span:
                    matched_column.condition = ">"
                if "more than" in span:
                    matched_column.condition = ">"
                if "less than" in span:
                    matched_column.condition = "<"
                if "count" in span:
                    matched_column.isCount = True
                if "sum" in span:
                    matched_column.isCount = True
                
                trimmed_span = span \
                    .replace("average", "") \
                    .replace("maximum", "") \
                    .replace("minimum", "") \
                    .replace("greater than", "") \
                    .replace("less than", "") \
                    .replace("more than", "") \
                    .replace("min", "") \
                    .replace("max", "")
                trimmed_span = ' '.join(trimmed_span.split())
                
                doc_span = nlp(trimmed_span)
                
                for span_token in doc_span:
                    if span_token.text.lower() == matched_column.name.lower():
                        if get_token_child_len(span_token) > 0:
                            span_token_child = next(itertools.islice(span_token.children, 1))
                            matched_column.value_ = get_value(span_token_child.text, matched_column.type_)
                         
# final representation of columns (matched_columns) and entities (matched_entities), including max, min, average, conditions
# now next is to build the SQL query generator
sql_generator = SQLGenerator(matched_entities, matched_columns, db_model)
sql_generator.get_sql()
# print(*[(ecm[0], [(ecm_child.name, ecm_child.type_, ecm_child.value_, ecm_child.condition) for ecm_child in ecm[1]]) for ecm in sql_generator.entity_column_mapping], sep="\n")

print(sql_generator.query)