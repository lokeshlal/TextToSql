def get_value(value, type):
    if type == "string":
        return str(value)
    elif type == "int":
        try:
            return int(value)
        except ValueError:
            return "NoValue"
    elif type == "float":
        try:
            return float(value)
        except ValueError:
            return "NoValue"
    return "NoValue"

def get_type(value, type):
    if type == "string":
        type = "str"
    if type(value).__name__ == type:
        return True
    else:
        return False

def replace_string(phrase, original, replacement):
    result = phrase.lower().find(original.lower())
    new_replacement = replacement
    if result != -1:
        if phrase[result].isupper():
            new_replacement = new_replacement[0].upper() + new_replacement[1:].lower()
        if phrase[result].islower():
            new_replacement = new_replacement.lower()
        string_to_replace = phrase[result:(result + len(original))]
        phrase = phrase.replace(string_to_replace, new_replacement)
    return phrase

def replace_entities(phrase, original, replacement):
    result = phrase.lower().find(original.lower())
    if result != -1:
        string_to_replace = phrase[result:(result + len(original))]
        phrase = phrase.replace(string_to_replace, replacement)
    return phrase


def get_token_child_len(token):
    children_length = len([child.text for child in token.children])
    return children_length

def get_neighbour_tokens(token):
    span = ""
    for i in range(-4, 6):
        try:
            span += token.nbor(i).text + " "
        except IndexError:
            span = span
    
    return span.lstrip()
    