import Storage
from Logger import logger
import random
import re

title_matcher = re.compile("^([^=]+)(=.*)$")
main_definition_searcher = re.compile("===([^=]+)===[^#]*# ([^\n]*)", re.DOTALL)
escaped_new_line = re.compile("\\\\n")
undesired_sections = re.compile("====?(?:Conjugation|Declension|Derived terms|Pronunciation)====?[^=]*", re.DOTALL)
quiz_grammatical_classes = re.compile("Adjective|Noun|Verb")
hashtag_search = re.compile("#")
curly_link_search = re.compile(r"\{\{[^}]*[|=]([^|}=]+)\}\}")
square_link_search_1 = re.compile(r"\[\[[^|]*\|([^|\]]*)\]\]")
square_link_search_2 = re.compile(r"\[\[([^|\]]*)\]\]")
h3_search = re.compile(r"===([^=]+)===")
h4_search = re.compile(r"====([^=]+)====")
reserved_characters_search = re.compile(r"([+-.|!()=#*{}\[\]])")

def _parse(line: str) -> tuple:
    title_match = title_matcher.match(line).groups()
    title = title_match[0]
    definition = title_match[1]
    definition = escaped_new_line.sub("\n", definition)
    definition = undesired_sections.sub("", definition)
    definition = curly_link_search.sub(r"(_\1_)", definition)
    definition = square_link_search_1.sub(r"\1", definition)    
    definition = square_link_search_2.sub(r"\1", definition)
    main_definition = main_definition_searcher.search(definition)
    if main_definition:
        grammatical_class = main_definition.groups()[0]
        main_definition = main_definition.groups()[1]
        main_definition = reserved_characters_search.sub(r"\\\1", main_definition)
    definition = hashtag_search.sub("*", definition)
    definition = h4_search.sub(r"### \1", definition)
    definition = h3_search.sub(r"## \1", definition)
    definition = reserved_characters_search.sub(r"\\\1", definition)
    return (title, definition, grammatical_class, main_definition)

def get(language: str, subscription: dict) -> str:
    with open(f"/tmp/{language}", "r") as file_obj:
        line_count = 0
        line = file_obj.readline()
        while line:
            if line_count == subscription["publication_count"]:
                (title, definition, grammatical_class, main_definition) = _parse(line)
                return f"{title} \\({grammatical_class}\\) {main_definition}\n\n{definition}"
            line_count += 1
            line = file_obj.readline()
    return None

def get_quiz(language: str, subscription: dict) -> list:
    max_index = max(subscription["publication_count"], 15000)
    random_index = random.randint(0, max_index)
    logger.info(f"random_index {random_index}")
    result = []
    grammatical_class = ""
    with open(f"/tmp/{language}", "r") as file_obj:
        line_count = 0
        line = file_obj.readline()
        while line:
            if line_count >= random_index:
                (title, _, grammatical_class_i, main_definition) = _parse(line)
                if main_definition:
                    if grammatical_class == "" \
                        and quiz_grammatical_classes.match(grammatical_class_i):
                        grammatical_class = grammatical_class_i
                    if grammatical_class == grammatical_class_i:
                        result.append((title, grammatical_class, main_definition))
                        random_index = line_count + random.randint(2, 10)
                        if len(result) == 3:
                            return result
            line_count += 1
            line = file_obj.readline()
    return None
