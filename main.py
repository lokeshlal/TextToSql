# import libraries
import spacy
import itertools
import re
import flask
import json

from spacy import displacy
from spacy.matcher import PhraseMatcher
from models.columns import Columns
from models.entities import Entities
from models.db_model import DBModel
from models.type_converter import get_value, get_token_child_len, get_neighbour_tokens, get_type, replace_string, replace_entities
from models.sql_model import SQLGenerator
from models.matcher import Matcher
from configuration.config import Configuration

#load the configuration
config = Configuration()
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
# sentence = u'Show all students with marks greater than 30'
# sentence = u'students in class 12 and mark 30 in english subject'
# sentence = u'students in class 12 and marks less than 50 in english subject in year greater than 2018'
# sentence = u'students in class 12 and marks less than 50 in english subject'
# sentence = u'average marks of students in english subject in class 12'
# sentence = u'average marks in english subject in class 12'
# sentence = u'student with maximum marks in english subject in class 12'
# sentence = u'minimum marks in english subject in class 12'
# sentence = u'total marks of students in class 12 in year 2019'
# sentence = u'students in class 12 with marks less than 60 in english subject'
# sentence = u'total marks in class 12 in year 2019'
# sentence = u'maximum marks in class 12 in year 2019'
# sentence = u'students in class 12 and 69 marks in english subject'
# sentence = u'students in class 12 and marks less than 50 in english subject'
# sentence = u'marks of Manoj Garg student in english subject'

# main method to process the incoming sentence
def process_sentence(sentence):

    # basic string replacements for count and sum
    sentence = sentence.replace("total number", "count")
    sentence = sentence.replace("total", "sum")

    # remove the stop words
    new_sentence = ""
    for word in sentence.split():
        if word not in stan_stop_words:
            new_sentence += word + " "
    sentence = new_sentence.lstrip()

    for loaded_entity in db_model.loaded_entities:
        for loaded_entity_value in loaded_entity[1]:
            if loaded_entity_value.lower() in sentence:
                sentence = replace_entities(sentence, loaded_entity_value, loaded_entity_value)

    # run nlp on sentence
    doc = nlp(sentence)

    identified_spans = []
    identified_entities = []

    for chunk in doc.noun_chunks:
        identified_spans.append(chunk.text)
        # print(chunk.text, " -- ", chunk.root.text, " -- ", chunk.root.dep_, " -- ", chunk.root.head.text)
    for ent in doc.ents:
        identified_entities.append(ent.text)
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)

    # build the lemma sentence
    lemmatizedSentence = ''
    for token in doc:
        lemmatizedSentence = lemmatizedSentence + (token.text if token.text in lemma_exceptions else token.lemma_) + " "
    lemmatizedSentence = lemmatizedSentence.lstrip()

    # stop word removal
    spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS

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
            lemmatizedSentence = replace_string(lemmatizedSentence, str(match[1]), match[0].replace("_TABLE",""))
        if match[0].endswith("COLUMN"):
            columnType = [c.type_ for c in db_model.columns if c.name == match[0].replace("_COLUMN","").lower()]
            if len(columnType) > 0:
                columnType = columnType[0]
            matched_columns.append(Columns(match[0].replace("_COLUMN",""), columnType))
            lemmatizedSentence = replace_string(lemmatizedSentence, str(match[1]), match[0].replace("_COLUMN",""))

    docLemmatized = nlp(lemmatizedSentence)

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
            span_ranges = re.split(config.get_phrase_splitter(), contextual_span)
            for span in span_ranges:
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
                        .replace("max", "") \
                        .replace("count", "") \
                        .replace("sum", "")
                    trimmed_span = ' '.join(trimmed_span.split())
                    doc_span = nlp(trimmed_span)

                    for span_token in doc_span:

                        if span_token.text.lower() == matched_entity.name.lower():

                            if get_token_child_len(span_token) > 0:
                                span_token_child = next(itertools.islice(span_token.children, 1))
                                ent = next(en for en in db_model.entities if en.name.lower() == matched_entity.name.lower())
                                default_column = next(col for col in ent.columns if col.name.lower() == ent.defaultColumn.lower())
                                value = get_value(span_token_child.text, default_column.type_)

                                identified_entity_exists = False
                                for identified_entity in identified_entities:
                                    if identified_entity in trimmed_span and str(value) in identified_entity:
                                        identified_entity_exists = True
                                        value = identified_entity
                                matched_entity.value_ = value


                    
            matched_entities = [me for me in matched_entities if me.name != token.text.upper()]
            matched_entities.append(matched_entity)
        

        # check of token matches any of the matched column
        if token.text.upper() in [m.name for m in matched_columns]:
            matched_column = next(mc for mc in matched_columns if mc.name == token.text.upper())

            contextual_span = get_neighbour_tokens(token)
            span_ranges = re.split(config.get_phrase_splitter(), contextual_span)
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
                        .replace("max", "") \
                        .replace("count", "") \
                        .replace("sum", "")
                    trimmed_span = ' '.join(trimmed_span.split())
                    
                    doc_span = nlp(trimmed_span)

                    for span_token in doc_span:
                        if span_token.text.lower() == matched_column.name.lower():
                            if get_token_child_len(span_token) > 0:
                                span_token_child = next(itertools.islice(span_token.children, 1))
                                value = get_value(span_token_child.text, matched_column.type_)

                                identified_entity_exists = False
                                for identified_entity in identified_entities:
                                    if identified_entity in trimmed_span and str(value) in identified_entity and get_value(identified_entity, matched_column.type_) != "NoValue":
                                        identified_entity_exists = True
                                        value = identified_entity
                                matched_column.value_ = value
                                

            matched_columns = [mc for mc in matched_columns if mc.name != token.text.upper()]
            matched_columns.append(matched_column)

    for loaded_entity in db_model.loaded_entities:
        entity_name = loaded_entity[0]
        for loaded_entity_value in loaded_entity[1]:
            if loaded_entity_value.lower() in lemmatizedSentence.lower():
                if entity_name.lower() in [me.name.lower() for me in matched_entities]:
                    # already exists
                    # no In operator support as of now
                    print("entity already processed")
                else:
                    en_def_col = next(col for en in db_model.entities if en.name.lower() == entity_name.lower() for col in en.columns if col.name.lower() == en.defaultColumn.lower())
                    if get_value(loaded_entity_value, en_def_col.type_) != "NoValue":
                        ent = Entities(entity_name.upper())
                        ent.condition = "="
                        ent.value_ = get_value(loaded_entity_value, en_def_col.type_)
                        matched_entities.append(ent)

    # final representation of columns (matched_columns) and entities (matched_entities), including max, min, average, conditions
    # now next is to build the SQL query generator
    # matched entities
    # print("####################")
    # print("\n".join([(mc.name + " -- " + str(mc.value_) + " -- " + " condition : " + str(mc.condition) + " -- " + " isMax : " + str(mc.isMax) + " -- " + " isMin : " + str(mc.isMin) + " -- " + " isAverage : " + str(mc.isAverage) + " -- " + " isSum : " + str(mc.isSum) + " -- " + " isCount : " + str(mc.isCount)) for mc in matched_entities]))
    # print("####################")
    # matched columns
    # print("\n".join([(mc.name + " -- " + str(mc.value_) + " -- " + " condition : " + str(mc.condition) + " -- " + " isMax : " + str(mc.isMax) + " -- " + " isMin : " + str(mc.isMin) + " -- " + " isAverage : " + str(mc.isAverage)) for mc in matched_columns]))
    # print("####################")

    sql_generator = SQLGenerator(matched_entities, matched_columns, db_model)
    print("=================================================================================")
    result = sql_generator.get_sql()
    # print(sql_generator.query)
    # print("=================================================================================")
    # print(result)
    # print("=================================================================================")
    response = {}
    response['sql'] = sql_generator.query
    response['result'] = result[0]
    response['columns'] = result[1]
    return response


app = flask.Flask(__name__)
@app.route('/request', methods=['POST'])
def home():
    content = flask.request.get_json()
    return flask.jsonify(process_sentence(content['sentence']))

@app.route('/')
def root():
    return flask.send_from_directory('','index.html') # serve root index.html

app.run()


