import json
import unidecode

def parse_json_from_file(filename):

    # Ler o arquivo de conversacao
    conversation_file = open(filename, "r")
    json_contents = json.load(conversation_file)

    return json_contents


def format_input(text) -> int:
    # Formatar o texto do usuario para lower case e sem acentos
    return unidecode.unidecode(text.lower())
