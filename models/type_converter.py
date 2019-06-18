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
    