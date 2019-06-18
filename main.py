# import libraries
import spacy
import itertools
import re
from spacy import displacy
from spacy.matcher import PhraseMatcher
from models.columns import Columns
from models.entities import Entities
from models.db_model import DBModel
from models.type_converter import get_value, get_token_child_len, get_neighbour_tokens
from models.sql_model import SQLGenerator
from models.matcher import Matcher

# load the DB Model
db_model = DBModel()

# remove unneccesary words
stan_stop_words = [line.rstrip('\n') for line in open("stopwords.txt")]

# load spacy's english model
nlp = spacy.load('en_core_web_sm')

# exceptions
exceptions = ["between", "more", "than"]
lemma_exceptions = ["greater", "less", "than", "more"]

# creating phrase matcher to get the entities and columns
# build this using above entities and columns list
# also add option to get the synonyms in declarative way
custom_matcher = Matcher()
custom_matcher = db_model.get_custom_matcher(custom_matcher, nlp)
# test sentence
# sentence = u'Show all students whose marks greater than 30'
# sentence = u'students in class 12 and mark 30 in english subject'
# sentence = u'students in class 12 and marks less than 50 in english subject in year greater than 2018'
# sentence = u'students in class 12 and marks less than 30 in english subject'
# sentence = u'average marks of students in english subject in class 12'
sentence = u'average marks in english subject in class 12'
# sentence = u'student with maximum marks in english subject in class 12'
# sentence = u'minimum marks in english subject in class 12'
# sentence = u'total marks of students in class 12 in year 2019'
# sentence = u'students in class 12 with 50 marks in english subject'
# sentence = u'students in class 12 and mark in english subject is 30'
# sentence = u'students in class 12 and marks less than 30 in english subject'

# basic string replacements for count and sum
sentence = sentence.replace("total number", "count")
sentence = sentence.replace("total", "sum")

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

# for chunk in docLemmatized.noun_chunks:
#     print(chunk.text, chunk.root.text, chunk.root.dep_,
#             chunk.root.head.text)

# get all tables and columns in the question
# matches = matcher(docLemmatized)
matches = custom_matcher.find(lemmatizedSentence)
matched_entities = []
matched_columns = []
for match in matches:
    if match[0].endswith("TABLE"):
        matched_entities.append(Entities(match[0].replace("_TABLE","")))
    if match[0].endswith("COLUMN"):
        columnType = [c.type_ for c in db_model.columns if c.name == match[0].replace("_COLUMN","").lower()]
        if len(columnType) > 0:
            columnType = columnType[0]
        matched_columns.append(Columns(match[0].replace("_COLUMN",""), columnType))

# print("####################")
# print(lemmatizedSentence)
# print([(m[0], m[1]) for m in custom_matcher.matcher])
# print([(m[0], m[1]) for m in matches])
# print([m.name for m in matched_entities])
# print([m.name for m in matched_columns])
# print("####################")

# get values for the captured columns in the above use case
for token in docLemmatized:

    # check of token matches any of the matched entities
    if token.text.upper() in [m.name for m in matched_entities]:
        matched_entity = next(me for me in matched_entities if me.name == token.text.upper())

        contextual_span = get_neighbour_tokens(token)
        span_ranges = re.split(" in |in | in| and |and | and| with |with | with", contextual_span)
        
        for span in span_ranges:
            # print("entity : ", span)
            if matched_entity.name.lower() in span:
                matched_entity.condition = "="
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
                    matched_entity.isSum = True
                if "total" in span:
                    matched_entity.isSum = True

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
                    if span_token.text.lower() == matched_entity.name.lower():
                        if get_token_child_len(span_token) > 0:
                            span_token_child = next(itertools.islice(span_token.children, 1))
                            ent = next(en for en in db_model.entities if en.name.lower() == matched_entity.name.lower())
                            default_column = next(col for col in ent.columns if col.name.lower() == ent.defaultColumn.lower())
                            matched_entity.value_ = get_value(span_token_child.text, default_column.type_)

                
        matched_entities = [me for me in matched_entities if me.name != token.text.upper()]
        matched_entities.append(matched_entity)
    

    # check of token matches any of the matched column
    if token.text.upper() in [m.name for m in matched_columns]:
        matched_column = next(mc for mc in matched_columns if mc.name == token.text.upper())

        contextual_span = get_neighbour_tokens(token)
        span_ranges = re.split(" in |in | in| and |and | and| with |with | with", contextual_span)
        for span in span_ranges:
            # print("column : ", span)
            if matched_column.name.lower() in span:
                matched_column.condition = "="
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
                    matched_column.isSum = True
                if "total" in span:
                    matched_column.isSum = True
                
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

        matched_columns = [mc for mc in matched_columns if mc.name != token.text.upper()]
        matched_columns.append(matched_column)
                         
# final representation of columns (matched_columns) and entities (matched_entities), including max, min, average, conditions
# now next is to build the SQL query generator
# matched entities
# print("####################")
# print("\n".join([(mc.name + " -- " + str(mc.value_) + " -- " + " condition : " + str(mc.condition) + " -- " + " isMax : " + str(mc.isMax) + " -- " + " isMin : " + str(mc.isMin) + " -- " + " isAverage : " + str(mc.isAverage)) for mc in matched_entities]))
# print("####################")
# # matched columns
# print("\n".join([(mc.name + " -- " + str(mc.value_) + " -- " + " condition : " + str(mc.condition) + " -- " + " isMax : " + str(mc.isMax) + " -- " + " isMin : " + str(mc.isMin) + " -- " + " isAverage : " + str(mc.isAverage)) for mc in matched_columns]))
# print("####################")

sql_generator = SQLGenerator(matched_entities, matched_columns, db_model)
result = sql_generator.get_sql()

print(sql_generator.query)
print(result)